"""Kalshi exchange client — implements ExchangeClient for Kalshi trade-api/v2.

Builds on backend.data.kalshi_client.KalshiClient for RSA-PSS auth and
HTTP transport, adding order placement, cancellation, positions, and
orderbook queries needed for live trading.
"""
import logging
from typing import Dict, List, Optional

from backend.exchange.base import (
    Balance,
    ExchangeClient,
    OrderBook,
    OrderResult,
    OrderSide,
    OrderType,
    Position,
)
from backend.data.kalshi_client import KalshiClient

logger = logging.getLogger("trading_bot")


class KalshiExchange(ExchangeClient):
    """Kalshi implementation of the ExchangeClient interface.

    Wraps KalshiClient (auth + transport) with order management
    and market data methods required by the trading loop.
    """

    def __init__(self):
        self._client = KalshiClient()
        # Track placed order IDs so we can cancel on abort
        self._pending_orders: Dict[str, str] = {}  # order_id -> ticker

    # ----------------------------------------------------------------
    # Order placement
    # ----------------------------------------------------------------

    async def place_order(
        self,
        ticker: str,
        side: OrderSide,
        price: float,
        size: float,
        order_type: OrderType = OrderType.LIMIT,
    ) -> OrderResult:
        """Place an order on Kalshi.

        Kalshi API: POST /portfolio/orders with JSON body:
        - market_ticker: ticker
        - side: "yes" or "no"
        - limit_price: price in cents (integer 1-99)
        - count: number of contracts
        - order_type: "limit" or "ioc"
        """
        # Convert dollars to cents for Kalshi API
        price_cents = int(round(price * 100))
        if price_cents < 1 or price_cents > 99:
            return OrderResult(success=False, error=f"Invalid price: {price} ({price_cents} cents)")

        # Convert float size to integer contracts
        count = int(size)
        if count < 1:
            return OrderResult(success=False, error=f"Invalid size: {size}")

        # Map our OrderType enum to Kalshi API values
        kalshi_order_type = "ioc" if order_type == OrderType.IOC else "limit"

        payload = {
            "market_ticker": ticker,
            "side": side.value,
            "limit_price": price_cents,
            "count": count,
            "order_type": kalshi_order_type,
        }

        try:
            result = await self._client.post("/portfolio/orders", json=payload)
            order_id = str(result.get("order_id", ""))
            filled_count = result.get("filled_count", 0)
            filled_price_cents = result.get("filled_price", 0)

            if order_id:
                self._pending_orders[order_id] = ticker

            return OrderResult(
                success=True,
                order_id=order_id,
                filled_size=float(filled_count),
                filled_price=filled_price_cents / 100.0,
                remaining_size=float(count - filled_count),
            )
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Kalshi order failed: {ticker} {side.value} {count}@{price_cents}c — {error_msg}")
            return OrderResult(success=False, error=error_msg)

    # ----------------------------------------------------------------
    # Order cancellation
    # ----------------------------------------------------------------

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order on Kalshi.

        DELETE /portfolio/orders/{order_id}
        """
        try:
            await self._client.delete(f"/portfolio/orders/{order_id}")
            self._pending_orders.pop(order_id, None)
            return True
        except Exception as e:
            logger.error(f"Cancel order {order_id} failed: {e}")
            return False

    async def cancel_all_orders(self, ticker: Optional[str] = None) -> int:
        """Cancel all open orders, optionally filtered by ticker."""
        try:
            orders = await self.get_open_orders(ticker)
            cancelled = 0
            for order in orders:
                order_id = str(order.get("id", ""))
                if await self.cancel_order(order_id):
                    cancelled += 1
            return cancelled
        except Exception as e:
            logger.error(f"Cancel all orders failed: {e}")
            return 0

    # ----------------------------------------------------------------
    # Positions and balance
    # ----------------------------------------------------------------

    async def get_positions(self) -> List[Position]:
        """Get all open positions from Kalshi.

        GET /portfolio/settlements
        """
        try:
            data = await self._client.get("/portfolio/settlements")
            positions = []
            for item in data.get("settlements", []):
                ticker = item.get("market_ticker", "")
                if not ticker:
                    continue
                positions.append(Position(
                    ticker=ticker,
                    side=item.get("side", "yes"),
                    size=float(item.get("count", 0)),
                    avg_price=float(item.get("avg_price", 0)) / 100.0,
                    unrealized_pnl=float(item.get("unrealized_pnl", 0)) / 100.0,
                    market_title=item.get("title", ""),
                ))
            return positions
        except Exception as e:
            logger.error(f"Get positions failed: {e}")
            return []

    async def get_balance(self) -> Balance:
        """Get account balance from Kalshi.

        GET /portfolio/balance
        """
        try:
            data = await self._client.get("/portfolio/balance")
            return Balance(
                total=float(data.get("balance", 0)) / 100.0,
                available=float(data.get("available_balance", 0)) / 100.0,
                invested=float(data.get("invested", 0)) / 100.0,
                currency="USD",
            )
        except Exception as e:
            logger.error(f"Get balance failed: {e}")
            return Balance()

    # ----------------------------------------------------------------
    # Market data
    # ----------------------------------------------------------------

    async def get_orderbook(self, ticker: str, depth: int = 10) -> OrderBook:
        """Get order book for a Kalshi market.

        GET /markets/{ticker}/orderbook
        """
        try:
            data = await self._client.get(f"/markets/{ticker}/orderbook", params={"depth": depth})
            bids = data.get("bids", [])
            asks = data.get("asks", [])

            best_bid = max((b.get("price", 0) for b in bids), default=0) / 100.0
            best_ask = min((a.get("price", 0) for a in asks), default=0) / 100.0

            return OrderBook(
                ticker=ticker,
                bids=[{"price": b.get("price", 0) / 100.0, "size": b.get("size", 0)} for b in bids],
                asks=[{"price": a.get("price", 0) / 100.0, "size": a.get("size", 0)} for a in asks],
                best_bid=best_bid,
                best_ask=best_ask,
                spread=best_ask - best_bid if best_bid and best_ask else 0.0,
                mid_price=(best_bid + best_ask) / 2 if best_bid and best_ask else 0.0,
            )
        except Exception as e:
            logger.error(f"Get orderbook for {ticker} failed: {e}")
            return OrderBook(ticker=ticker)

    async def get_market(self, ticker: str) -> dict:
        """Get market details from Kalshi.

        GET /markets/{ticker}
        """
        try:
            return await self._client.get(f"/markets/{ticker}")
        except Exception as e:
            logger.error(f"Get market {ticker} failed: {e}")
            return {}

    async def get_event_markets(self, series_ticker: str) -> List[dict]:
        """Get all markets (brackets) under a series.

        Crucial for Strategy B: fetch all bracket prices to check
        if sum(YES prices) < $1.00 (cross-bracket arbitrage).

        GET /markets?series_ticker=...&status=open
        Handles cursor-based pagination.
        """
        markets = []
        cursor = None

        while True:
            params = {
                "series_ticker": series_ticker,
                "status": "open",
                "limit": 200,
            }
            if cursor:
                params["cursor"] = cursor

            try:
                data = await self._client.get("/markets", params=params)
            except Exception as e:
                logger.error(f"Get event markets for {series_ticker} failed: {e}")
                break

            batch = data.get("markets", [])
            markets.extend(batch)

            cursor = data.get("cursor")
            if not cursor or not batch:
                break

        return markets

    # ----------------------------------------------------------------
    # Helper methods
    # ----------------------------------------------------------------

    async def get_open_orders(self, ticker: Optional[str] = None) -> List[dict]:
        """Get open orders, optionally filtered by ticker."""
        try:
            params = {}
            if ticker:
                params["ticker"] = ticker
            data = await self._client.get("/portfolio/orders", params=params)
            return data.get("orders", [])
        except Exception as e:
            logger.error(f"Get open orders failed: {e}")
            return []