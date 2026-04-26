"""Strategy B — Cross-Bracket Sum Arbitrage.

The simplest and safest strategy: if the sum of all YES prices across
an event's brackets is less than $1.00, buy YES on every bracket.

Since exactly one bracket MUST resolve YES, we're guaranteed a $1.00
payout regardless of which bracket wins. Profit = $1.00 - total_cost.

No weather model needed. Pure price arbitrage. Near-100% win rate.

Edge cases:
- Use ask prices (what we'd pay to buy), not mid or last
- Skip if any bracket has no ask (0 volume = illiquid)
- Factor in Kalshi fees (currently ~0 per trade for first $100M)
- Handle partial fills: IOC for remaining brackets if first doesn't fill
"""
import logging
from datetime import date
from typing import Dict, List, Optional, Tuple

from backend.config import settings
from backend.data.kalshi_markets import CITY_SERIES, _parse_kalshi_ticker
from backend.exchange.base import ExchangeClient, OrderSide, OrderType
from backend.scanner.opportunity import (
    BracketMarket,
    Opportunity,
    OpportunityStatus,
    OpportunityType,
)

logger = logging.getLogger("trading_bot")

# Minimum edge after fees to make Strategy B worthwhile
# Kalshi fee model: currently $0 for first $100M monthly volume,
# but leave room for future fee changes
MIN_STRATEGY_B_EDGE = 0.02  # 2 cents minimum profit per event

# Minimum volume per bracket to consider it tradeable
MIN_BRACKET_VOLUME = 50.0  # Skip brackets with < $50 volume

# Maximum spread (ask - bid) for a bracket to be considered liquid
MAX_BRACKET_SPREAD = 0.10  # 10 cents max spread


def _extract_bracket_markets(raw_markets: List[dict]) -> List[BracketMarket]:
    """Convert raw Kalshi market data into BracketMarket objects.

    Filters out:
    - Markets with no ask price (0 volume)
    - Markets that are effectively resolved (price > 0.98 or < 0.02)
    - Markets too illiquid to trade
    """
    brackets = []

    for m in raw_markets:
        ticker = m.get("ticker", "")
        parsed = _parse_kalshi_ticker(ticker, "")
        if not parsed:
            continue

        # Get ask prices (what we'd pay)
        yes_ask = (m.get("yes_ask") or 0) / 100.0
        no_ask = (m.get("no_ask") or 0) / 100.0

        # Get bid prices (for spread calculation)
        yes_bid = (m.get("yes_bid") or 0) / 100.0
        no_bid = (m.get("no_bid") or 0) / 100.0

        # Need an ask price to buy
        if yes_ask <= 0:
            yes_ask = (m.get("last_price") or 0) / 100.0
            if yes_ask <= 0:
                continue

        # Skip effectively-resolved brackets
        if yes_ask > 0.98 or yes_ask < 0.02:
            continue

        volume = float(m.get("volume", 0) or 0)
        open_interest = float(m.get("open_interest", 0) or 0)

        # Check spread
        spread = yes_ask - yes_bid if yes_bid > 0 else 0

        brackets.append(BracketMarket(
            ticker=ticker,
            yes_price=yes_ask,
            no_price=no_ask if no_ask > 0 else 1.0 - yes_ask,
            yes_bid=yes_bid,
            no_bid=no_bid,
            threshold_f=parsed["threshold_f"],
            direction=parsed["direction"],
            volume=volume,
            open_interest=open_interest,
        ))

    return brackets


def _group_brackets_by_event(brackets: List[BracketMarket]) -> Dict[str, List[BracketMarket]]:
    """Group bracket markets by their event (series + date).

    E.g., all KXHIGHNY-26MAR01-* brackets go together.
    """
    events: Dict[str, List[BracketMarket]] = {}

    for b in brackets:
        # Extract event key: everything up to the dash before B/T
        # KXHIGHNY-26MAR01-B45.5 → event_key = "KXHIGHNY-26MAR01"
        parts = b.ticker.rsplit("-", 1)
        if len(parts) < 2:
            continue
        event_key = parts[0]

        if event_key not in events:
            events[event_key] = []
        events[event_key].append(b)

    return events


