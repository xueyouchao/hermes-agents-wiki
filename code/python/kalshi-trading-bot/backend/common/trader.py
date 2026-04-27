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
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from backend.common.config import settings
from backend.common.risk import RiskManager, RiskLimits
from backend.common.exchange.base import ExchangeClient, OrderSide, OrderType, OrderResult, ExchangeError
from backend.common.exchange.kalshi import KalshiExchange, TransientExchangeError
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

# ── Retry settings for bracket orders ──
# How many times to retry each bracket order on transient failure
BRACKET_RETRY_ATTEMPTS = 3

# Delay between bracket retry attempts (seconds)
BRACKET_RETRY_DELAY = 1.0


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
            if strategies and len(strategies) == 1 and strategies[0] == "strategy_b":
                opportunities = await scan_strategy_b(self.exchange)
            else:
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
        total_edge = sum(r.get("edge_dollars", 0) * r.get("size", 1) for r in execution_results)

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
            "edge_dollars": opp.edge_dollars * opp.suggested_size,  # Total dollar profit for actual position size
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
        except TransientExchangeError as e:
            # All retries exhausted at both exchange layer and bracket layer
            result["error"] = f"Transient error after all retries: {e}"
            alert_execution_failure(
                strategy=opp.opportunity_type.value,
                ticker=opp.series_ticker,
                error=f"All retries exhausted: {e}",
            )
            logger.critical(
                f"  Execution failed (retries exhausted) for {opp.series_ticker}: {e}"
            )
        except ExchangeError as e:
            result["error"] = str(e)
            alert_execution_failure(
                strategy=opp.opportunity_type.value,
                ticker=opp.series_ticker,
                error=str(e),
            )
            logger.error(f"  Exchange error for {opp.series_ticker}: {e}", exc_info=True)
        except Exception as e:
            result["error"] = str(e)
            alert_execution_failure(
                strategy=opp.opportunity_type.value,
                ticker=opp.series_ticker,
                error=str(e),
            )
            logger.error(f"  Execution failed for {opp.series_ticker}: {e}", exc_info=True)

        return result

    # ── Strategy B: Two-phase commit with per-bracket retry ──────────

    async def _execute_strategy_b(self, opp: Opportunity, result: dict) -> dict:
        """Execute Strategy B — two-phase commit with per-bracket retry and compensating rollback.

        Phase 1: Place LIMIT (GTC) orders on ALL brackets with per-bracket retry.
          - Each bracket gets up to BRACKET_RETRY_ATTEMPTS attempts with backoff.
          - Transient errors (timeouts, 503s) are retried; permanent errors fail immediately.
        Phase 2: After a short wait, check fills.
          - If ALL brackets filled → arb complete, mark COMPLETE.
          - If any bracket failed after retries → COMPENSATING ROLLBACK:
            1. Cancel all unfilled/partially-filled orders
            2. Sell back any filled positions at market (flatten)
            3. Alert for manual intervention if rollback fails

        We NEVER leave partial fills unhedged. Either all brackets fill (arb) or
        we flatten and take the small loss on fills.
        """
        opp.status = OpportunityStatus.EXECUTING
        total_brackets = len(opp.brackets)

        # ── PRE-EXECUTION: Revalidate prices haven't moved ──────────
        MAX_PRICE_SLIPPAGE = 0.03  # 3 cents max slippage from scan
        for bracket in opp.brackets:
            try:
                orderbook = await asyncio.wait_for(
                    self.exchange.get_orderbook(bracket.ticker, depth=1),
                    timeout=5.0,
                )
                current_ask = orderbook.best_ask
                if current_ask > 0 and current_ask > bracket.yes_price + MAX_PRICE_SLIPPAGE:
                    logger.warning(
                        f"  Price revalidation FAILED for {bracket.ticker}: "
                        f"scan ask={bracket.yes_price:.2f}, current ask={current_ask:.2f} "
                        f"(slippage={current_ask - bracket.yes_price:.2f} > {MAX_PRICE_SLIPPAGE})"
                    )
                    # Update the bracket price to current ask if it's still profitable
                    if current_ask < 1.0:
                        bracket.yes_price = current_ask
                    else:
                        # Price too high — can't buy
                        result["error"] = f"Price moved for {bracket.ticker}: ask={current_ask:.2f}"
                        opp.status = OpportunityStatus.CANCELLED
                        return result
            except Exception as e:
                logger.warning(f"  Price revalidation skipped for {bracket.ticker}: {e}")
                continue

        # Re-check if arb still exists after price updates
        updated_total = sum(b.yes_price for b in opp.brackets)
        if updated_total >= 1.0:
            logger.warning(
                f"  Arb disappeared after revalidation: sum(YES)={updated_total:.4f} >= $1.00"
            )
            result["error"] = f"Arb no longer exists: sum(YES)={updated_total:.4f}"
            opp.status = OpportunityStatus.EXPIRED
            return result

        # ── PHASE 1: Place bracket orders with per-bracket retry ──────────
        placed_orders = await self._place_all_brackets(opp, result)

        # Count placements
        initial_placed_count = sum(1 for o in placed_orders if o["success"])
        initial_cost = sum(o["filled_price"] * o["filled_size"] for o in placed_orders if o["success"])

        # ── PHASE 1.5: Wait for LIMIT orders to fill ──────────
        logger.info(f"  Phase 1 complete ({initial_placed_count}/{total_brackets} placed). "
                     f"Waiting {FILL_WAIT_SECONDS}s for LIMIT fills...")
        await asyncio.sleep(FILL_WAIT_SECONDS)

        # ── PHASE 2: Poll fills ──────────
        await self._poll_fills(placed_orders, opp)

        # ── PHASE 3: Verify all brackets filled, rollback if not ──────────
        unfilled_orders = [o for o in placed_orders if o["success"] and o["filled_size"] < opp.suggested_size]
        completely_failed = [o for o in placed_orders if not o["success"]]
        all_filled = (initial_placed_count == total_brackets
                      and len(completely_failed) == 0
                      and len(unfilled_orders) == 0)

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
                f"  Strategy B COMPLETE: {initial_placed_count}/{total_brackets} brackets filled, "
                f"total cost ${initial_cost:.4f}"
            )
            return result

        # ── COMPENSATING ROLLBACK: Partial fill — flatten immediately ──────────
        alert_partial_fill(
            brackets_filled=initial_placed_count,
            brackets_total=total_brackets,
            tickers=[o["bracket"].ticker for o in placed_orders if o["success"]],
        )
        logger.critical(
            f"  !!! Strategy B PARTIAL FILL: {initial_placed_count}/{total_brackets} filled, "
            f"{len(completely_failed)} failed, {len(unfilled_orders)} partial. "
            f"ROLLING BACK ALL POSITIONS."
        )

        # Step 2b: Cancel any unfilled/partially-filled open orders
        cancel_tasks = []
        for o in placed_orders:
            if o["order_id"] and o["success"]:
                cancel_tasks.append(self._safe_cancel_order(o["order_id"]))

        if cancel_tasks:
            cancel_results = await asyncio.gather(*cancel_tasks)
            cancelled_count = sum(1 for r in cancel_results if r)
            logger.info(f"  Cancelled {cancelled_count}/{len(cancel_tasks)} open orders")

        # Step 2c: Compensating rollback — sell back all filled positions
        flatten_results = await self._rollback_filled_positions(placed_orders, opp.suggested_size)

        # Step 2d: Record the partial fill as a loss in risk manager
        for o in placed_orders:
            if o["success"] and o["filled_size"] > 0:
                self.risk_manager.record_trade(
                    ticker=o["bracket"].ticker,
                    size=int(o["filled_size"]),
                    cost=o["filled_price"] * o["filled_size"],
                    pnl=-0.02 * o["filled_size"],  # Estimated slippage loss per contract
                )

        flat_succeeded = sum(1 for r in flatten_results if r["success"])
        flat_failed = sum(1 for r in flatten_results if not r["success"])
        opp.status = OpportunityStatus.CANCELLED
        result["executed"] = False  # NOT executed — we rolled back
        result["partial_flattened"] = True
        result["flatten_results"] = flatten_results

        if flat_failed > 0:
            # Some positions couldn't be rolled back — this needs human attention
            failed_tickers = [r["ticker"] for r in flatten_results if not r["success"]]
            alert_execution_failure(
                strategy="strategy_b",
                ticker=",".join(failed_tickers),
                error=f"Rollback FAILED for {flat_failed} positions. MANUAL INTERVENTION REQUIRED.",
            )
            logger.critical(
                f"  ROLLBACK INCOMPLETE: {flat_succeeded} positions sold, "
                f"{flat_failed} ROLLBACK FAILED ({failed_tickers}). "
                f"MANUAL INTERVENTION REQUIRED for unhedged exposure."
            )
        else:
            logger.warning(
                f"  Strategy B ABORTED & ROLLED BACK: {flat_succeeded}/{initial_placed_count} "
                f"positions sold back. Small slippage loss taken."
            )

        return result

    async def _place_all_brackets(self, opp: Opportunity, result: dict) -> List[dict]:
        """Phase 1: Place LIMIT orders on all brackets with per-bracket retry.

        Returns list of placed_order dicts.
        """
        async def _place_bracket_with_retry(
            bracket: BracketMarket, max_attempts: int = BRACKET_RETRY_ATTEMPTS
        ) -> Tuple[BracketMarket, OrderResult, int]:
            """Place a single bracket order with retry on transient failures."""
            last_result = OrderResult(success=False, error="Not attempted")
            for attempt in range(1, max_attempts + 1):
                try:
                    order_result = await asyncio.wait_for(
                        self.exchange.place_order(
                            ticker=bracket.ticker,
                            side=OrderSide.YES,
                            price=bracket.yes_price,
                            size=opp.suggested_size,
                            order_type=OrderType.LIMIT,
                        ),
                        timeout=ORDER_TIMEOUT_SECONDS,
                    )
                    if order_result.success:
                        return bracket, order_result, attempt
                    # Non-transient failure from exchange — don't retry
                    if attempt < max_attempts:
                        logger.warning(
                            f"  Bracket {bracket.ticker} order failed (attempt {attempt}/{max_attempts}): "
                            f"{order_result.error}. Retrying in {BRACKET_RETRY_DELAY}s..."
                        )
                        await asyncio.sleep(BRACKET_RETRY_DELAY)
                    last_result = order_result
                except asyncio.TimeoutError:
                    last_result = OrderResult(success=False, error="Order timed out")
                    if attempt < max_attempts:
                        logger.warning(
                            f"  Bracket {bracket.ticker} timed out (attempt {attempt}/{max_attempts}). "
                            f"Retrying in {BRACKET_RETRY_DELAY}s..."
                        )
                        await asyncio.sleep(BRACKET_RETRY_DELAY)
                except Exception as e:
                    last_result = OrderResult(success=False, error=str(e))
                    if attempt < max_attempts:
                        logger.warning(
                            f"  Bracket {bracket.ticker} error (attempt {attempt}/{max_attempts}): {e}. "
                            f"Retrying in {BRACKET_RETRY_DELAY}s..."
                        )
                        await asyncio.sleep(BRACKET_RETRY_DELAY)

            # All attempts exhausted
            logger.error(
                f"  Bracket {bracket.ticker} FAILED after {max_attempts} attempts: {last_result.error}"
            )
            return bracket, last_result, max_attempts

        # Place all bracket orders concurrently (each with its own retry loop)
        order_tasks = [_place_bracket_with_retry(b) for b in opp.brackets]
        order_results = await asyncio.gather(*order_tasks)

        # Collect order details for Phase 2
        placed_orders: List[dict] = []
        for bracket, order_result, attempts in order_results:
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
                "attempts": attempts,
            }
            result["orders"].append(order_dict)

            placed_orders.append({
                "bracket": bracket,
                "order_id": order_result.order_id,
                "filled_size": order_result.filled_size,
                "filled_price": order_result.filled_price,
                "success": order_result.success,
                "attempts": attempts,
            })

            if order_result.success:
                if order_result.order_id:
                    self.risk_manager.register_order_for_cancel(order_result.order_id)
            else:
                logger.error(
                    f"  Order FAILED for {bracket.ticker} after {attempts} attempts: {order_result.error}"
                )

        return placed_orders

    async def _poll_fills(self, placed_orders: List[dict], opp: Opportunity):
        """Phase 2: Poll order status to get updated fill information."""
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
                        # Order not in open list — could be filled OR cancelled.
                        # Do NOT assume filled — cancelled orders leave us unhedged.
                        # Try to query order status explicitly.
                        try:
                            order_status = await asyncio.wait_for(
                                self.exchange.get_order_status(o["order_id"]),
                                timeout=5.0,
                            )
                            if order_status and order_status.get("status") in ("filled", "matched"):
                                filled_so_far = float(order_status.get("filled_count", opp.suggested_size))
                                o["filled_size"] = filled_so_far
                                o["filled_price"] = float(order_status.get("filled_price", 0)) / 100.0 or o["bracket"].yes_price
                                logger.info(f"  Poll: {o['bracket'].ticker} confirmed filled ({filled_so_far}/{opp.suggested_size})")
                            else:
                                # Order was cancelled or expired — treat as unfilled
                                logger.warning(f"  Poll: {o['bracket'].ticker} order status={order_status.get('status') if order_status else 'unknown'} — treating as UNFILLED")
                                o["filled_size"] = 0
                                rechecked_all_filled = False
                        except Exception as e2:
                            # Can't confirm status — log warning and treat as potentially unfilled
                            logger.warning(f"  Poll: {o['bracket'].ticker} cannot confirm order status: {e2} — treating as UNFILLED")
                            o["filled_size"] = 0
                            rechecked_all_filled = False
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

    async def _rollback_filled_positions(
        self,
        placed_orders: List[dict],
        original_size: int,
    ) -> List[dict]:
        """Sell back all filled positions to close unhedged exposure.

        This is the compensating action when Strategy B can't complete all brackets.
        We sell YES (i.e., buy NO) at the bid price for immediate exit.

        Each sell is retried up to BRACKET_RETRY_ATTEMPTS to maximize the chance
        that we don't leave unhedged positions open.
        """
        flatten_results = []

        for o in placed_orders:
            if not o["success"] or o["filled_size"] <= 0:
                continue

            bracket = o["bracket"]
            filled_size = int(o["filled_size"])

            logger.warning(
                f"  ROLLBACK: Selling {filled_size} YES {bracket.ticker} "
                f"(bought @ {o['filled_price']:.2f})"
            )

            # Retry the sell up to BRACKET_RETRY_ATTEMPTS times
            sell_success = False
            last_error = ""
            for attempt in range(1, BRACKET_RETRY_ATTEMPTS + 1):
                try:
                    # Re-fetch orderbook for current bid (scan-time bids may be stale)
                    current_sell_price = bracket.yes_bid if bracket.yes_bid > 0 else max(bracket.yes_price - 0.01, 0.01)
                    try:
                        fresh_orderbook = await asyncio.wait_for(
                            self.exchange.get_orderbook(bracket.ticker, depth=1),
                            timeout=3.0,
                        )
                        if fresh_orderbook.best_bid > 0:
                            current_sell_price = fresh_orderbook.best_bid
                            logger.info(f"  ROLLBACK: Using fresh bid {current_sell_price:.2f} for {bracket.ticker}")
                    except Exception as e:
                        logger.warning(f"  ROLLBACK: Could not fetch fresh orderbook for {bracket.ticker}: {e}, using scan-time bid")
                    sell_price = current_sell_price
                    sell_result = await asyncio.wait_for(
                        self.exchange.place_order(
                            ticker=bracket.ticker,
                            side=OrderSide.NO,  # Sell YES = buy NO
                            price=round(1.0 - sell_price, 2),
                            size=filled_size,
                            order_type=OrderType.IOC,  # IOC for immediate exit
                        ),
                        timeout=ORDER_TIMEOUT_SECONDS,
                    )
                    if sell_result.success:
                        flatten_results.append({
                            "ticker": bracket.ticker,
                            "success": True,
                            "filled_size": sell_result.filled_size,
                            "filled_price": sell_result.filled_price,
                            "error": "",
                        })
                        sell_success = True
                        logger.info(
                            f"  ROLLBACK OK: {bracket.ticker} sold {sell_result.filled_size} "
                            f"@ {sell_result.filled_price:.2f}"
                        )
                        break
                    else:
                        last_error = sell_result.error
                        if attempt < BRACKET_RETRY_ATTEMPTS:
                            logger.warning(
                                f"  ROLLBACK retry {bracket.ticker} (attempt {attempt}/{BRACKET_RETRY_ATTEMPTS}): "
                                f"{sell_result.error}"
                            )
                            await asyncio.sleep(BRACKET_RETRY_DELAY)
                except asyncio.TimeoutError:
                    last_error = "Sell order timed out"
                    if attempt < BRACKET_RETRY_ATTEMPTS:
                        logger.warning(
                            f"  ROLLBACK retry {bracket.ticker} (attempt {attempt}/{BRACKET_RETRY_ATTEMPTS}): "
                            f"timed out"
                        )
                        await asyncio.sleep(BRACKET_RETRY_DELAY)
                except Exception as e:
                    last_error = str(e)
                    if attempt < BRACKET_RETRY_ATTEMPTS:
                        logger.warning(
                            f"  ROLLBACK retry {bracket.ticker} (attempt {attempt}/{BRACKET_RETRY_ATTEMPTS}): {e}"
                        )
                        await asyncio.sleep(BRACKET_RETRY_DELAY)

            if not sell_success:
                flatten_results.append({
                    "ticker": bracket.ticker,
                    "success": False,
                    "filled_size": 0,
                    "error": f"ROLLBACK FAILED after {BRACKET_RETRY_ATTEMPTS} attempts: {last_error}",
                })
                logger.critical(
                    f"  ROLLBACK FAILED: {bracket.ticker} — could not sell {filled_size} YES. "
                    f"MANUAL INTERVENTION REQUIRED. Last error: {last_error}"
                )

        return flatten_results

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

        Additionally, detects orphaned Strategy B positions — cases where
        only some brackets of a cross-bracket arbitrage filled before the
        process crashed. These positions are directionally exposed and should
        be flattened.
        """
        logger.info("Reconciling positions from previous session...")

        try:
            balance = await self.exchange.get_balance()
            positions = await self.exchange.get_positions()

            logger.info(f"Balance: ${balance.available:.2f} available, ${balance.total:.2f} total")
            logger.info(f"Open positions: {len(positions)}")

            for pos in positions:
                logger.info(f"  {pos.ticker}: {pos.side} {pos.size} @ {pos.avg_price:.2f}")

            # ── Detect orphaned Strategy B positions ──────────
            orphaned = self._detect_orphaned_positions(positions)

            if orphaned:
                logger.warning(
                    f"Found {len(orphaned)} orphaned position groups. "
                    f"Attempting to flatten..."
                )
                flatten_results = []
                for group in orphaned:
                    logger.warning(
                        f"  Orphaned group: {group['event_key']} — "
                        f"{group['filled_count']}/{group['expected_brackets']} brackets"
                    )
                    # Flatten each bracket in the orphaned group
                    for pos in group["positions"]:
                        try:
                            # Sell at market to exit
                            sell_price = max(pos.avg_price - 0.02, 0.01)  # Slightly below entry
                            sell_result = await asyncio.wait_for(
                                self.exchange.place_order(
                                    ticker=pos.ticker,
                                    side=OrderSide.NO,
                                    price=round(1.0 - sell_price, 2),
                                    size=int(pos.size),
                                    order_type=OrderType.IOC,
                                ),
                                timeout=ORDER_TIMEOUT_SECONDS,
                            )
                            flatten_results.append({
                                "ticker": pos.ticker,
                                "success": sell_result.success,
                                "filled_size": sell_result.filled_size,
                                "error": sell_result.error if not sell_result.success else "",
                            })
                            if sell_result.success:
                                logger.info(f"  Flattened orphaned {pos.ticker}")
                            else:
                                logger.error(
                                    f"  Failed to flatten {pos.ticker}: {sell_result.error}"
                                )
                        except Exception as e:
                            flatten_results.append({
                                "ticker": pos.ticker,
                                "success": False,
                                "error": str(e),
                            })
                            logger.error(f"  Exception flattening {pos.ticker}: {e}")

                flat_ok = sum(1 for r in flatten_results if r["success"])
                flat_fail = sum(1 for r in flatten_results if not r["success"])
                if flat_fail > 0:
                    failed_tickers = [r["ticker"] for r in flatten_results if not r["success"]]
                    logger.critical(
                        f"  Startup reconciliation: {flat_ok} positions flattened, "
                        f"{flat_fail} FAILED ({failed_tickers}). MANUAL INTERVENTION REQUIRED."
                    )
                    alert_execution_failure(
                        strategy="strategy_b",
                        ticker=",".join(failed_tickers),
                        error=f"Startup reconciliation: {flat_fail} orphaned positions could not be flattened.",
                    )
                else:
                    logger.info(f"  Startup reconciliation: all {flat_ok} orphaned positions flattened.")
            else:
                logger.info("No orphaned Strategy B positions detected.")

            # Cancel any stale open orders
            try:
                open_orders = await self.exchange.get_open_orders()
                if open_orders:
                    logger.info(f"Found {len(open_orders)} stale open orders, cancelling...")
                    for order in open_orders:
                        order_id = str(order.get("id", ""))
                        if order_id:
                            try:
                                await self.exchange.cancel_order(order_id)
                                logger.info(f"  Cancelled stale order {order_id}")
                            except Exception as e:
                                logger.warning(f"  Could not cancel stale order {order_id}: {e}")
            except Exception as e:
                logger.warning(f"Could not check for stale open orders: {e}")

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
                "orphaned_groups": len(orphaned),
            }
        except Exception as e:
            logger.error(f"Reconciliation failed: {e}")
            return {"error": str(e)}

    def _detect_orphaned_positions(self, positions: List) -> List[dict]:
        """Detect incomplete Strategy B positions that are missing brackets.

        Groups positions by event (series_ticker + date extracted from ticker).
        If an event has positions in fewer brackets than expected,
        those positions are orphaned — they represent a partial Strategy B
        execution where the process crashed before all brackets filled or
        before rollback completed.

        Returns a list of dicts: {
            "event_key": str,
            "positions": List[Position],
            "filled_count": int,
            "expected_brackets": int,
        }
        """
        if not positions:
            return []

        # Group positions by event key (extracted from ticker pattern like KXHIGHNY-26MAY01-...)
        from collections import defaultdict
        event_groups: Dict[str, List] = defaultdict(list)

        for pos in positions:
            # Extract event key from ticker: "KXHIGHNY-26MAY01-B45.5" → "KXHIGHNY-26MAY01"
            parts = pos.ticker.rsplit("-", 1)
            if len(parts) == 2 and parts[1][0] in ("B", "T"):
                event_key = parts[0]
                event_groups[event_key].append(pos)

        # Heuristic: positions in 1-5 brackets of the same event are likely orphaned
        # from a partial Strategy B execution. 6+ brackets likely means a complete set.
        # This can be overridden via KALSHI_EXPECTED_BRACKETS env var.
        _expected_brackets = int(os.getenv("KALSHI_EXPECTED_BRACKETS", "0"))

        orphaned = []
        for event_key, event_positions in event_groups.items():
            if _expected_brackets > 0:
                # Use the explicit config
                EXPECTED_BRACKETS = _expected_brackets
                if len(event_positions) < EXPECTED_BRACKETS:
                    orphaned.append({
                        "event_key": event_key,
                        "positions": event_positions,
                        "filled_count": len(event_positions),
                        "expected_brackets": EXPECTED_BRACKETS,
                    })
            else:
                # Heuristic: 1-5 positions in an event group = likely orphaned
                # 6+ = likely complete Strategy B
                if 0 < len(event_positions) <= 5:
                    orphaned.append({
                        "event_key": event_key,
                        "positions": event_positions,
                        "filled_count": len(event_positions),
                        "expected_brackets": 6,  # Default estimate
                    })

        return orphaned

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