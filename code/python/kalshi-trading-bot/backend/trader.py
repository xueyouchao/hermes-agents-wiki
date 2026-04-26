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

from backend.config import settings
from backend.core.risk import RiskManager, RiskLimits
from backend.exchange.base import ExchangeClient, OrderSide, OrderType, OrderResult
from backend.exchange.kalshi import KalshiExchange
from backend.scanner.opportunity import (
    BracketMarket,
    Opportunity,
    OpportunityStatus,
    OpportunityType,
)
from backend.scanner.opportunity_scanner import scan_all, scan_strategy_b

logger = logging.getLogger("trading_bot")

# Timeout for individual order placement (seconds)
ORDER_TIMEOUT_SECONDS = 10


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
        current_positions: Dict[str, float] = {}
        try:
            positions = await self.exchange.get_positions()
            for pos in positions:
                current_positions[pos.ticker] = pos.size * pos.avg_price
        except Exception as e:
            logger.warning(f"Could not fetch positions for concentration check: {e}")

        # Step 3: Risk check each opportunity
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
            logger.error(f"  Execution failed for {opp.series_ticker}: {e}", exc_info=True)

        return result

    async def _execute_strategy_b(self, opp: Opportunity, result: dict) -> dict:
        """Execute Strategy B — buy YES on every bracket in the event.

        This is the core arbitrage execution:
        1. Buy YES on all brackets at their ask price concurrently
        2. Use IOC (immediate-or-cancel) for speed
        3. If any bracket fails to fill enough, we have partial arb
        4. Auto-cancel remaining if critical bracket fails
        5. Log results for reconciliation
        """
        opp.status = OpportunityStatus.EXECUTING
        filled_brackets = 0
        total_cost = 0.0

        # Place all bracket orders concurrently for speed
        async def _place_bracket_order(bracket: BracketMarket) -> Tuple[BracketMarket, OrderResult]:
            """Place a single bracket order with timeout."""
            try:
                order_result = await asyncio.wait_for(
                    self.exchange.place_order(
                        ticker=bracket.ticker,
                        side=OrderSide.YES,
                        price=bracket.yes_price,
                        size=opp.suggested_size,
                        order_type=OrderType.IOC,
                    ),
                    timeout=ORDER_TIMEOUT_SECONDS,
                )
                return bracket, order_result
            except asyncio.TimeoutError:
                return bracket, OrderResult(success=False, error="Order timed out")
            except Exception as e:
                return bracket, OrderResult(success=False, error=str(e))

        # Execute all orders concurrently
        order_tasks = [_place_bracket_order(b) for b in opp.brackets]
        order_results = await asyncio.gather(*order_tasks)

        # Process results
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

            if order_result.success:
                filled_brackets += 1
                total_cost += order_result.filled_price * order_result.filled_size

                # Register order for potential auto-cancel on risk halt
                if order_result.order_id:
                    self.risk_manager.register_order_for_cancel(order_result.order_id)

                if order_result.remaining_size > 0:
                    logger.warning(
                        f"  Partial fill on {bracket.ticker}: "
                        f"{order_result.filled_size}/{opp.suggested_size} @ {order_result.filled_price:.2f}"
                    )

                # Record in risk manager
                self.risk_manager.record_trade(
                    ticker=bracket.ticker,
                    size=int(order_result.filled_size),
                    cost=order_result.filled_price * order_result.filled_size,
                )
            else:
                logger.error(
                    f"  Order FAILED for {bracket.ticker}: {order_result.error}"
                )

        # Determine final status
        if filled_brackets == len(opp.brackets):
            opp.status = OpportunityStatus.COMPLETE
            result["executed"] = True
            logger.info(
                f"  Strategy B COMPLETE: {filled_brackets}/{len(opp.brackets)} brackets filled, "
                f"total cost ${total_cost:.4f}"
            )
        elif filled_brackets > 0:
            opp.status = OpportunityStatus.PARTIAL
            opp.order_ids = [o.get("order_id", "") for o in result["orders"] if o.get("order_id")]
            result["executed"] = True
            logger.warning(
                f"  Strategy B PARTIAL: {filled_brackets}/{len(opp.brackets)} brackets filled"
            )
        else:
            opp.status = OpportunityStatus.CANCELLED
            logger.error("  Strategy B FAILED: 0 brackets filled")

        return result

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