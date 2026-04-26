"""Abstract base class for exchange clients.

All exchange implementations (Kalshi, Polymarket, etc.) must implement
this interface. Strategy code only depends on ExchangeClient, never
on platform-specific details.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class OrderSide(str, Enum):
    YES = "yes"
    NO = "no"


class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"
    IOC = "ioc"  # Immediate-or-cancel (limit that cancels unfilled portion)


@dataclass
class OrderResult:
    """Result of placing an order on an exchange."""
    success: bool
    order_id: str = ""
    filled_size: float = 0.0
    filled_price: float = 0.0
    remaining_size: float = 0.0
    error: str = ""


@dataclass
class Position:
    """An open position on an exchange."""
    ticker: str
    side: str           # "yes" or "no"
    size: float                  # number of contracts
    avg_price: float             # average entry price (0.0-1.0)
    unrealized_pnl: float = 0.0
    market_title: str = ""


@dataclass
class OrderBook:
    """Snapshot of an order book for a single market."""
    ticker: str
    bids: List[Dict] = field(default_factory=list)  # [{price, size}, ...]
    asks: List[Dict] = field(default_factory=list)
    best_bid: float = 0.0
    best_ask: float = 0.0
    spread: float = 0.0
    mid_price: float = 0.0


@dataclass
class Balance:
    """Account balance on an exchange."""
    total: float = 0.0
    available: float = 0.0
    invested: float = 0.0
    currency: str = "USD"


class ExchangeClient(ABC):
    """Abstract interface for a prediction market exchange.

    Strategy code calls ExchangeClient methods only — never platform
    APIs directly. This lets us swap Kalshi for Polymarket or add
    cross-platform arbitrage without touching strategy logic.
    """

    @abstractmethod
    async def place_order(
        self,
        ticker: str,
        side: OrderSide,
        price: float,
        size: float,
        order_type: OrderType = OrderType.LIMIT,
    ) -> OrderResult:
        """Place an order on the exchange.

        Args:
            ticker: Market ticker (e.g. "KXHIGHNY-26MAR01-B45.5")
            side: YES or NO
            price: Limit price (0.01 to 0.99, in dollars)
            size: Number of contracts
            order_type: limit, market, or ioc

        Returns:
            OrderResult with fill details or error message
        """
        ...

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order. Returns True if successful."""
        ...

    @abstractmethod
    async def cancel_all_orders(self, ticker: Optional[str] = None) -> int:
        """Cancel all open orders, optionally filtered by ticker.
        Returns count of cancelled orders."""
        ...

    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """Get all open positions."""
        ...

    @abstractmethod
    async def get_balance(self) -> Balance:
        """Get account balance."""
        ...

    @abstractmethod
    async def get_orderbook(self, ticker: str, depth: int = 10) -> OrderBook:
        """Get order book for a market."""
        ...

    @abstractmethod
    async def get_market(self, ticker: str) -> dict:
        """Get market details (prices, volume, status)."""
        ...

    @abstractmethod
    async def get_event_markets(self, series_ticker: str) -> List[dict]:
        """Get all markets (brackets) under a series/event.
        This is crucial for Strategy B — fetching all brackets
        for a weather event to check if sum(YES prices) < $1.00.
        """
        ...

    @abstractmethod
    async def close(self):
        """Close the exchange client and release resources (HTTP sessions, etc)."""
        ...