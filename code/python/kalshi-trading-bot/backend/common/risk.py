"""Risk management module — position sizing, daily limits, concentration caps,
circuit breakers, and drawdown protection.

All opportunities pass through the risk manager before execution.
The risk manager can:
  - Reduce position size (Kelly fraction cap)
  - Reject opportunities (insufficient edge, concentration too high)
  - Kill all trading (daily loss limit hit, drawdown breach, kill switch)
  - Auto-cancel open orders on risk halt
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from backend.common.config import settings
from backend.weather.scanner.opportunity import Opportunity, OpportunityType
from backend.common.alerting import alert_risk_halt, alert_daily_reset

logger = logging.getLogger("trading_bot")


@dataclass
class RiskLimits:
    """Configurable risk limits."""
    # Position limits
    daily_loss_limit: float = 300.0           # Max daily loss in dollars
    max_trade_size: float = 100.0             # Max dollars per single trade
    max_event_concentration: float = 0.15     # Max % of bankroll per event
    max_portfolio_exposure: float = 0.50      # Max % of bankroll across all positions
    max_daily_trades: int = 50                # Max number of trades per day
    max_pending_trades: int = 20              # Max open positions at once
    min_edge: float = 0.02                    # Minimum edge to trade (2%)
    kelly_fraction_cap: float = 0.25          # Max Kelly fraction (quarter Kelly)

    # Drawdown protection
    max_drawdown_pct: float = 0.10            # 10% drawdown from peak → halt
    max_consecutive_losses: int = 5           # Halt after N consecutive losses

    # Circuit breaker
    volatility_halt_threshold: float = 0.0    # Placeholder — future: detect extreme volatility
    rolling_loss_window_hours: int = 4        # Rolling window for loss tracking
    rolling_loss_limit: float = 200.0          # Max loss in rolling window

    # Liquidity / slippage
    min_market_volume: float = 100.0          # Skip markets with < $100 volume (weather markets are thin)
    max_position_pct_of_liquidity: float = 0.05  # Max 5% of available order book depth
    max_bracket_spread: float = 0.10          # Skip brackets with > 10c spread

    # Fee modeling
    fee_rate_per_contract: float = 0.01    # Kalshi fee: 1 cent per contract per trade (matches settings.KALSHI_FEE_RATE)


@dataclass
class TradeRecord:
    """Record of a completed trade for risk tracking."""
    ticker: str
    side: str
    size: int
    cost: float
    pnl: float = 0.0
    timestamp: str = ""
    is_loss: bool = False

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        self.is_loss = self.pnl < 0


@dataclass
class DailyStats:
    """Track daily trading statistics for risk management."""
    date: str = ""
    trades_executed: int = 0
    dollars_traded: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    positions_opened: List[str] = field(default_factory=list)
    trade_records: List[TradeRecord] = field(default_factory=list)
    peak_bankroll: float = 0.0
    consecutive_losses: int = 0

    def __post_init__(self):
        if not self.date:
            self.date = datetime.now(timezone.utc).strftime("%Y-%m-%d")


class RiskManager:
    """Pre-trade risk checks, position sizing, and circuit breakers.

    Called before any order is placed. Can approve, shrink, or reject
    an opportunity based on portfolio-level constraints.

    Implements:
    - Daily loss limit (flat cap)
    - Drawdown from high-water mark (percentage cap)
    - Consecutive loss tracking
    - Rolling window loss limit (4-hour)
    - Liquidity / slippage filter
    - Fee-adjusted edge calculation
    - Position size relative to order book depth
    - Portfolio-level exposure cap
    - Kill switch with auto-cancel
    - Automatic daily stats reset at UTC midnight
    """

    def __init__(self, limits: RiskLimits = None, bankroll: float = None):
        self.limits = limits or RiskLimits()
        self._daily_stats = DailyStats()
        self._killed = False  # Emergency kill switch
        self._bankroll_peak = bankroll or settings.INITIAL_BANKROLL  # High-water mark
        self._bankroll_override = bankroll  # Allow test injection
        self._order_ids_to_cancel: List[str] = []  # Orders to cancel on halt
        self._last_reset_date: str = ""  # Track last reset date for daily rollover

    def _check_day_reset(self):
        """Reset daily stats if the UTC date has changed since last reset.

        Called automatically at the start of is_trading_allowed() and
        record_trade(). This ensures daily loss limits, trade counts, and
        consecutive loss counters reset each UTC day instead of accumulating
        indefinitely.
        """
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self._last_reset_date and today != self._last_reset_date:
            # Preserve high-water mark across resets (bankroll peak is not daily)
            prev_bankroll = self.bankroll + self._daily_stats.realized_pnl
            logger.info(
                f"Daily stats reset: {self._last_reset_date} → {today} | "
                f"Prev day P&L: ${self._daily_stats.realized_pnl:.2f} | "
                f"Trades: {self._daily_stats.trades_executed}"
            )
            alert_daily_reset(
                yesterday_pnl=self._daily_stats.realized_pnl,
                trades=self._daily_stats.trades_executed,
                date_str=self._last_reset_date,
            )
            self._daily_stats = DailyStats()
            # Carry forward bankroll peak if we're above it
            if prev_bankroll > self._bankroll_peak:
                self._bankroll_peak = prev_bankroll
            self._last_reset_date = today
        elif not self._last_reset_date:
            self._last_reset_date = today

    @property
    def bankroll(self) -> float:
        """Current bankroll. Uses override if set (for testing), else config."""
        return self._bankroll_override if self._bankroll_override is not None else settings.INITIAL_BANKROLL

    def is_trading_allowed(self) -> Tuple[bool, str]:
        """Check if trading is allowed at all.

        Returns (allowed, reason) tuple.
        """
        self._check_day_reset()  # Roll over daily stats if date changed

        if self._killed:
            alert_risk_halt("Kill switch activated")
            return False, "Kill switch activated"

        # Daily loss limit (flat cap)
        if self._daily_stats.realized_pnl <= -self.limits.daily_loss_limit:
            alert_risk_halt(
                f"Daily loss limit reached: ${abs(self._daily_stats.realized_pnl):.2f}",
                details={"pnl": self._daily_stats.realized_pnl, "limit": self.limits.daily_loss_limit},
            )
            return False, f"Daily loss limit reached: ${abs(self._daily_stats.realized_pnl):.2f}"

        # Daily trade count
        if self._daily_stats.trades_executed >= self.limits.max_daily_trades:
            return False, f"Daily trade limit reached: {self._daily_stats.trades_executed}"

        # Drawdown from peak
        current_bankroll = self.bankroll + self._daily_stats.realized_pnl
        if self._bankroll_peak > 0 and current_bankroll < self._bankroll_peak:
            drawdown = (self._bankroll_peak - current_bankroll) / self._bankroll_peak
            if drawdown >= self.limits.max_drawdown_pct:
                alert_risk_halt(
                    f"Drawdown limit: {drawdown:.1%} from peak ${self._bankroll_peak:.2f}",
                    details={"drawdown_pct": drawdown, "peak": self._bankroll_peak, "current": current_bankroll},
                )
                return False, (
                    f"Drawdown limit: {drawdown:.1%} from peak "
                    f"${self._bankroll_peak:.2f}"
                )

        # Consecutive losses
        if self._daily_stats.consecutive_losses >= self.limits.max_consecutive_losses:
            alert_risk_halt(
                f"Consecutive loss limit: {self._daily_stats.consecutive_losses} losses in a row",
                details={"consecutive_losses": self._daily_stats.consecutive_losses},
            )
            return False, (
                f"Consecutive loss limit: {self._daily_stats.consecutive_losses} "
                f"losses in a row"
            )

        # Rolling window loss (4-hour)
        rolling_loss = self._compute_rolling_window_loss()
        if rolling_loss <= -self.limits.rolling_loss_limit:
            return False, (
                f"Rolling {self.limits.rolling_loss_window_hours}h loss limit: "
                f"${abs(rolling_loss):.2f}"
            )

        return True, "OK"

    def _compute_rolling_window_loss(self) -> float:
        """Compute realized P&L in the last N hours."""
        if not self.limits.rolling_loss_window_hours or not self._daily_stats.trade_records:
            return 0.0

        from datetime import timedelta
        window = timedelta(hours=self.limits.rolling_loss_window_hours)
        cutoff = datetime.now(timezone.utc) - window

        rolling_pnl = 0.0
        for record in self._daily_stats.trade_records:
            try:
                trade_time = datetime.fromisoformat(record.timestamp)
                if trade_time.tzinfo is None:
                    trade_time = trade_time.replace(tzinfo=timezone.utc)
                if trade_time >= cutoff:
                    rolling_pnl += record.pnl
            except (ValueError, TypeError):
                continue

        return rolling_pnl

    def approve_opportunity(
        self,
        opp: Opportunity,
        current_positions: Optional[Dict[str, float]] = None,
    ) -> Tuple[bool, float, str]:
        """Decide whether to trade an opportunity and at what size.

        Returns (approved, adjusted_size, reason).
        """
        # Check kill switch and daily limits
        allowed, reason = self.is_trading_allowed()
        if not allowed:
            return False, 0.0, reason

        # Check pending trades
        if len(self._daily_stats.positions_opened) >= self.limits.max_pending_trades:
            return False, 0.0, "Too many pending positions"

        # Check minimum edge
        # NOTE: For Strategy B, opp.edge is already fee-adjusted by the scanner
        # (check_cross_bracket_arb subtracts fees at line 246-248).
        # We do NOT subtract fees again here — that would be a double deduction.
        if opp.edge < self.limits.min_edge:
            return False, 0.0, f"Edge {opp.edge:.1%} below minimum {self.limits.min_edge:.1%}" 

        # Check concentration (same event = same city + same date)
        event_key = f"{opp.city_key}_{opp.target_date}"
        if current_positions:
            for pos_key, pos_value in current_positions.items():
                if event_key in pos_key:
                    if pos_value >= self.bankroll * self.limits.max_event_concentration:
                        return False, 0.0, (
                            f"Concentration limit: {event_key} at "
                            f"${pos_value:.2f} > "
                            f"{self.limits.max_event_concentration:.0%} of bankroll"
                        )

        # Portfolio-level exposure cap
        total_exposure = sum(current_positions.values()) if current_positions else 0
        if total_exposure >= self.bankroll * self.limits.max_portfolio_exposure:
            return False, 0.0, (
                f"Portfolio exposure limit: ${total_exposure:.2f} >= "
                f"{self.limits.max_portfolio_exposure:.0%} of bankroll"
            )

        # Check liquidity filter for Strategy B brackets
        if opp.opportunity_type == OpportunityType.STRATEGY_B and opp.brackets:
            for b in opp.brackets:
                if b.volume < self.limits.min_market_volume:
                    return False, 0.0, (
                        f"Liquidity filter: bracket {b.ticker} volume "
                        f"${b.volume:.0f} < ${self.limits.min_market_volume:.0f}"
                    )
                spread = b.yes_price - b.yes_bid if b.yes_bid > 0 else 0
                if spread > self.limits.max_bracket_spread:
                    return False, 0.0, (
                        f"Spread filter: bracket {b.ticker} spread "
                        f"{spread:.2f} > {self.limits.max_bracket_spread:.2f}"
                    )

        # Calculate position size
        base_size = opp.suggested_size

        if opp.opportunity_type == OpportunityType.STRATEGY_B and opp.brackets:
            # Each set costs total_cost (sum of all YES prices)
            total_cost_per_set = opp.total_cost
            max_sets_by_concentration = (
                self.bankroll * self.limits.max_event_concentration / total_cost_per_set
            )
            # Don't exceed max_trade_size per bracket — use total_cost_per_set
            # to compute how many full sets we can buy
            max_sets_by_trade_size = (
                self.limits.max_trade_size / total_cost_per_set
            )
            adjusted_size = min(max_sets_by_concentration, max_sets_by_trade_size, base_size)
        else:
            # Strategies A and C: use Kelly sizing with cap
            kelly_size = opp.suggested_size * self.limits.kelly_fraction_cap
            adjusted_size = min(kelly_size, self.limits.max_trade_size)

        # Reject if below 1 contract after truncation (don't floor to 1 — that bypasses sizing)
        # Truncate to integer contracts first, then check
        adjusted_size = int(adjusted_size)
        if adjusted_size < 1:
            return False, 0.0, (
                f"Position size {adjusted_size} below minimum 1 contract after truncation"
            )

        return True, adjusted_size, "Approved"

    def record_trade(self, ticker: str, size: int, cost: float, pnl: float = 0.0):
        """Record a completed trade for daily tracking.

        Args:
            ticker: Market ticker
            size: Number of contracts
            cost: Total cost of the trade
            pnl: Realized P&L from settlement (0 for opening trades)
        """
        self._check_day_reset()  # Roll over daily stats if date changed

        record = TradeRecord(
            ticker=ticker,
            side="yes",
            size=size,
            cost=cost,
            pnl=pnl,
        )
        self._daily_stats.trades_executed += 1
        self._daily_stats.dollars_traded += cost
        self._daily_stats.realized_pnl += pnl
        self._daily_stats.positions_opened.append(ticker)
        self._daily_stats.trade_records.append(record)

        # Track consecutive losses
        if pnl < 0:
            self._daily_stats.consecutive_losses += 1
        else:
            self._daily_stats.consecutive_losses = 0

        # Update high-water mark
        current_bankroll = self.bankroll + self._daily_stats.realized_pnl
        if current_bankroll > self._bankroll_peak:
            self._bankroll_peak = current_bankroll

    def register_order_for_cancel(self, order_id: str):
        """Register an order ID for auto-cancellation on risk halt."""
        self._order_ids_to_cancel.append(order_id)

    def get_orders_to_cancel(self) -> List[str]:
        """Get all order IDs that should be cancelled on risk halt."""
        return self._order_ids_to_cancel.copy()

    def clear_cancelled_orders(self, cancelled_ids: List[str]):
        """Remove cancelled order IDs after successful cancellation."""
        self._order_ids_to_cancel = [
            oid for oid in self._order_ids_to_cancel if oid not in cancelled_ids
        ]

    def kill_switch(self, activate: bool = True):
        """Emergency kill switch — pause all trading immediately."""
        self._killed = activate
        if activate:
            logger.critical("!!! KILL SWITCH ACTIVATED — ALL TRADING HALTED !!!")
        else:
            logger.info("Kill switch deactivated — trading resumed")

    def get_daily_stats(self) -> DailyStats:
        """Get current daily statistics."""
        return self._daily_stats