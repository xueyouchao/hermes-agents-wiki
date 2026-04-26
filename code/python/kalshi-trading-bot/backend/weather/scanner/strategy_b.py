"""Strategy B — Cross-Bracket Sum Arbitrage.

The simplest and safest strategy: if the sum of all YES prices across
an event's brackets is less than $1.00, buy YES on every bracket.

Since exactly one bracket MUST resolve YES, we're guaranteed a $1.00
payout regardless of which bracket wins. Profit = $1.00 - total_cost.

No weather model needed. Pure price arbitrage. Near-100% win rate.

Improvements (v2):
- Uses ask prices (what we'd pay to buy), never mid or last
- Factors in Kalshi fees (configurable, currently 0)
- Tracks skip_reasons for every filtered-out market
- Calculates exact ROI and net profit
- Enforces min profit threshold after fees
- Filters by volume, spread, and liquidity
"""
import logging
from datetime import date
from typing import Dict, List, Optional, Tuple

from backend.common.config import settings
from backend.common.data.kalshi_markets import CITY_SERIES, _parse_kalshi_ticker
from backend.common.exchange.base import ExchangeClient, OrderSide, OrderType
from backend.weather.scanner.opportunity import (
    BracketMarket,
    Opportunity,
    OpportunityStatus,
    OpportunityType,
)

logger = logging.getLogger("trading_bot")

# Configurable thresholds (override via settings if needed)
MIN_STRATEGY_B_EDGE = 0.02       # 2 cents minimum profit per event after fees
MIN_BRACKET_VOLUME = 50.0       # Skip brackets with < $50 volume
MAX_BRACKET_SPREAD = 0.10       # 10 cents max spread
MIN_MARKET_VOLUME = 1000.0      # Skip markets with < $1000 total volume (from risk.py)

# Parse cities once at module level (avoid re-splitting every scan)
_CACHED_CITIES: Optional[List[str]] = None


def _get_cities() -> List[str]:
    """Get and cache the city list from settings."""
    global _CACHED_CITIES
    if _CACHED_CITIES is None:
        _CACHED_CITIES = [c.strip() for c in settings.WEATHER_CITIES.split(",") if c.strip()]
    return _CACHED_CITIES


