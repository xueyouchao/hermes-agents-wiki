"""Opportunity model — represents a tradeable signal detected by the scanner."""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import List, Optional


class OpportunityType(str, Enum):
    """Which strategy detected this opportunity."""
    STRATEGY_A = "strategy_a"  # Ultra-low bracket (ensemble confirms misprice)
    STRATEGY_B = "strategy_b"  # Cross-bracket sum arbitrage (price-only)
    STRATEGY_C = "strategy_c"  # Ensemble edge (model vs market disagreement)


class OpportunityStatus(str, Enum):
    """Lifecycle status of an opportunity."""
    DETECTED = "detected"        # Just found, not yet validated
    VALIDATED = "validated"      # Edge confirmed, ready to trade
    EXECUTING = "executing"      # Orders being placed
    PARTIAL = "partial"          # Some orders filled, some pending
    COMPLETE = "complete"        # All orders filled
    EXPIRED = "expired"          # Market closed or prices moved
    CANCELLED = "cancelled"      # Risk manager rejected or error


@dataclass
class BracketMarket:
    """A single bracket market within a weather event.

    For Strategy B, we need all brackets for an event together.
    For example, NYC high temp on 2026-03-01:
      KXHIGHNY-26MAR01-B32.5  (≤32.5°F)
      KXHIGHNY-26MAR01-B45.5  (>32.5 and ≤45.5)
      KXHIGHNY-26MAR01-B58.5  (>45.5 and ≤58.5)
      KXHIGHNY-26MAR01-B71.5  (>58.5 and ≤71.5)
      KXHIGHNY-26MAR01-B84.5  (>71.5 and ≤84.5)
      KXHIGHNY-26MAR01-T84.5  (>84.5°F)
    Exactly one resolves YES → all YES prices should sum to ~$1.00
    """
    ticker: str
    yes_price: float          # Market's YES ask price (0.0-1.0)
    no_price: float           # Market's NO ask price (0.0-1.0)
    yes_bid: float = 0.0     # Best bid for YES (for spread calculation)
    no_bid: float = 0.0     # Best bid for NO
    threshold_f: float = 0.0  # Temperature threshold (degrees Fahrenheit)
    direction: str = "above"  # "above" or "below"
    volume: float = 0.0
    open_interest: float = 0.0


@dataclass
class Opportunity:
    """A tradeable opportunity detected by the scanner.

    This is the unified output of all three scanner strategies.
    The risk manager and execution layer operate on Opportunity objects,
    never on raw market data.
    """
    # What: strategy and identification
    opportunity_type: OpportunityType
    series_ticker: str        # e.g., "KXHIGHNY"
    city_key: str             # e.g., "nyc"
    city_name: str            # e.g., "New York"
    target_date: date         # The date the event resolves
    platform: str = "kalshi"

    # Edge and sizing
    edge: float = 0.0         # Expected edge (0.0-1.0), e.g. 0.06 = 6%
    edge_dollars: float = 0.0 # Expected profit in dollars
    total_cost: float = 0.0   # Total capital required (sum of all yes/no prices)
    confidence: float = 0.5   # How confident we are (0-1)
    kelly_fraction: float = 0.0
    suggested_size: float = 0.0

    # Strategy-specific data
    brackets: List[BracketMarket] = field(default_factory=list)
    model_probability: Optional[float] = None  # For strategies A and C
    market_probability: Optional[float] = None   # For strategies A and C
    ensemble_mean: Optional[float] = None        # For strategies A and C
    ensemble_std: Optional[float] = None         # For strategies A and C
    ensemble_members: int = 0

    # Status and metadata
    status: OpportunityStatus = OpportunityStatus.DETECTED
    reasoning: str = ""
    detected_at: datetime = field(default_factory=datetime.utcnow)
    order_ids: List[str] = field(default_factory=list)  # Track placed orders

    @property
    def num_brackets(self) -> int:
        """Number of bracket markets in this opportunity."""
        return len(self.brackets)

    @property
    def yes_sum(self) -> float:
        """Sum of all YES prices across brackets. Should be ~1.00"""
        return sum(b.yes_price for b in self.brackets)

    @property
    def is_actionable(self) -> bool:
        """Whether this opportunity has enough edge to trade."""
        return self.edge > 0 and self.status in (
            OpportunityStatus.DETECTED,
            OpportunityStatus.VALIDATED,
        )