"""End-to-end test of the trading pipeline using mock data.

Validates the full scanner → risk → engine flow without Kalshi API keys.
"""
import pytest
import asyncio
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

from backend.exchange.base import ExchangeClient, OrderResult, OrderSide, OrderType, OrderBook, Position, Balance
from backend.scanner.opportunity import BracketMarket, Opportunity, OpportunityType, OpportunityStatus
from backend.scanner.strategy_b import check_cross_bracket_arb
from backend.core.risk import RiskManager, RiskLimits
from backend.trader import TradingEngine


class MockExchange(ExchangeClient):
    """Mock exchange that returns fake market data and records order calls."""

    def __init__(self):
        self.placed_orders = []
        self.cancelled_orders = []

    async def place_order(self, ticker, side, price, size, order_type=OrderType.LIMIT):
        self.placed_orders.append({
            "ticker": ticker, "side": side, "price": price,
            "size": size, "order_type": order_type,
        })
        return OrderResult(success=True, order_id=f"mock-{len(self.placed_orders)}", filled_size=size, filled_price=price)

    async def cancel_order(self, order_id):
        self.cancelled_orders.append(order_id)
        return True

    async def cancel_all_orders(self, ticker=None):
        return 0

    async def get_positions(self):
        return []

    async def get_balance(self):
        return Balance(total=10000.0, available=8000.0, invested=2000.0)

    async def get_orderbook(self, ticker, depth=10):
        return OrderBook(ticker=ticker, bids=[{"price": 0.08, "size": 100}], asks=[{"price": 0.10, "size": 100}], best_bid=0.08, best_ask=0.10, spread=0.02, mid_price=0.09)

    async def get_market(self, ticker):
        return {"ticker": ticker, "yes_ask": 10, "no_ask": 90}

    async def get_event_markets(self, series_ticker):
        """Return mock markets for NYC high temp — 6 brackets with sum(YES) < 1.0"""
        return [
            {"ticker": "KXHIGHNY-26MAY01-B32.5", "yes_ask": 3, "no_ask": 97, "last_price": 3, "volume": 200, "open_interest": 50},
            {"ticker": "KXHIGHNY-26MAY01-B45.5", "yes_ask": 10, "no_ask": 90, "last_price": 10, "volume": 300, "open_interest": 80},
            {"ticker": "KXHIGHNY-26MAY01-B58.5", "yes_ask": 25, "no_ask": 75, "last_price": 25, "volume": 500, "open_interest": 120},
            {"ticker": "KXHIGHNY-26MAY01-B71.5", "yes_ask": 30, "no_ask": 70, "last_price": 30, "volume": 400, "open_interest": 100},
            {"ticker": "KXHIGHNY-26MAY01-B84.5", "yes_ask": 15, "no_ask": 85, "last_price": 15, "volume": 250, "open_interest": 60},
            {"ticker": "KXHIGHNY-26MAY01-T84.5", "yes_ask": 11, "no_ask": 89, "last_price": 11, "volume": 150, "open_interest": 40},
        ]


