"""Exchange abstraction layer for cross-platform trading."""

from backend.exchange.base import ExchangeClient, OrderResult

__all__ = ["ExchangeClient", "OrderResult"]