def check_cross_bracket_arb(
    brackets: List[BracketMarket],
    series_ticker: str = "",
    city_key: str = "",
) -> Optional[Opportunity]:
    """Check if a set of brackets for one event has cross-bracket arbitrage.

    This is the core of Strategy B: compute sum(yes_ask) for all brackets.
    If sum < $1.00, we can buy YES on every bracket and guarantee profit.

    Args:
        brackets: All bracket markets for one event (same date, same city)
        series_ticker: The Kalshi series ticker (e.g., "KXHIGHNY")
        city_key: City identifier (e.g., "nyc")

    Returns:
        Opportunity if arbitrage exists, None otherwise
    """
    if len(brackets) < 4:
        # Need at least a few brackets to make this work
        return None

    # Sort by threshold for readability
    brackets.sort(key=lambda b: b.threshold_f)

    # Compute the total cost of buying YES on every bracket
    total_yes_cost = sum(b.yes_price for b in brackets)

    if total_yes_cost >= 1.0:
        # No arbitrage — sum is at or above $1.00
        return None

    # Edge = profit per dollar invested
    edge = 1.0 - total_yes_cost
    edge_dollars = edge  # Per event — $1.00 payout - total_yes_cost cost

    if edge < MIN_STRATEGY_B_EDGE:
        # Edge too small after considering slippage / opportunity cost
        return None

    # Check liquidity: skip if any bracket has dangerously low volume
    for b in brackets:
        if b.volume < MIN_BRACKET_VOLUME and b.yes_price > 0.05:
            # Only flag illiquidity on non-trivial brackets
            # (ultra-cheap brackets naturally have low volume)
            logger.debug(
                f"Skipping arb — bracket {b.ticker} volume ${b.volume:.0f} "
                f"< ${MIN_BRACKET_VOLUME}"
            )
            return None

    # Parse city and date from first bracket
    first_parsed = _parse_kalshi_ticker(brackets[0].ticker, city_key) or {}
    target_date = first_parsed.get("target_date", date.today())

    city_name_map = {
        "nyc": "New York", "chicago": "Chicago", "miami": "Miami",
        "los_angeles": "Los Angeles", "denver": "Denver",
    }

    # Build reasoning
    bracket_lines = []
    for b in brackets:
        bracket_lines.append(f"  {b.ticker}: YES@{b.yes_price:.2f} (vol=${b.volume:.0f})")
    bracket_detail = "\n".join(bracket_lines)

    reasoning = (
        f"STRATEGY B — Cross-bracket arbitrage on {series_ticker}\n"
        f"Sum(YES) = ${total_yes_cost:.4f} < $1.00\n"
        f"Edge = ${edge_dollars:.4f} per event ({edge:.1%})\n"
        f"Brackets ({len(brackets)}):\n{bracket_detail}"
    )

    return Opportunity(
        opportunity_type=OpportunityType.STRATEGY_B,
        series_ticker=series_ticker,
        city_key=city_key,
        city_name=city_name_map.get(city_key, city_key),
        target_date=target_date,
        edge=edge,
        edge_dollars=edge_dollars,
        total_cost=total_yes_cost,
        confidence=0.95,  # Very high confidence — pure arbitrage
        kelly_fraction=1.0,  # Full Kelly on arb (risk is near-zero)
        suggested_size=1,  # Buy 1 contract per bracket (adjusted by risk manager)
        brackets=brackets,
        status=OpportunityStatus.DETECTED,
        reasoning=reasoning,
    )


async def scan_strategy_b(
    exchange: ExchangeClient,
    city_keys: Optional[List[str]] = None,
) -> List[Opportunity]:
    """Scan all Kalshi weather events for Strategy B opportunities.

    For each city's series:
    1. Fetch all open markets (brackets) via exchange.get_event_markets()
    2. Extract and group brackets by event
    3. Check cross-bracket sum for each event
    4. Return all opportunities where sum(YES) < $1.00

    Args:
        exchange: ExchangeClient for API access
        city_keys: Cities to scan (defaults to config)

    Returns:
        List of Strategy B opportunities, sorted by edge (descending)
    """
    cities = city_keys or [c.strip() for c in settings.WEATHER_CITIES.split(",") if c.strip()]
    all_opportunities: List[Opportunity] = []
    today = date.today()

    logger.info("=" * 60)
    logger.info("STRATEGY B SCAN: Cross-bracket sum arbitrage")
    logger.info(f"Cities: {cities}")

    for city_key in cities:
        series = CITY_SERIES.get(city_key)
        if not series:
            continue

        try:
            raw_markets = await exchange.get_event_markets(series)
            logger.info(f"  {city_key} ({series}): {len(raw_markets)} markets fetched")
        except Exception as e:
            logger.warning(f"  {city_key} ({series}): fetch failed — {e}")
            continue

        # Convert to BracketMarket objects
        brackets = _extract_bracket_markets(raw_markets)
        if not brackets:
            continue

        # Filter out past dates
        current_brackets = []
        for b in brackets:
            parsed = _parse_kalshi_ticker(b.ticker, city_key)
            if parsed and parsed["target_date"] >= today:
                current_brackets.append(b)

        # Group by event (same date)
        events = _group_brackets_by_event(current_brackets)

        logger.info(f"  {city_key}: {len(events)} events, {len(current_brackets)} brackets")

        for event_key, event_brackets in events.items():
            opp = check_cross_bracket_arb(event_brackets, series, city_key)
            if opp:
                logger.info(
                    f"  >>> ARB FOUND: {event_key} — "
                    f"sum(YES)={opp.yes_sum:.4f}, edge={opp.edge:.1%}"
                )
                all_opportunities.append(opp)

    # Sort by edge (highest first)
    all_opportunities.sort(key=lambda o: o.edge, reverse=True)

    logger.info(
        f"STRATEGY B SCAN COMPLETE: {len(all_opportunities)} arbitrage opportunities"
    )
    for opp in all_opportunities:
        logger.info(
            f"  {opp.series_ticker} {opp.target_date}: "
            f"edge={opp.edge:.1%}, cost=${opp.total_cost:.4f}"
        )

    return all_opportunities