"""Kalshi exchange client — implements ExchangeClient for Kalshi trade-api/v2.

Builds on backend.data.kalshi_client.KalshiClient for RSA-PSS auth and
HTTP transport, adding order placement, cancellation, positions, and
orderbook queries needed for live trading.

Retry strategy:
  - KalshiClient._request_with_retry handles HTTP-level retries (429, 5xx, ConnectError)
  - This layer adds application-level retry on transient order placement failures
    using tenacity, covering cases where the Kalshi API returns an error response
    that indicates a transient condition (e.g., "market temporarily paused").
  - Validation errors (bad price, size) are NOT retried — they fail immediately.
"""
import logging
from typing import Dict, List, Optional

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    before_sleep_log,
)

from backend.common.exchange.base import (
    Balance,
    ExchangeClient,
    ExchangeError,
    OrderBook,
    OrderResult,
    OrderSide,
    OrderType,
    Position,
)
from backend.common.data.kalshi_client import KalshiClient

logger = logging.getLogger("trading_bot")


# ---------------------------------------------------------------------------
# Retry helpers
# ---------------------------------------------------------------------------

class TransientExchangeError(Exception):
    """Raised when an exchange call fails with a transient/retriable error.

    Examples: market temporarily paused, internal server error on order
    placement that slipped through KalshiClient's HTTP retry, etc.
    Non-transient errors (validation, insufficient funds) should NOT raise
    this — they should return OrderResult(success=False) immediately.
    """
    pass


def _is_transient_error(exc: BaseException) -> bool:
    """Return True if the exception indicates a transient failure worth retrying."""
    return isinstance(exc, (TransientExchangeError,))


# Retry decorator for order placement: 3 attempts, exponential backoff 0.5s→2s
_order_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4.0),
    retry=retry_if_exception(_is_transient_error),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)