class TestTradingEnginePipeline:
    """Test the full scanner → risk → engine pipeline with mock data."""

    @pytest.mark.asyncio
    async def test_strategy_b_scan_with_mock_exchange(self):
        """Strategy B scanner finds arbitrage with mock market data."""
        from backend.scanner.strategy_b import scan_strategy_b

        exchange = MockExchange()
        opportunities = await scan_strategy_b(exchange)

        # With mock data: sum(YES) = 0.03 + 0.10 + 0.25 + 0.30 + 0.15 + 0.11 = 0.94
        # Edge = 1.0 - 0.94 = 0.06 = 6%
        # MockExchange returns same data for all 5 cities, so we get 5 arbs
        assert len(opportunities) == 5  # One per city
        opp = opportunities[0]
        assert opp.opportunity_type == OpportunityType.STRATEGY_B
        assert abs(opp.yes_sum - 0.94) < 0.01
        assert abs(opp.edge - 0.06) < 0.01

    @pytest.mark.asyncio
    async def test_full_cycle_simulation_mode(self):
        """Full cycle in simulation mode — no real orders placed."""
        exchange = MockExchange()
        engine = TradingEngine(exchange=exchange, simulation_mode=True)

        mock_opp = Opportunity(
            opportunity_type=OpportunityType.STRATEGY_B,
            series_ticker="KXHIGHNY",
            city_key="nyc",
            city_name="New York",
            target_date=date(2026, 5, 1),
            edge=0.06,
            edge_dollars=0.06,
            total_cost=0.94,
            suggested_size=1,
            brackets=[
                BracketMarket(ticker="KXHIGHNY-26MAY01-B32.5", yes_price=0.03, no_price=0.97, threshold_f=32.5, direction="above", volume=200),
                BracketMarket(ticker="KXHIGHNY-26MAY01-B45.5", yes_price=0.10, no_price=0.90, threshold_f=45.5, direction="above", volume=300),
                BracketMarket(ticker="KXHIGHNY-26MAY01-B58.5", yes_price=0.25, no_price=0.75, threshold_f=58.5, direction="above", volume=500),
                BracketMarket(ticker="KXHIGHNY-26MAY01-B71.5", yes_price=0.30, no_price=0.70, threshold_f=71.5, direction="above", volume=400),
                BracketMarket(ticker="KXHIGHNY-26MAY01-B84.5", yes_price=0.15, no_price=0.85, threshold_f=84.5, direction="above", volume=250),
                BracketMarket(ticker="KXHIGHNY-26MAY01-T84.5", yes_price=0.11, no_price=0.89, threshold_f=84.5, direction="above", volume=150),
            ],
        )
        # Patch at the module where it's imported in trader.py
        with patch("backend.trader.scan_all", return_value=[mock_opp]):
            results = await engine.run_cycle()

        assert len(results) == 1
        r = results[0]
        assert r["opportunity_type"] == "strategy_b"
        assert r["execution"]["simulated"] is True
        # No real orders placed in sim mode
        assert len(exchange.placed_orders) == 0

    @pytest.mark.asyncio
    async def test_full_cycle_live_mode(self):
        """Full cycle in live mode — orders placed through mock exchange."""
        exchange = MockExchange()
        engine = TradingEngine(exchange=exchange, simulation_mode=False)

        mock_opp = Opportunity(
            opportunity_type=OpportunityType.STRATEGY_B,
            series_ticker="KXHIGHNY",
            city_key="nyc",
            city_name="New York",
            target_date=date(2026, 5, 1),
            edge=0.06,
            edge_dollars=0.06,
            total_cost=0.94,
            suggested_size=1,
            confidence=0.95,
            brackets=[
                BracketMarket(ticker="KXHIGHNY-26MAY01-B32.5", yes_price=0.03, no_price=0.97, threshold_f=32.5, direction="above", volume=200),
                BracketMarket(ticker="KXHIGHNY-26MAY01-B58.5", yes_price=0.25, no_price=0.75, threshold_f=58.5, direction="above", volume=500),
            ],
        )

        with patch("backend.trader.scan_all", return_value=[mock_opp]):
            results = await engine.run_cycle()

        assert len(results) == 1
        # In live mode, orders should be placed on the exchange
        assert len(exchange.placed_orders) == 2  # 2 brackets
        assert exchange.placed_orders[0]["side"] == OrderSide.YES

    def test_risk_manager_kill_switch(self):
        """Kill switch blocks all trading."""
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

    def test_risk_manager_daily_limit(self):
        """Daily loss limit blocks trading."""
        limits = RiskLimits(daily_loss_limit=50.0)
        rm = RiskManager(limits=limits)
        # Simulate a big loss
        rm._daily_stats.realized_pnl = -60.0

        allowed, reason = rm.is_trading_allowed()
        assert not allowed
        assert "Daily loss limit" in reason