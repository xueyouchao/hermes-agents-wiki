"""Exchange abstraction layer for cross-platform trading."""

from backend.common.exchange.base import ExchangeClient, OrderResult

__all__ = ["ExchangeClient", "OrderResult"]
