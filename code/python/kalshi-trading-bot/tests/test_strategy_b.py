"""Tests for Strategy B — cross-bracket sum arbitrage scanner."""
import pytest
from datetime import date

from backend.weather.scanner.opportunity import BracketMarket, OpportunityType
from backend.weather.scanner.strategy_b import check_cross_bracket_arb, _group_brackets_by_event


def make_bracket(
    ticker: str,
    yes_price: float,
    volume: float = 100.0,
    threshold: float = 50.0,
    yes_bid: float = 0.0,
) -> BracketMarket:
    """Helper to create a BracketMarket for testing."""
    return BracketMarket(
        ticker=ticker,
        yes_price=yes_price,
        no_price=1.0 - yes_price,
        yes_bid=yes_bid if yes_bid > 0 else yes_price - 0.02,
        no_bid=1.0 - yes_price - 0.02,
        threshold_f=threshold,
        direction="above",
        volume=volume,
    )


class TestCheckCrossBracketArb:
    """Test the core arbitrage detection logic."""

    def test_no_arb_when_sum_equals_one(self):
        """If sum(YES) = 1.00, no arbitrage exists."""
        brackets = [
            make_bracket("KXHIGHNY-26MAY01-B40", 0.15),
            make_bracket("KXHIGHNY-26MAY01-B50", 0.25),
            make_bracket("KXHIGHNY-26MAY01-B60", 0.30),
            make_bracket("KXHIGHNY-26MAY01-B70", 0.20),
            make_bracket("KXHIGHNY-26MAY01-B80", 0.07),
            make_bracket("KXHIGHNY-26MAY01-T80", 0.03),
        ]
        result = check_cross_bracket_arb(brackets)
        assert result is None

    def test_arb_when_sum_below_one(self):
        """If sum(YES) < 1.00, arbitrage should be detected."""
        brackets = [
            make_bracket("KXHIGHNY-26MAY01-B40", 0.12),
            make_bracket("KXHIGHNY-26MAY01-B50", 0.20),
            make_bracket("KXHIGHNY-26MAY01-B60", 0.25),
            make_bracket("KXHIGHNY-26MAY01-B70", 0.18),
            make_bracket("KXHIGHNY-26MAY01-B80", 0.05),
            make_bracket("KXHIGHNY-26MAY01-T80", 0.02),
        ]
        # sum = 0.82, raw edge = 0.18
        # fees = 6 * $0.01 = $0.06, net edge = 0.18 - 0.06 = 0.12
        result = check_cross_bracket_arb(brackets, series_ticker="KXHIGHNY", city_key="nyc")
        assert result is not None
        assert result.opportunity_type == OpportunityType.STRATEGY_B
        assert abs(result.edge - 0.12) < 0.001  # Fee-adjusted edge
        assert abs(result.total_cost - 0.82) < 0.001
        assert result.num_brackets == 6

    def test_no_arb_when_edge_too_small(self):
        """If sum(YES) = 0.99, edge is only 1 cent — below threshold."""
        brackets = [
            make_bracket("KXHIGHNY-26MAY01-B40", 0.10),
            make_bracket("KXHIGHNY-26MAY01-B50", 0.20),
            make_bracket("KXHIGHNY-26MAY01-B60", 0.30),
            make_bracket("KXHIGHNY-26MAY01-B70", 0.20),
            make_bracket("KXHIGHNY-26MAY01-B80", 0.10),
            make_bracket("KXHIGHNY-26MAY01-T80", 0.09),
        ]
        # sum = 0.99, edge = 0.01 < MIN_STRATEGY_B_EDGE (0.02)
        result = check_cross_bracket_arb(brackets)
        assert result is None

    def test_no_arb_with_too_few_brackets(self):
        """Can't have arb with fewer than 4 brackets."""
        brackets = [
            make_bracket("KXHIGHNY-26MAY01-B40", 0.40),
            make_bracket("KXHIGHNY-26MAY01-B50", 0.40),
        ]
        result = check_cross_bracket_arb(brackets)
        assert result is None

    def test_realistic_scenario(self):
        """Realistic scenario: 6 brackets with sum=0.88, net edge after fees."""
        brackets = [
            make_bracket("KXHIGHNY-26MAY01-B32.5", 0.03, volume=200, threshold=32.5),
            make_bracket("KXHIGHNY-26MAY01-B45.5", 0.05, volume=300, threshold=45.5),
            make_bracket("KXHIGHNY-26MAY01-B58.5", 0.15, volume=500, threshold=58.5),
            make_bracket("KXHIGHNY-26MAY01-B71.5", 0.30, volume=400, threshold=71.5),
            make_bracket("KXHIGHNY-26MAY01-B84.5", 0.20, volume=250, threshold=84.5),
            make_bracket("KXHIGHNY-26MAY01-T84.5", 0.15, volume=150, threshold=84.5),
        ]
        # sum = 0.88, raw edge = 0.12
        # fees = 6 * $0.01 = $0.06, net edge = 0.12 - 0.06 = 0.06
        result = check_cross_bracket_arb(brackets, "KXHIGHNY", "nyc")
        assert result is not None
        assert abs(result.edge - 0.06) < 0.001  # Fee-adjusted edge
        assert result.confidence >= 0.9  # High confidence for pure arb
        assert result.direction == "yes"

    def test_skip_reasons_populated_on_filter(self):
        """Skip reasons should be tracked when markets are filtered out."""
        skip_reasons = []
        brackets = [
            make_bracket("KXHIGHNY-26MAY01-B40", 0.40),
            make_bracket("KXHIGHNY-26MAY01-B50", 0.40),
        ]
        result = check_cross_bracket_arb(brackets, skip_reasons=skip_reasons)
        assert result is None
        assert len(skip_reasons) > 0
        assert any("Too few brackets" in r for r in skip_reasons)

    def test_roi_calculation(self):
        """ROI should be calculated correctly (with fees)."""
        brackets = [
            make_bracket("KXHIGHNY-26MAY01-B40", 0.10),
            make_bracket("KXHIGHNY-26MAY01-B50", 0.15),
            make_bracket("KXHIGHNY-26MAY01-B60", 0.20),
            make_bracket("KXHIGHNY-26MAY01-B70", 0.25),
            make_bracket("KXHIGHNY-26MAY01-B80", 0.05),
            make_bracket("KXHIGHNY-26MAY01-T80", 0.03),
        ]
        # sum = 0.78, raw edge = 0.22
        # fees = 6 * $0.01 = $0.06, net edge = 0.22 - 0.06 = 0.16
        result = check_cross_bracket_arb(brackets, "KXHIGHNY", "nyc")
        assert result is not None
        assert result.roi_pct > 0

    def test_low_volume_bracket_filtered(self):
        """Brackets with very low volume should be filtered out."""
        brackets = [
            make_bracket("KXHIGHNY-26MAY01-B40", 0.10, volume=10),    # Below MIN_BRACKET_VOLUME
            make_bracket("KXHIGHNY-26MAY01-B50", 0.15, volume=200),
            make_bracket("KXHIGHNY-26MAY01-B60", 0.20, volume=300),
            make_bracket("KXHIGHNY-26MAY01-B70", 0.25, volume=400),
            make_bracket("KXHIGHNY-26MAY01-B80", 0.05, volume=250),
            make_bracket("KXHIGHNY-26MAY01-T80", 0.03, volume=150),
        ]
        skip_reasons = []
        result = check_cross_bracket_arb(brackets, skip_reasons=skip_reasons)
        # Should be filtered because one bracket has low volume (and yes_price > 0.05)
        assert result is None or any("Low volume" in r for r in skip_reasons)


