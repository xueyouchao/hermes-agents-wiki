"""Trading engine — the main loop connecting scanner → risk → exchange.

This is the orchestrator that:
1. Calls the scanner to find opportunities (Strategy B, A, C)
2. Passes each opportunity through the risk manager
3. Executes approved opportunities via the exchange client
4. Handles partial fills and order reconciliation
5. Auto-cancels orders when risk halt triggers
6. Logs all decisions for audit

Designed to be called by APScheduler at regular intervals, or manually
via CLI/API.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from backend.common.config import settings
from backend.common.risk import RiskManager, RiskLimits
from backend.common.exchange.base import ExchangeClient, OrderSide, OrderType, OrderResult
from backend.common.exchange.kalshi import KalshiExchange
from backend.common.alerting import alert_partial_fill, alert_execution_failure
from backend.weather.scanner.opportunity import (
    BracketMarket,
    Opportunity,
    OpportunityStatus,
    OpportunityType,
)
from backend.weather.scanner.opportunity_scanner import scan_all, scan_strategy_b

logger = logging.getLogger("trading_bot")

# Timeout for individual order placement (seconds)
ORDER_TIMEOUT_SECONDS = 10

# How long to wait after placing LIMIT orders before checking fill status
# GTC LIMIT orders need time to match — this pause lets the exchange fill them
FILL_WAIT_SECONDS = 3.0

# How many times to poll order status after the initial wait
FILL_POLL_ATTEMPTS = 2

# Seconds between poll attempts
FILL_POLL_INTERVAL = 2.0


class TradingEngine:
    """Orchestrates the full scan → approve → execute cycle.

    Usage:
        engine = TradingEngine()
        results = await engine.run_cycle()

    In SIMULATION_MODE, all decisions are logged but no orders are placed.
    """

    def __init__(
        self,
        exchange: Optional[ExchangeClient] = None,
        risk_manager: Optional[RiskManager] = None,
        simulation_mode: Optional[bool] = None,
    ):
        self.exchange = exchange or KalshiExchange()
        self.risk_manager = risk_manager or RiskManager(
            limits=RiskLimits(
                daily_loss_limit=settings.DAILY_LOSS_LIMIT,
                max_trade_size=settings.MAX_TRADE_SIZE,
                max_event_concentration=0.15,
                min_edge=0.02,
                fee_rate_per_contract=settings.KALSHI_FEE_RATE,
            )
        )
        self.simulation_mode = simulation_mode if simulation_mode is not None else settings.SIMULATION_MODE
        self._cycle_count = 0
        self._results: List[dict] = []

    async def run_cycle(self, strategies: Optional[List[str]] = None) -> List[dict]:
        """Run one complete scan → approve → execute cycle.

        Args:
            strategies: Which strategies to run. Defaults to all.
                Options: ["strategy_b", "strategy_a", "strategy_c"]

        Returns:
            List of cycle result dicts with opportunity + execution details
        """
        self._cycle_count += 1
        cycle_id = self._cycle_count
        cycle_start = datetime.now(timezone.utc)

        logger.info("=" * 60)
        logger.info(f"TRADING CYCLE #{cycle_id} START | sim={self.simulation_mode}")
        logger.info("=" * 60)

        # Step 0: Check if trading is allowed at all
        is_allowed, halt_reason = self.risk_manager.is_trading_allowed()
        if not is_allowed:
            logger.warning(f"Trading halted: {halt_reason}")
            # Auto-cancel any open orders when risk halt is active
            await self._auto_cancel_on_halt()
            return self._make_cycle_results(cycle_id, cycle_start, [])

        # Step 1: Scan for opportunities
        logger.info("Step 1: Scanning markets...")
        try:
            opportunities = await scan_all(self.exchange)
        except Exception as e:
            logger.error(f"Scan failed: {e}", exc_info=True)
            return self._make_cycle_results(cycle_id, cycle_start, [])

        if not opportunities:
            logger.info("No opportunities found. Cycle complete.")
            return self._make_cycle_results(cycle_id, cycle_start, [])

        logger.info(f"Found {len(opportunities)} opportunities")

        # Step 2: Fetch current positions for concentration check
        # If we can't verify current positions, we CANNOT safely trade —
        # we might be over-concentrated and not know it.
        current_positions: Dict[str, float] = {}
        positions_fetched = False
        try:
            positions = await self.exchange.get_positions()
            for pos in positions:
                current_positions[pos.ticker] = pos.size * pos.avg_price
            positions_fetched = True
        except Exception as e:
            logger.error(f"Could not fetch positions for concentration check: {e}")
            logger.error("Skipping this cycle — cannot verify concentration limits without position data")

        # Step 3: Risk check each opportunity
        # If positions failed, we cannot safely approve anything
        if not positions_fetched:
            logger.error("Aborting cycle — position data unavailable, concentration uncheckable")
            return self._make_cycle_results(cycle_id, cycle_start, [])

        logger.info("Step 2: Risk managing opportunities...")
        approved = []
        for opp in opportunities:
            is_allowed, adjusted_size, reason = self.risk_manager.approve_opportunity(
                opp, current_positions
            )
            if is_allowed:
                opp.suggested_size = adjusted_size
                opp.status = OpportunityStatus.VALIDATED
                approved.append(opp)
                logger.info(
                    f"  APPROVED: {opp.series_ticker} {opp.target_date} "
                    f"edge={opp.edge:.1%} size={adjusted_size} | {reason}"
                )
            else:
                opp.status = OpportunityStatus.CANCELLED
                logger.info(
                    f"  REJECTED: {opp.series_ticker} {opp.target_date} "
                    f"edge={opp.edge:.1%} | {reason}"
                )

        if not approved:
            logger.info("No opportunities approved after risk check.")
            return self._make_cycle_results(cycle_id, cycle_start, opportunities)

        # Step 4: Execute approved opportunities
        logger.info(f"Step 3: Executing {len(approved)} approved opportunities...")
        execution_results = []

        for opp in approved:
            # Re-check trading allowed before each execution
            is_allowed, reason = self.risk_manager.is_trading_allowed()
            if not is_allowed:
                logger.warning(f"Trading halted mid-cycle: {reason}")
                await self._auto_cancel_on_halt()
                break

            result = await self._execute_opportunity(opp)
            execution_results.append(result)

        # Step 5: Summary
        executed = sum(1 for r in execution_results if r.get("executed", False))
        simulated = sum(1 for r in execution_results if r.get("simulated", False))
        total_edge = sum(r.get("edge_dollars", 0) for r in execution_results)

        logger.info("-" * 60)
        logger.info(f"CYCLE #{cycle_id} COMPLETE")
        logger.info(f"  Opportunities found:  {len(opportunities)}")
        logger.info(f"  Approved by risk:     {len(approved)}")
        logger.info(f"  Executed (live):      {executed}")
        logger.info(f"  Simulated (paper):    {simulated}")
        logger.info(f"  Expected edge:        ${total_edge:.4f}")
        logger.info("=" * 60)

        return self._make_cycle_results(cycle_id, cycle_start, opportunities, execution_results)

    async def _auto_cancel_on_halt(self):
        """Auto-cancel all tracked orders when a risk halt is triggered."""
        order_ids = self.risk_manager.get_orders_to_cancel()
        if not order_ids:
            return

        logger.info(f"Auto-cancelling {len(order_ids)} tracked orders on risk halt...")
        cancelled = []
        for order_id in order_ids:
            try:
                success = await asyncio.wait_for(
                    self.exchange.cancel_order(order_id),
                    timeout=5.0,
                )
                if success:
                    cancelled.append(order_id)
                    logger.info(f"  Cancelled order {order_id}")
            except (asyncio.TimeoutError, Exception) as e:
                logger.error(f"  Failed to cancel order {order_id}: {e}")

        self.risk_manager.clear_cancelled_orders(cancelled)
        if cancelled:
            logger.info(f"Successfully cancelled {len(cancelled)}/{len(order_ids)} orders")

    async def _execute_opportunity(self, opp: Opportunity) -> dict:
        """Execute a single approved opportunity.

        For Strategy B (cross-bracket arb), we buy YES on every bracket.
        For other strategies, we buy YES or NO on a single market.
        """
        result = {
            "opportunity_type": opp.opportunity_type.value,
            "series_ticker": opp.series_ticker,
            "city_key": opp.city_key,
            "target_date": str(opp.target_date),
            "edge": opp.edge,
            "edge_dollars": opp.edge_dollars,
            "total_cost": opp.total_cost,
            "size": opp.suggested_size,
            "simulated": self.simulation_mode,
            "executed": False,
            "orders": [],
            "error": "",
        }

        if self.simulation_mode:
            result["simulated"] = True
            logger.info(
                f"  [SIM] Would execute {opp.opportunity_type.value}: "
                f"{opp.series_ticker} {opp.target_date} "
                f"edge={opp.edge:.1%} cost=${opp.total_cost:.4f} "
                f"ROI={opp.roi_pct:.1f}%"
            )

            # In simulation, still log what we would have done
            if opp.opportunity_type == OpportunityType.STRATEGY_B:
                for bracket in opp.brackets:
                    result["orders"].append({
                        "ticker": bracket.ticker,
                        "side": "yes",
                        "price": bracket.yes_price,
                        "size": opp.suggested_size,
                        "simulated": True,
                    })
                    logger.info(
                        f"    [SIM] BUY YES {bracket.ticker} @ {bracket.yes_price:.2f} "
                        f"x {opp.suggested_size}"
                    )
            else:
                # Strategy A or C — use explicit direction field
                result["orders"].append({
                    "ticker": opp.series_ticker,
                    "side": opp.direction,
                    "price": opp.total_cost,
                    "size": opp.suggested_size,
                    "simulated": True,
                })

            return result

        # Live execution
        try:
            if opp.opportunity_type == OpportunityType.STRATEGY_B:
                result = await self._execute_strategy_b(opp, result)
            else:
                result = await self._execute_single_market(opp, result)
        except Exception as e:
            result["error"] = str(e)
            alert_execution_failure(
                strategy=opp.opportunity_type.value,
                ticker=opp.series_ticker,
                error=str(e),
            )
            logger.error(f"  Execution failed for {opp.series_ticker}: {e}", exc_info=True)

        return result

    async def _execute_strategy_b(self, opp: Opportunity, result: dict) -> dict:
        """Execute Strategy B — two-phase commit for cross-bracket arbitrage.

        Phase 1: Place LIMIT (GTC) orders on ALL brackets concurrently.
        Phase 2: After a short wait, check fills.
          - If ALL brackets filled → arb complete, mark COMPLETE.
          - If any bracket unfilled → IMMEDIATELY cancel all unfilled orders
            and attempt to sell any filled positions at market (flatten).
            This converts partial arb exposure back to cash, avoiding directional risk.

        We NEVER leave partial fills unhedged. Either all brackets fill (arb) or
        we flatten and take the small loss on fills.
        """
        opp.status = OpportunityStatus.EXECUTING
        total_brackets = len(opp.brackets)

        # ── PHASE 1: Place all bracket orders as LIMIT (GTC) ──────────
        async def _place_bracket_order(bracket: BracketMarket) -> Tuple[BracketMarket, OrderResult]:
            """Place a single bracket LIMIT order with timeout."""
            try:
                order_result = await asyncio.wait_for(
                    self.exchange.place_order(
                        ticker=bracket.ticker,
                        side=OrderSide.YES,
                        price=bracket.yes_price,
                        size=opp.suggested_size,
                        order_type=OrderType.LIMIT,  # GTC, not IOC — we manage cancellations ourselves
                    ),
                    timeout=ORDER_TIMEOUT_SECONDS,
                )
                return bracket, order_result
            except asyncio.TimeoutError:
                return bracket, OrderResult(success=False, error="Order timed out")
            except Exception as e:
                return bracket, OrderResult(success=False, error=str(e))

        order_tasks = [_place_bracket_order(b) for b in opp.brackets]
        order_results = await asyncio.gather(*order_tasks)

        # Collect order IDs for Phase 2
        placed_orders: List[dict] = []  # {bracket, order_id, filled_size, filled_price, success}
        all_succeeded = True
        initial_filled_count = 0
        initial_cost = 0.0

        for bracket, order_result in order_results:
            order_dict = {
                "ticker": bracket.ticker,
                "side": "yes",
                "price": bracket.yes_price,
                "size": opp.suggested_size,
                "order_id": order_result.order_id,
                "filled_size": order_result.filled_size,
                "filled_price": order_result.filled_price,
                "simulated": False,
                "success": order_result.success,
                "error": order_result.error if not order_result.success else "",
            }
            result["orders"].append(order_dict)

            placed_orders.append({
                "bracket": bracket,
                "order_id": order_result.order_id,
                "filled_size": order_result.filled_size,
                "filled_price": order_result.filled_price,
                "success": order_result.success,
            })

            if order_result.success:
                initial_filled_count += 1
                initial_cost += order_result.filled_price * order_result.filled_size
                if order_result.order_id:
                    self.risk_manager.register_order_for_cancel(order_result.order_id)
            else:
                all_succeeded = False
                logger.error(f"  Order FAILED for {bracket.ticker}: {order_result.error}")

        # ── PHASE 1.5: Wait for LIMIT orders to fill ──────────
        # GTC LIMIT orders need time to match. We wait, then
        # poll each order's status before deciding whether to flatten.
        logger.info(f"  Phase 1 complete. Waiting {FILL_WAIT_SECONDS}s for LIMIT fills...")
        await asyncio.sleep(FILL_WAIT_SECONDS)

        # Poll order status to get updated fill information
        for poll_attempt in range(FILL_POLL_ATTEMPTS):
            rechecked_all_filled = True
            for o in placed_orders:
                if not o["success"] or o["filled_size"] >= opp.suggested_size:
                    continue  # Already failed or fully filled
                # Check order status via exchange
                try:
                    open_orders = await asyncio.wait_for(
                        self.exchange.get_open_orders(ticker=o["bracket"].ticker),
                        timeout=5.0,
                    )
                    # Find our order in the open orders list
                    our_order = None
                    for oo in open_orders:
                        if str(oo.get("id", "")) == str(o["order_id"]):
                            our_order = oo
                            break
                    if our_order is None:
                        # Order not in open list — it was either fully filled or cancelled
                        # Assume fully filled (best case for us)
                        o["filled_size"] = opp.suggested_size
                        o["filled_price"] = o["bracket"].yes_price
                        logger.info(f"  Poll: {o['bracket'].ticker} order filled (not in open orders)")
                    else:
                        filled_so_far = opp.suggested_size - float(our_order.get("remaining_count", opp.suggested_size))
                        if filled_so_far > o["filled_size"]:
                            o["filled_size"] = filled_so_far
                            logger.info(f"  Poll: {o['bracket'].ticker} partial fill: {filled_so_far}/{opp.suggested_size}")
                        if o["filled_size"] < opp.suggested_size:
                            rechecked_all_filled = False
                except Exception as e:
                    logger.warning(f"  Poll: Could not check order status for {o['bracket'].ticker}: {e}")
                    rechecked_all_filled = False

            if rechecked_all_filled:
                break
            elif poll_attempt < FILL_POLL_ATTEMPTS - 1:
                logger.info(f"  Poll attempt {poll_attempt + 1}: not all filled. Waiting {FILL_POLL_INTERVAL}s...")
                await asyncio.sleep(FILL_POLL_INTERVAL)

        # ── PHASE 2: Verify all brackets filled, flatten if not ──────────
        unfilled_orders = [o for o in placed_orders if o["success"] and o["filled_size"] < opp.suggested_size]
        completely_failed = [o for o in placed_orders if not o["success"]]
        all_filled = initial_filled_count == total_brackets and len(completely_failed) == 0 and len(unfilled_orders) == 0

        if all_filled:
            # All brackets filled — arb complete!
            opp.status = OpportunityStatus.COMPLETE
            result["executed"] = True

            # Record all trades in risk manager
            for o in placed_orders:
                if o["success"] and o["filled_size"] > 0:
                    self.risk_manager.record_trade(
                        ticker=o["bracket"].ticker,
                        size=int(o["filled_size"]),
                        cost=o["filled_price"] * o["filled_size"],
                    )

            logger.info(
                f"  Strategy B COMPLETE: {initial_filled_count}/{total_brackets} brackets filled, "
                f"total cost ${initial_cost:.4f}"
            )
            return result

        # PARTIAL FILL — dangerous! Flatten positions immediately.
        alert_partial_fill(
            brackets_filled=initial_filled_count,
            brackets_total=total_brackets,
            tickers=[o["bracket"].ticker for o in placed_orders if o["success"]],
        )
        logger.critical(
            f"  !!! Strategy B PARTIAL FILL: {initial_filled_count}/{total_brackets} filled, "
            f"{len(completely_failed)} failed, {len(unfilled_orders)} partial. "
            f"FLATTENING ALL POSITIONS."
        )

        # Cancel any unfilled/partially-filled orders
        cancel_tasks = []
        for o in placed_orders:
            if o["order_id"] and o["success"]:
                # Cancel any remaining open portion
                cancel_tasks.append(self._safe_cancel_order(o["order_id"]))

        if cancel_tasks:
            await asyncio.gather(*cancel_tasks)

        # Attempt to sell filled positions back at market (flatten)
        # If we bought YES on N brackets but not all, we have directional risk.
        # Best we can do: place sell orders at bid price to exit.
        flatten_results = []
        for o in placed_orders:
            if o["success"] and o["filled_size"] > 0:
                bracket = o["bracket"]
                logger.warning(
                    f"  FLATTEN: Selling {o['filled_size']} YES {bracket.ticker} "
                    f"(bought @ {o['filled_price']:.2f})"
                )
                try:
                    # Sell YES at bid price (accept lower price for immediate exit)
                    sell_price = bracket.yes_bid if bracket.yes_bid > 0 else bracket.yes_price - 0.01
                    sell_result = await asyncio.wait_for(
                        self.exchange.place_order(
                            ticker=bracket.ticker,
                            side=OrderSide.NO,  # Sell YES = buy NO
                            price=round(1.0 - sell_price, 2),
                            size=int(o["filled_size"]),
                            order_type=OrderType.IOC,  # IOC for immediate exit
                        ),
                        timeout=ORDER_TIMEOUT_SECONDS,
                    )
                    flatten_results.append({
                        "ticker": bracket.ticker,
                        "success": sell_result.success,
                        "filled_size": sell_result.filled_size,
                        "error": sell_result.error if not sell_result.success else "",
                    })
                except Exception as e:
                    flatten_results.append({
                        "ticker": bracket.ticker,
                        "success": False,
                        "error": str(e),
                    })

        # Record the partial fill as a loss in risk manager
        # (we entered and exited, net P&L is the slippage from bid-ask spread)
        for o in placed_orders:
            if o["success"] and o["filled_size"] > 0:
                self.risk_manager.record_trade(
                    ticker=o["bracket"].ticker,
                    size=int(o["filled_size"]),
                    cost=o["filled_price"] * o["filled_size"],
                    pnl=-0.02 * o["filled_size"],  # Estimated slippage loss per contract
                )

        flat_succeeded = sum(1 for r in flatten_results if r["success"])
        opp.status = OpportunityStatus.CANCELLED
        result["executed"] = False  # NOT executed — we flattened
        result["partial_flattened"] = True
        result["flatten_results"] = flatten_results

        logger.warning(
            f"  Strategy B ABORTED & FLATTENED: {flat_succeeded}/{initial_filled_count} "
            f"positions sold back. Remaining exposure may need manual settlement."
        )

        return result

    async def _safe_cancel_order(self, order_id: str) -> bool:
        """Cancel an order, returning True if successful. Non-blocking, logs errors."""
        try:
            return await asyncio.wait_for(
                self.exchange.cancel_order(order_id),
                timeout=5.0,
            )
        except (asyncio.TimeoutError, Exception) as e:
            logger.error(f"  Failed to cancel order {order_id}: {e}")
            return False

    async def _execute_single_market(self, opp: Opportunity, result: dict) -> dict:
        """Execute a single-market trade (Strategy A or C).

        Uses the explicit `direction` field on the Opportunity object.
        """
        side = OrderSide(opp.direction)  # "yes" or "no"

        try:
            order_result: OrderResult = await asyncio.wait_for(
                self.exchange.place_order(
                    ticker=opp.series_ticker,
                    side=side,
                    price=opp.total_cost,
                    size=opp.suggested_size,
                    order_type=OrderType.LIMIT,
                ),
                timeout=ORDER_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            return {**result, "error": "Order timed out"}
        except Exception as e:
            return {**result, "error": str(e)}

        result["orders"].append({
            "ticker": opp.series_ticker,
            "side": side.value,
            "price": opp.total_cost,
            "size": opp.suggested_size,
            "order_id": order_result.order_id,
            "filled_size": order_result.filled_size,
            "filled_price": order_result.filled_price,
            "simulated": False,
            "success": order_result.success,
            "error": order_result.error,
        })

        if order_result.success:
            opp.status = OpportunityStatus.EXECUTING
            result["executed"] = True
            if order_result.order_id:
                self.risk_manager.register_order_for_cancel(order_result.order_id)
            self.risk_manager.record_trade(
                ticker=opp.series_ticker,
                size=int(order_result.filled_size),
                cost=order_result.filled_price * order_result.filled_size,
            )
        else:
            opp.status = OpportunityStatus.CANCELLED
            result["error"] = order_result.error

        return result

    async def reconcile_positions(self) -> dict:
        """Reconcile open positions on restart.

        Checks for any open orders that may have been placed before a crash,
        cancels stale ones, and reports current position state.
        """
        logger.info("Reconciling positions...")

        try:
            balance = await self.exchange.get_balance()
            positions = await self.exchange.get_positions()

            logger.info(f"Balance: ${balance.available:.2f} available, ${balance.total:.2f} total")
            logger.info(f"Open positions: {len(positions)}")

            for pos in positions:
                logger.info(f"  {pos.ticker}: {pos.side} {pos.size} @ {pos.avg_price:.2f}")

            return {
                "balance": {"total": balance.total, "available": balance.available},
                "positions": [
                    {
                        "ticker": p.ticker,
                        "side": p.side,
                        "size": p.size,
                        "avg_price": p.avg_price,
                        "unrealized_pnl": p.unrealized_pnl,
                    }
                    for p in positions
                ],
            }
        except Exception as e:
            logger.error(f"Reconciliation failed: {e}")
            return {"error": str(e)}

    def _make_cycle_results(
        self,
        cycle_id: int,
        cycle_start: datetime,
        opportunities: List[Opportunity],
        execution_results: Optional[List[dict]] = None,
    ) -> List[dict]:
        """Package cycle results for logging and API responses."""
        results = []
        for opp in opportunities:
            # Find matching execution result
            exec_result = None
            if execution_results:
                for er in execution_results:
                    if er.get("series_ticker") == opp.series_ticker and str(er.get("target_date")) == str(opp.target_date):
                        exec_result = er
                        break

            results.append({
                "cycle_id": cycle_id,
                "opportunity_type": opp.opportunity_type.value,
                "series_ticker": opp.series_ticker,
                "city_key": opp.city_key,
                "target_date": str(opp.target_date),
                "edge": opp.edge,
                "edge_dollars": opp.edge_dollars,
                "total_cost": opp.total_cost,
                "suggested_size": opp.suggested_size,
                "confidence": opp.confidence,
                "status": opp.status.value,
                "num_brackets": opp.num_brackets,
                "reasoning": opp.reasoning[:200] if opp.reasoning else "",
                "skip_reasons": opp.skip_reasons[:10] if opp.skip_reasons else [],
                "roi_pct": opp.roi_pct,
                "execution": exec_result,
            })

        # Store in memory for dashboard
        self._results.extend(results)
        if len(self._results) > 1000:
            self._results = self._results[-500:]

        return results

    def get_recent_results(self, limit: int = 50) -> List[dict]:
        """Get recent cycle results for dashboard display."""
        return self._results[-limit:]

    def kill_switch(self, activate: bool = True):
        """Emergency stop — pause all trading immediately."""
        self.risk_manager.kill_switch(activate)