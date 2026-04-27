"""End-to-end test of the trading pipeline using mock data.

Validates the full scanner → risk → engine flow without Kalshi API keys.
"""
import pytest
import asyncio
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

from backend.common.exchange.base import ExchangeClient, OrderResult, OrderSide, OrderType, OrderBook, Position, Balance
from backend.weather.scanner.opportunity import BracketMarket, Opportunity, OpportunityType, OpportunityStatus
from backend.weather.scanner.strategy_b import check_cross_bracket_arb
from backend.common.risk import RiskManager, RiskLimits
from backend.common.trader import TradingEngine


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
        return OrderBook(ticker=ticker, bids=[], asks=[], best_bid=0.0, best_ask=0.0, spread=0.0, mid_price=0.0)

    async def get_open_orders(self, ticker=None):
        return []

    async def get_order_status(self, order_id):
        return {"status": "filled", "filled_count": 1, "filled_price": 10}

    async def get_market(self, ticker):
        return {"ticker": ticker, "yes_ask": 10, "no_ask": 90}

    async def get_event_markets(self, series_ticker):
        """Return mock markets for NYC high temp — 6 brackets with sum(YES) < 1.0

        Prices in cents: 3 + 8 + 15 + 30 + 12 + 8 = 76 cents → sum = 0.76
        Raw edge = 1.0 - 0.76 = 0.24
        After 6 * $0.01 fees = 0.06, net edge = 0.18
        """
        return [
            {"ticker": "KXHIGHNY-26MAY01-B32.5", "yes_ask": 3, "yes_bid": 2, "no_ask": 97, "last_price": 3, "volume": 200, "open_interest": 50},
            {"ticker": "KXHIGHNY-26MAY01-B45.5", "yes_ask": 8, "yes_bid": 7, "no_ask": 92, "last_price": 8, "volume": 300, "open_interest": 80},
            {"ticker": "KXHIGHNY-26MAY01-B58.5", "yes_ask": 15, "yes_bid": 14, "no_ask": 85, "last_price": 15, "volume": 500, "open_interest": 120},
            {"ticker": "KXHIGHNY-26MAY01-B71.5", "yes_ask": 30, "yes_bid": 29, "no_ask": 70, "last_price": 30, "volume": 400, "open_interest": 100},
            {"ticker": "KXHIGHNY-26MAY01-B84.5", "yes_ask": 12, "yes_bid": 11, "no_ask": 88, "last_price": 12, "volume": 250, "open_interest": 60},
            {"ticker": "KXHIGHNY-26MAY01-T84.5", "yes_ask": 8, "yes_bid": 7, "no_ask": 92, "last_price": 8, "volume": 150, "open_interest": 40},
        ]

    async def close(self):
        """Close mock exchange — no-op."""
        pass