def _extract_bracket_markets(
    raw_markets: List[dict],
    skip_reasons: Optional[List[str]] = None,
) -> List[BracketMarket]:
    """Convert raw Kalshi market data into BracketMarket objects.

    Uses ASK prices (what we'd pay), never mid or last.
    Filters out:
    - Markets with no ask price (0 volume)
    - Markets that are effectively resolved (price > 0.98 or < 0.02)
    - Markets that are too illiquid to trade

    Tracks skip_reasons for every filtered market.
    """
    if skip_reasons is None:
        skip_reasons = []

    brackets = []

    for m in raw_markets:
        ticker = m.get("ticker", "")
        parsed = _parse_kalshi_ticker(ticker, "")
        if not parsed:
            skip_reasons.append(f"Unparseable ticker: {ticker}")
            continue

        # Get ask prices (what we'd pay to BUY)
        # Kalshi API returns prices in cents (integer)
        yes_ask = (m.get("yes_ask") or 0) / 100.0
        no_ask = (m.get("no_ask") or 0) / 100.0

        # Get bid prices (for spread calculation)
        yes_bid = (m.get("yes_bid") or 0) / 100.0
        no_bid = (m.get("no_bid") or 0) / 100.0

        # Need an ask price to buy — NEVER fall back to last_price
        if yes_ask <= 0:
            skip_reasons.append(f"No ask price: {ticker}")
            continue

        # Skip effectively-resolved brackets
        if yes_ask > 0.98:
            skip_reasons.append(f"Near-certain YES: {ticker} ask={yes_ask:.2f}")
            continue
        if yes_ask < 0.02:
            skip_reasons.append(f"Near-certain NO: {ticker} ask={yes_ask:.2f}")
            continue

        volume = float(m.get("volume", 0) or 0)
        open_interest = float(m.get("open_interest", 0) or 0)

        # Check spread
        spread = yes_ask - yes_bid if yes_bid > 0 else 0
        if spread > MAX_BRACKET_SPREAD:
            skip_reasons.append(f"Spread too wide: {ticker} spread={spread:.2f}")
            continue

        brackets.append(BracketMarket(
            ticker=ticker,
            yes_price=yes_ask,       # Always use ask price for Strategy B
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
    skip_reasons: Optional[List[str]] = None,
) -> Optional[Opportunity]:
    """Check if a set of brackets for one event has cross-bracket arbitrage.

    This is the core of Strategy B: compute sum(yes_ask) for all brackets.
    If sum < $1.00, we can buy YES on every bracket and guarantee profit.

    Args:
        brackets: All bracket markets for one event (same date, same city)
        series_ticker: The Kalshi series ticker (e.g., "KXHIGHNY")
        city_key: City identifier (e.g., "nyc")
        skip_reasons: Shared list for tracking why markets were skipped

    Returns:
        Opportunity if arbitrage exists, None otherwise
    """
    if skip_reasons is None:
        skip_reasons = []

    if len(brackets) < 4:
        skip_reasons.append(
            f"Too few brackets for {series_ticker}: {len(brackets)} < 4"
        )
        return None

    # Sort by threshold for readability
    brackets.sort(key=lambda b: b.threshold_f)

    # Compute the total cost of buying YES on every bracket (using ASK prices)
    total_yes_cost = sum(b.yes_price for b in brackets)

    if total_yes_cost >= 1.0:
        # No arbitrage — sum is at or above $1.00
        return None

    # Edge = profit per dollar invested (before fees)
    edge = 1.0 - total_yes_cost

    # Subtract Kalshi fees
    fee_per_contract = getattr(settings, 'KALSHI_FEE_RATE', 0.0)
    total_fees = len(brackets) * fee_per_contract
    edge_after_fees = edge - total_fees

    if edge_after_fees < MIN_STRATEGY_B_EDGE:
        skip_reasons.append(
            f"Edge after fees too small: {edge_after_fees:.4f} < {MIN_STRATEGY_B_EDGE}"
        )
        return None

    # Check liquidity: skip if any bracket has dangerously low volume
    for b in brackets:
        if b.volume < MIN_BRACKET_VOLUME and b.yes_price > 0.05:
            skip_reasons.append(
                f"Low volume bracket: {b.ticker} vol=${b.volume:.0f}"
            )
            return None

    # Calculate ROI
    roi_pct = (edge_after_fees / total_yes_cost) * 100.0 if total_yes_cost > 0 else 0.0

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
        spread = b.yes_price - b.yes_bid if b.yes_bid > 0 else 0
        bracket_lines.append(
            f"  {b.ticker}: YES@{b.yes_price:.2f} "
            f"(bid={b.yes_bid:.2f}, spread={spread:.2f}, vol=${b.volume:.0f})"
        )
    bracket_detail = "\n".join(bracket_lines)

    reasoning = (
        f"STRATEGY B — Cross-bracket arbitrage on {series_ticker}\n"
        f"Sum(YES ask) = ${total_yes_cost:.4f} < $1.00\n"
        f"Gross edge = ${edge:.4f} ({edge:.1%})\n"
        f"Fees = ${total_fees:.4f}\n"
        f"Net edge = ${edge_after_fees:.4f} ({edge_after_fees:.1%})\n"
        f"ROI = {roi_pct:.1f}%\n"
        f"Brackets ({len(brackets)}):\n{bracket_detail}"
    )

    return Opportunity(
        opportunity_type=OpportunityType.STRATEGY_B,
        series_ticker=series_ticker,
        city_key=city_key,
        city_name=city_name_map.get(city_key, city_key),
        target_date=target_date,
        edge=edge_after_fees,     # Use fee-adjusted edge
        edge_dollars=edge_after_fees,
        total_cost=total_yes_cost,
        confidence=0.95,          # Very high confidence — pure arbitrage
        kelly_fraction=1.0,       # Full Kelly on arb (risk is near-zero)
        suggested_size=1,         # Buy 1 contract per bracket (adjusted by risk manager)
        direction="yes",          # Strategy B always buys YES
        brackets=brackets,
        status=OpportunityStatus.DETECTED,
        reasoning=reasoning,
        skip_reasons=skip_reasons,
        markets_scanned=len(brackets),
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
        city_keys: Cities to scan (defaults to config, cached)

    Returns:
        List of Strategy B opportunities, sorted by edge (descending)
    """
    cities = city_keys or _get_cities()
    all_opportunities: List[Opportunity] = []
    today = date.today()
    total_skip_reasons: List[str] = []

    logger.info("=" * 60)
    logger.info("STRATEGY B SCAN: Cross-bracket sum arbitrage")
    logger.info(f"Cities: {cities}")

    for city_key in cities:
        series = CITY_SERIES.get(city_key)
        if not series:
            continue

        city_skip_reasons: List[str] = []

        try:
            raw_markets = await exchange.get_event_markets(series)
            logger.info(f"  {city_key} ({series}): {len(raw_markets)} markets fetched")
        except Exception as e:
            logger.warning(f"  {city_key} ({series}): fetch failed — {e}")
            city_skip_reasons.append(f"API error for {series}: {e}")
            total_skip_reasons.extend(city_skip_reasons)
            continue

        # Convert to BracketMarket objects (uses ask prices)
        brackets = _extract_bracket_markets(raw_markets, city_skip_reasons)
        if not brackets:
            logger.info(f"  {city_key}: no valid brackets after filtering")
            total_skip_reasons.extend(city_skip_reasons)
            continue

        # Filter out past dates
        current_brackets = []
        stale_count = 0
        for b in brackets:
            parsed = _parse_kalshi_ticker(b.ticker, city_key)
            if parsed and parsed["target_date"] >= today:
                current_brackets.append(b)
            else:
                stale_count += 1
        if stale_count > 0:
            city_skip_reasons.append(f"{stale_count} past-date brackets filtered")

        # Group by event (same date)
        events = _group_brackets_by_event(current_brackets)

        logger.info(
            f"  {city_key}: {len(events)} events, {len(current_brackets)} brackets "
            f"({len(city_skip_reasons)} skips)"
        )

        for event_key, event_brackets in events.items():
            opp = check_cross_bracket_arb(
                event_brackets, series, city_key, city_skip_reasons
            )
            if opp:
                logger.info(
                    f"  >>> ARB FOUND: {event_key} — "
                    f"sum(YES)={opp.yes_sum:.4f}, edge={opp.edge:.1%}, "
                    f"ROI={opp.roi_pct:.1f}%"
                )
                all_opportunities.append(opp)

        total_skip_reasons.extend(city_skip_reasons)

    # Sort by edge (highest first)
    all_opportunities.sort(key=lambda o: o.edge, reverse=True)

    logger.info(
        f"STRATEGY B SCAN COMPLETE: {len(all_opportunities)} arbitrage opportunities"
    )
    for opp in all_opportunities:
        logger.info(
            f"  {opp.series_ticker} {opp.target_date}: "
            f"edge={opp.edge:.1%}, cost=${opp.total_cost:.4f}, "
            f"ROI={opp.roi_pct:.1f}%"
        )

    if total_skip_reasons:
        # Log skip summary at debug level to avoid noise
        from collections import Counter
        skip_counts = Counter(total_skip_reasons)
        logger.debug(
            f"Skip summary: {dict(skip_counts.most_common(10))}"
        )

    return all_opportunities