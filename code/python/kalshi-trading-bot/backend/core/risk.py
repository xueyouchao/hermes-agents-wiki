"""Risk management module — position sizing, daily limits, and concentration caps.

All opportunities pass through the risk manager before execution.
The risk manager can:
  - Reduce position size (Kelly fraction cap)
  - Reject opportunities (insufficient edge, concentration too high)
  - Kill all trading (daily loss limit hit)
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from backend.config import settings
from backend.scanner.opportunity import Opportunity, OpportunityType

logger = logging.getLogger("trading_bot")


@dataclass
class RiskLimits:
    """Configurable risk limits."""
    daily_loss_limit: float = 300.0           # Max daily loss in dollars
    max_trade_size: float = 100.0             # Max dollars per single trade
    max_event_concentration: float = 0.15     # Max % of bankroll per event
    max_daily_trades: int = 50                # Max number of trades per day
    max_pending_trades: int = 20              # Max open positions at once
    min_edge: float = 0.02                    # Minimum edge to trade (2%)
    kelly_fraction_cap: float = 0.25          # Max Kelly fraction (quarter Kelly)


@dataclass
class DailyStats:
    """Track daily trading statistics for risk management."""
    date: str = ""
    trades_executed: int = 0
    dollars_traded: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    positions_opened: List[str] = None

    def __post_init__(self):
        if self.positions_opened is None:
            self.positions_opened = []
        if not self.date:
            self.date = datetime.utcnow().strftime("%Y-%m-%d")


class RiskManager:
    """Pre-trade risk checks and position sizing.

    Called before any order is placed. Can approve, shrink, or reject
    an opportunity based on portfolio-level constraints.
    """

    def __init__(self, limits: RiskLimits = None):
        self.limits = limits or RiskLimits()
        self._daily_stats = DailyStats()
        self._killed = False  # Emergency kill switch

    @property
    def bankroll(self) -> float:
        """Current bankroll (from config for now, live balance later)."""
        return settings.INITIAL_BANKROLL

    def is_trading_allowed(self) -> Tuple[bool, str]:
        """Check if trading is allowed at all.

        Returns (allowed, reason) tuple.
        """
        if self._killed:
            return False, "Kill switch activated"

        if self._daily_stats.realized_pnl <= -self.limits.daily_loss_limit:
            return False, f"Daily loss limit reached: ${abs(self._daily_stats.realized_pnl):.2f}"

        if self._daily_stats.trades_executed >= self.limits.max_daily_trades:
            return False, f"Daily trade limit reached: {self._daily_stats.trades_executed}"

        return True, "OK"

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
        if opp.edge < self.limits.min_edge:
            return False, 0.0, f"Edge {opp.edge:.1%} below minimum {self.limits.min_edge:.1%}"

        # Check concentration (same event = same city + same date)
        if current_positions:
            event_key = f"{opp.city_key}_{opp.target_date}"
            for pos_key, pos_value in current_positions.items():
                if event_key in pos_key:
                    if pos_value >= self.bankroll * self.limits.max_event_concentration:
                        return False, 0.0, (
                            f"Concentration limit: {event_key} at "
                            f"${pos_value:.2f} > "
                            f"{self.limits.max_event_concentration:.0%} of bankroll"
                        )

        # Calculate position size
        base_size = opp.suggested_size

        # For Strategy B: size = max contracts we can afford per bracket
        # (need to buy one per bracket, so total = brackets * per-bracket)
        if opp.opportunity_type == OpportunityType.STRATEGY_B and opp.brackets:
            # Each contract costs the YES ask price
            total_cost_per_set = opp.total_cost  # sum of all YES prices
            max_sets = self.bankroll * self.limits.max_event_concentration / total_cost_per_set
            # Don't exceed max_trade_size per bracket
            max_by_trade_limit = self.limits.max_trade_size / max(b.yes_price for b in opp.brackets)
            adjusted_size = min(max_sets, max_by_trade_limit, base_size)
        else:
            # Strategies A and C (or Strategy B without brackets from test): use Kelly sizing with cap
            kelly_size = opp.suggested_size * self.limits.kelly_fraction_cap
            adjusted_size = min(kelly_size, self.limits.max_trade_size)

        # Floor at 1 contract
        if adjusted_size < 1:
            adjusted_size = 1

        adjusted_size = int(adjusted_size)

        return True, adjusted_size, "Approved"

    def record_trade(self, ticker: str, size: int, cost: float):
        """Record a completed trade for daily tracking."""
        self._daily_stats.trades_executed += 1
        self._daily_stats.dollars_traded += cost
        self._daily_stats.positions_opened.append(ticker)

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