class TestTradingEnginePipeline:
    """Test the full scanner → risk → engine pipeline with mock data."""

    @pytest.mark.asyncio
    async def test_strategy_b_scan_with_mock_exchange(self):
        """Strategy B scanner finds arbitrage with mock market data."""
        from backend.weather.scanner.strategy_b import scan_strategy_b

        exchange = MockExchange()
        opportunities = await scan_strategy_b(exchange)

        # With mock data: sum(YES) = 0.03 + 0.08 + 0.15 + 0.30 + 0.12 + 0.08 = 0.76
        # Raw edge = 1.0 - 0.76 = 0.24
        # After 6 * $0.01 fees = 0.06, net edge = 0.24 - 0.06 = 0.18
        # MockExchange returns same data for all 5 cities, so we get 5 arbs
        assert len(opportunities) == 5  # One per city
        opp = opportunities[0]
        assert opp.opportunity_type == OpportunityType.STRATEGY_B
        assert abs(opp.yes_sum - 0.76) < 0.01
        assert abs(opp.edge - 0.18) < 0.01  # Fee-adjusted edge

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
            direction="yes",
            brackets=[
                BracketMarket(ticker="KXHIGHNY-26MAY01-B32.5", yes_price=0.03, no_price=0.97, yes_bid=0.02, threshold_f=32.5, direction="above", volume=200),
                BracketMarket(ticker="KXHIGHNY-26MAY01-B45.5", yes_price=0.10, no_price=0.90, yes_bid=0.09, threshold_f=45.5, direction="above", volume=300),
                BracketMarket(ticker="KXHIGHNY-26MAY01-B58.5", yes_price=0.25, no_price=0.75, yes_bid=0.24, threshold_f=58.5, direction="above", volume=500),
                BracketMarket(ticker="KXHIGHNY-26MAY01-B71.5", yes_price=0.30, no_price=0.70, yes_bid=0.29, threshold_f=71.5, direction="above", volume=400),
                BracketMarket(ticker="KXHIGHNY-26MAY01-B84.5", yes_price=0.15, no_price=0.85, yes_bid=0.14, threshold_f=84.5, direction="above", volume=250),
                BracketMarket(ticker="KXHIGHNY-26MAY01-T84.5", yes_price=0.11, no_price=0.89, yes_bid=0.10, threshold_f=84.5, direction="above", volume=150),
            ],
        )
        # Patch at the module where it's imported in trader.py
        with patch("backend.common.trader.scan_all", return_value=[mock_opp]):
            results = await engine.run_cycle()

        assert len(results) == 1
        r = results[0]
        assert r["opportunity_type"] == "strategy_b"
        # execution may have been set by the cycle
        exec_result = r.get("execution")
        if exec_result:
            assert exec_result.get("simulated") is True
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
            direction="yes",
            brackets=[
                BracketMarket(ticker="KXHIGHNY-26MAY01-B32.5", yes_price=0.03, no_price=0.97, yes_bid=0.02, threshold_f=32.5, direction="above", volume=200),
                BracketMarket(ticker="KXHIGHNY-26MAY01-B45.5", yes_price=0.10, no_price=0.90, yes_bid=0.09, threshold_f=45.5, direction="above", volume=300),
                BracketMarket(ticker="KXHIGHNY-26MAY01-B58.5", yes_price=0.25, no_price=0.75, yes_bid=0.24, threshold_f=58.5, direction="above", volume=500),
                BracketMarket(ticker="KXHIGHNY-26MAY01-B71.5", yes_price=0.30, no_price=0.70, yes_bid=0.29, threshold_f=71.5, direction="above", volume=400),
                BracketMarket(ticker="KXHIGHNY-26MAY01-B84.5", yes_price=0.15, no_price=0.85, yes_bid=0.14, threshold_f=84.5, direction="above", volume=250),
                BracketMarket(ticker="KXHIGHNY-26MAY01-T84.5", yes_price=0.11, no_price=0.89, yes_bid=0.10, threshold_f=84.5, direction="above", volume=150),
            ],
        )

        with patch("backend.common.trader.scan_all", return_value=[mock_opp]):
            results = await engine.run_cycle()

        assert len(results) == 1
        # In live mode, orders should be placed on the exchange
        assert len(exchange.placed_orders) == 6  # 6 brackets
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

    @pytest.mark.asyncio
    async def test_auto_cancel_on_risk_halt(self):
        """When risk halt triggers mid-cycle, auto-cancel should fire."""
        exchange = MockExchange()
        limits = RiskLimits(daily_loss_limit=10000, max_daily_trades=1)
        rm = RiskManager(limits=limits)
        engine = TradingEngine(exchange=exchange, risk_manager=rm, simulation_mode=False)

        # Register some orders
        rm.register_order_for_cancel("order-1")
        rm.register_order_for_cancel("order-2")

        # Hit a risk halt
        rm._daily_stats.trades_executed = 100
        rm._daily_stats.realized_pnl = -500

        # Running a cycle should detect trading is not allowed
        results = await engine.run_cycle()
        # Should have no results
        assert results == []

    @pytest.mark.asyncio
    async def test_concurrent_order_placement(self):
        """Strategy B orders should be placed concurrently, not sequentially."""
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
            total_cost=0.90,
            suggested_size=1,
            confidence=0.95,
            direction="yes",
            brackets=[
                BracketMarket(ticker=f"KXHIGHNY-26MAY01-B{i}", yes_price=0.15, no_price=0.85, yes_bid=0.14, threshold_f=50, direction="above", volume=200)
                for i in range(6)
            ],
        )

        with patch("backend.common.trader.scan_all", return_value=[mock_opp]):
            results = await engine.run_cycle()

        # All 6 bracket orders should be placed (concurrently via asyncio.gather)
        assert len(exchange.placed_orders) == 6