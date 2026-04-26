"""Tests for Strategy B — cross-bracket sum arbitrage scanner."""
import pytest
from datetime import date

from backend.scanner.opportunity import BracketMarket, OpportunityType
from backend.scanner.strategy_b import check_cross_bracket_arb, _group_brackets_by_event


def make_bracket(ticker: str, yes_price: float, volume: float = 100.0, threshold: float = 50.0) -> BracketMarket:
    """Helper to create a BracketMarket for testing."""
    return BracketMarket(
        ticker=ticker,
        yes_price=yes_price,
        no_price=1.0 - yes_price,
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
        # sum = 0.82, edge = 0.18
        result = check_cross_bracket_arb(brackets, series_ticker="KXHIGHNY", city_key="nyc")
        assert result is not None
        assert result.opportunity_type == OpportunityType.STRATEGY_B
        assert abs(result.edge - 0.18) < 0.001
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
        """Realistic scenario: 6 brackets with sum=0.94, edge=6%."""
        brackets = [
            make_bracket("KXHIGHNY-26MAY01-B32.5", 0.03, volume=200, threshold=32.5),
            make_bracket("KXHIGHNY-26MAY01-B45.5", 0.10, volume=300, threshold=45.5),
            make_bracket("KXHIGHNY-26MAY01-B58.5", 0.25, volume=500, threshold=58.5),
            make_bracket("KXHIGHNY-26MAY01-B71.5", 0.30, volume=400, threshold=71.5),
            make_bracket("KXHIGHNY-26MAY01-B84.5", 0.15, volume=250, threshold=84.5),
            make_bracket("KXHIGHNY-26MAY01-T84.5", 0.11, volume=150, threshold=84.5),
        ]
        # sum = 0.94, edge = 0.06
        result = check_cross_bracket_arb(brackets, "KXHIGHNY", "nyc")
        assert result is not None
        assert abs(result.edge - 0.06) < 0.001
        assert result.confidence >= 0.9  # High confidence for pure arb


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
        from backend.core.risk import RiskManager, RiskLimits
        from backend.scanner.opportunity import Opportunity

        limits = RiskLimits(daily_loss_limit=300, max_trade_size=100)
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
        )
        approved, size, reason = rm.approve_opportunity(opp)
        assert approved
        assert size >= 1

    def test_reject_when_killed(self):
        """Kill switch should reject all opportunities."""
        from backend.core.risk import RiskManager
        from backend.scanner.opportunity import Opportunity

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