class TestGroupBracketsByEvent:
    """Test bracket grouping by event."""

    def test_groups_correctly(self):
        """Brackets for same event should be grouped together."""
        brackets = [
            make_bracket("KXHIGHNY-26MAY01-B40", 0.15),
            make_bracket("KXHIGHNY-26MAY01-B50", 0.25),
            make_bracket("KXHIGHNY-26MAY02-B40", 0.20),  # Different date
            make_bracket("KXHIGHNY-26MAY02-B50", 0.30),
        ]
        events = _group_brackets_by_event(brackets)
        assert "KXHIGHNY-26MAY01" in events
        assert "KXHIGHNY-26MAY02" in events
        assert len(events["KXHIGHNY-26MAY01"]) == 2
        assert len(events["KXHIGHNY-26MAY02"]) == 2


class TestRiskManager:
    """Test risk manager approval logic."""

    def test_approve_good_opportunity(self):
        """Good opportunity should be approved."""
        from backend.common.risk import RiskManager, RiskLimits
        from backend.weather.scanner.opportunity import Opportunity

        # Use fee_rate_per_contract=0 for this test so edge=0.10 passes min_edge check
        # (In production, fee is $0.01/contract and edge is fee-adjusted)
        limits = RiskLimits(daily_loss_limit=300, max_trade_size=100, fee_rate_per_contract=0.0)
        rm = RiskManager(limits)

        opp = Opportunity(
            opportunity_type=OpportunityType.STRATEGY_B,
            series_ticker="KXHIGHNY",
            city_key="nyc",
            city_name="New York",
            target_date=date(2026, 5, 1),
            edge=0.06,
            edge_dollars=0.06,
            total_cost=0.94,
            suggested_size=1,
            direction="yes",
            brackets=[
                make_bracket("KXHIGHNY-26MAY01-B32.5", 0.03, volume=200, threshold=32.5),
                make_bracket("KXHIGHNY-26MAY01-B45.5", 0.10, volume=300, threshold=45.5),
                make_bracket("KXHIGHNY-26MAY01-B58.5", 0.25, volume=500, threshold=58.5),
                make_bracket("KXHIGHNY-26MAY01-B71.5", 0.30, volume=400, threshold=71.5),
                make_bracket("KXHIGHNY-26MAY01-B84.5", 0.15, volume=250, threshold=84.5),
                make_bracket("KXHIGHNY-26MAY01-T84.5", 0.11, volume=150, threshold=84.5),
            ],
        )
        approved, size, reason = rm.approve_opportunity(opp)
        assert approved
        assert size >= 1

    def test_reject_when_killed(self):
        """Kill switch should reject all opportunities."""
        from backend.common.risk import RiskManager
        from backend.weather.scanner.opportunity import Opportunity

        rm = RiskManager()
        rm.kill_switch(True)

        opp = Opportunity(
            opportunity_type=OpportunityType.STRATEGY_B,
            series_ticker="KXHIGHNY",
            city_key="nyc",
            city_name="New York",
            target_date=date(2026, 5, 1),
            edge=0.10,
            suggested_size=1,
        )
        approved, size, reason = rm.approve_opportunity(opp)
        assert not approved
        assert "Kill switch" in reason

    def test_drawdown_halt(self):
        """Drawdown from peak should halt trading."""
        from backend.common.risk import RiskManager, RiskLimits

        limits = RiskLimits(max_drawdown_pct=0.10, daily_loss_limit=10000)
        rm = RiskManager(limits=limits, bankroll=1000.0)
        rm._bankroll_peak = 1000.0
        rm._daily_stats.realized_pnl = -110.0  # 11% drawdown from 1000

        allowed, reason = rm.is_trading_allowed()
        assert not allowed
        assert "Drawdown" in reason

    def test_consecutive_loss_halt(self):
        """Consecutive losses should halt trading."""
        from backend.common.risk import RiskManager, RiskLimits

        limits = RiskLimits(max_consecutive_losses=3, daily_loss_limit=10000)
        rm = RiskManager(limits=limits)
        rm._daily_stats.consecutive_losses = 3

        allowed, reason = rm.is_trading_allowed()
        assert not allowed
        assert "Consecutive loss" in reason

    def test_rolling_window_loss_halt(self):
        """Rolling window loss should halt trading."""
        from backend.common.risk import RiskManager, RiskLimits
        from datetime import datetime, timezone, timedelta

        limits = RiskLimits(rolling_loss_limit=50.0, rolling_loss_window_hours=4, daily_loss_limit=10000)
        rm = RiskManager(limits=limits)

        # Add a recent large loss
        from backend.common.risk import TradeRecord
        rm._daily_stats.trade_records.append(
            TradeRecord(ticker="TEST", side="yes", size=1, cost=1.0, pnl=-60.0)
        )

        allowed, reason = rm.is_trading_allowed()
        assert not allowed
        assert "Rolling" in reason

    def test_fee_adjusted_edge_rejection(self):
        """Opportunities with fee-adjusted edge below min_edge should be rejected.

        IMPORTANT: opp.edge is already fee-adjusted by the scanner
        (check_cross_bracket_arb deducts fees). The risk manager does NOT
        re-subtract fees — it just compares opp.edge against min_edge.
        """
        from backend.common.risk import RiskManager, RiskLimits
        from backend.weather.scanner.opportunity import Opportunity

        limits = RiskLimits(min_edge=0.03)
        rm = RiskManager(limits=limits)

        # This represents what the scanner would produce after fee deduction:
        # Gross edge was 0.04, minus 6 * 0.01 fees = -0.02 (net)
        opp = Opportunity(
            opportunity_type=OpportunityType.STRATEGY_B,
            series_ticker="KXHIGHNY",
            city_key="nyc",
            city_name="New York",
            target_date=date(2026, 5, 1),
            edge=0.02,  # Already fee-adjusted (net edge after fees)
            edge_dollars=0.02,
            total_cost=0.96,
            suggested_size=1,
            brackets=[BracketMarket(ticker=f"T{i}", yes_price=0.16, no_price=0.84, threshold_f=50, direction="above", volume=200) for i in range(6)],
        )
        # 0.02 < 0.03 min_edge → rejected
        approved, size, reason = rm.approve_opportunity(opp)
        assert not approved
        assert "edge" in reason.lower() or "below" in reason.lower()

    def test_auto_cancel_on_kill_switch(self):
        """Kill switch should trigger auto-cancel of registered orders."""
        from backend.common.risk import RiskManager

        rm = RiskManager()
        rm.register_order_for_cancel("order-123")
        rm.register_order_for_cancel("order-456")

        rm.kill_switch(True)
        order_ids = rm.get_orders_to_cancel()
        assert "order-123" in order_ids
        assert "order-456" in order_ids

        rm.clear_cancelled_orders(["order-123"])
        remaining = rm.get_orders_to_cancel()
        assert "order-123" not in remaining
        assert "order-456" in remaining

    def test_daily_trade_count_limit(self):
        """Daily trade count limit should block trading."""
        from backend.common.risk import RiskManager, RiskLimits

        limits = RiskLimits(max_daily_trades=3, daily_loss_limit=10000)
        rm = RiskManager(limits=limits)
        rm._daily_stats.trades_executed = 3

        allowed, reason = rm.is_trading_allowed()
        assert not allowed
        assert "trade limit" in reason.lower()

    def test_size_below_one_rejected(self):
        """Position size below 1 contract should be rejected (no floor-of-1 override)."""
        from backend.common.risk import RiskManager, RiskLimits
        from backend.weather.scanner.opportunity import Opportunity

        limits = RiskLimits(max_trade_size=0.5, daily_loss_limit=10000)
        rm = RiskManager(limits=limits)

        opp = Opportunity(
            opportunity_type=OpportunityType.STRATEGY_A,
            series_ticker="KXHIGHNY",
            city_key="nyc",
            city_name="New York",
            target_date=date(2026, 5, 1),
            edge=0.10,
            edge_dollars=0.10,
            total_cost=0.50,
            suggested_size=10,  # Will be cut to 0.5 * 0.25 = 2.5, then max_trade_size = 0.5
        )
        approved, size, reason = rm.approve_opportunity(opp)
        assert not approved
        assert "below minimum" in reason.lower() or "1 contract" in reason