class KalshiExchange(ExchangeClient):
    """Kalshi implementation of the ExchangeClient interface.

    Wraps KalshiClient (auth + transport) with order management
    and market data methods required by the trading loop.
    """

    def __init__(self):
        self._client = KalshiClient()

    # ----------------------------------------------------------------
    # Order placement (with application-level retry)
    # ----------------------------------------------------------------

    @_order_retry
    async def place_order(
        self,
        ticker: str,
        side: OrderSide,
        price: float,
        size: float,
        order_type: OrderType = OrderType.LIMIT,
    ) -> OrderResult:
        """Place an order on Kalshi with automatic retry on transient failures.

        Kalshi API: POST /portfolio/orders with JSON body:
        - market_ticker: ticker
        - side: "yes" or "no"
        - limit_price: price in cents (integer 1-99)
        - count: number of contracts
        - order_type: "limit" or "ioc"

        Retry policy:
          - TransientExchangeError: retried up to 3 times with backoff
          - Validation errors (bad price, size): fail immediately
          - Other errors: fail immediately (return OrderResult with error)
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
                pass  # Order placed successfully

            return OrderResult(
                success=True,
                order_id=order_id,
                filled_size=float(filled_count),
                filled_price=filled_price_cents / 100.0,
                remaining_size=float(count - filled_count),
            )
        except Exception as e:
            error_msg = str(e)
            # Classify: transient vs permanent
            transient_keywords = [
                "temporarily paused",
                "temporarily unavailable",
                "rate limit",
                "timeout",
                "connection",
                "internal server error",
                "502",
                "503",
                "504",
                "service unavailable",
            ]
            is_transient = any(kw in error_msg.lower() for kw in transient_keywords)

            if is_transient:
                # Raise so tenacity can retry
                logger.warning(
                    f"Transient Kalshi order error: {ticker} {side.value} "
                    f"{count}@{price_cents}c — {error_msg} (will retry)"
                )
                raise TransientExchangeError(
                    f"Transient error placing order {ticker}: {error_msg}"
                ) from e
            else:
                # Permanent error — return failure, don't retry
                logger.error(
                    f"Kalshi order failed (permanent): {ticker} {side.value} "
                    f"{count}@{price_cents}c — {error_msg}"
                )
                return OrderResult(success=False, error=error_msg)

    # ----------------------------------------------------------------
    # Order cancellation (with retry for robustness during rollback)
    # ----------------------------------------------------------------

    @_order_retry
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order on Kalshi with retry on transient failures.

        DELETE /portfolio/orders/{order_id}

        Retry policy:
          - TransientExchangeError: retried up to 3 times
          - "not found" errors: return True (order already cancelled/filled)
          - Other errors: return False after retries exhausted
        """
        try:
            await self._client.delete(f"/portfolio/orders/{order_id}")
            return True
        except Exception as e:
            error_msg = str(e).lower()
            # "not found" means it's already gone — that's OK
            if "not found" in error_msg or "does not exist" in error_msg:
                logger.info(f"Cancel order {order_id}: already gone (not found)")
                return True
            # Transient error — raise for retry
            if any(kw in error_msg for kw in ["timeout", "connection", "502", "503", "504", "service unavailable"]):
                logger.warning(f"Transient cancel error for order {order_id}: {e} (will retry)")
                raise TransientExchangeError(f"Transient error cancelling order {order_id}: {e}") from e
            # Permanent error
            logger.error(f"Cancel order {order_id} failed (permanent): {e}")
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

        Raises ExchangeError on API failure (instead of silently returning []).
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
            raise ExchangeError(f"Failed to get positions: {e}") from e

    async def get_balance(self) -> Balance:
        """Get account balance from Kalshi.

        GET /portfolio/balance

        Raises ExchangeError on API failure (instead of silently returning empty Balance).
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
            raise ExchangeError(f"Failed to get balance: {e}") from e

    # ----------------------------------------------------------------
    # Market data
    # ----------------------------------------------------------------

    async def get_orderbook(self, ticker: str, depth: int = 10) -> OrderBook:
        """Get order book for a Kalshi market.

        GET /markets/{ticker}/orderbook

        Raises ExchangeError on API failure.
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
        except ExchangeError:
            raise  # Re-raise our own errors
        except Exception as e:
            logger.error(f"Get orderbook for {ticker} failed: {e}")
            raise ExchangeError(f"Failed to get orderbook for {ticker}: {e}") from e

    async def get_market(self, ticker: str) -> dict:
        """Get market details from Kalshi.

        GET /markets/{ticker}

        Raises ExchangeError on API failure.
        """
        try:
            return await self._client.get(f"/markets/{ticker}")
        except Exception as e:
            logger.error(f"Get market {ticker} failed: {e}")
            raise ExchangeError(f"Failed to get market {ticker}: {e}") from e

    async def get_event_markets(self, series_ticker: str) -> List[dict]:
        """Get all markets (brackets) under a series.

        Crucial for Strategy B: fetch all bracket prices to check
        if sum(YES prices) < $1.00 (cross-bracket arbitrage).

        GET /markets?series_ticker=...&status=open
        Handles cursor-based pagination.

        Raises ExchangeError if any pagination page fails, rather than
        silently returning a partial bracket set that would break the
        arbitrage guarantee.
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
                if markets:
                    # We already have partial data — this is dangerous.
                    # A partial bracket set could hide brackets that would
                    # break the arbitrage guarantee. Raise instead.
                    raise ExchangeError(
                        f"Partial data for {series_ticker}: {len(markets)} markets "
                        f"fetched before failure ({e}). Cannot safely use "
                        f"partial bracket set for Strategy B."
                    ) from e
                raise ExchangeError(f"Failed to get markets for {series_ticker}: {e}") from e

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
        """Get open orders, optionally filtered by ticker.

        Raises ExchangeError on API failure.
        """
        try:
            params = {}
            if ticker:
                params["ticker"] = ticker
            data = await self._client.get("/portfolio/orders", params=params)
            return data.get("orders", [])
        except Exception as e:
            logger.error(f"Get open orders failed: {e}")
            raise ExchangeError(f"Failed to get open orders: {e}") from e

    async def get_order_status(self, order_id: str) -> Optional[dict]:
        """Get status of a specific order by ID.
        
        GET /portfolio/orders/{order_id}
        
        Returns dict with 'status', 'filled_count', 'filled_price' keys,
        or None if the order is not found.
        """
        try:
            return await self._client.get(f"/portfolio/orders/{order_id}")
        except Exception as e:
            if "not found" in str(e).lower():
                return None
            raise ExchangeError(f"Failed to get order status for {order_id}: {e}") from e

    async def close(self):
        """Close the underlying HTTP client session."""
        await self._client.close()