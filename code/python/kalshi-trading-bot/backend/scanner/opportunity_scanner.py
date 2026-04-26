"""Unified scanner — dispatches strategies A, B, and C in a single pass.

Single process, asyncio event loop. APScheduler calls scan_all() every
2-5 minutes depending on strategy priority:
  - Strategy B: every 2 min (highest priority, pure price arb)
  - Strategy A + C: every 5 min (needs ensemble fetch)
"""
import logging
from typing import List

from backend.config import settings
from backend.exchange.base import ExchangeClient
from backend.exchange.kalshi import KalshiExchange
from backend.scanner.opportunity import Opportunity, OpportunityType

logger = logging.getLogger("trading_bot")


async def scan_strategy_b(exchange: ExchangeClient = None) -> List[Opportunity]:
    """Run Strategy B scanner (cross-bracket sum arbitrage).

    Pure price check — no weather data needed.
    """
    from backend.scanner.strategy_b import scan_strategy_b as _scan_b

    if exchange is None:
        exchange = KalshiExchange()

    return await _scan_b(exchange)


async def scan_strategy_a(exchange: ExchangeClient = None) -> List[Opportunity]:
    """Run Strategy A scanner (ultra-low bracket with ensemble support).

    Needs ensemble forecast data — slower, less frequent.
    """
    # Strategy A is Phase 2 — stub for now
    logger.info("Strategy A scan: not yet implemented (Phase 2)")
    return []


async def scan_strategy_c(exchange: ExchangeClient = None) -> List[Opportunity]:
    """Run Strategy C scanner (ensemble edge — model vs market disagreement).

    Needs ensemble forecast data — slower, less frequent.
    """
    # Strategy C is Phase 2 — uses existing weather_signals.py
    logger.info("Strategy C scan: not yet implemented (Phase 2)")
    return []


async def scan_all(exchange: ExchangeClient = None) -> List[Opportunity]:
    """Run all scanner strategies and aggregate opportunities.

    Called by APScheduler every 2-5 minutes.

    Returns:
        All opportunities sorted by edge (descending)
    """
    if exchange is None:
        exchange = KalshiExchange()

    all_opps: List[Opportunity] = []

    # Strategy B: always run (fast, no weather needed)
    try:
        b_opps = await scan_strategy_b(exchange)
        all_opps.extend(b_opps)
    except Exception as e:
        logger.error(f"Strategy B scan failed: {e}", exc_info=True)

    # Strategy A: Phase 2
    try:
        a_opps = await scan_strategy_a(exchange)
        all_opps.extend(a_opps)
    except Exception as e:
        logger.error(f"Strategy A scan failed: {e}", exc_info=True)

    # Strategy C: Phase 2
    try:
        c_opps = await scan_strategy_c(exchange)
        all_opps.extend(c_opps)
    except Exception as e:
        logger.error(f"Strategy C scan failed: {e}", exc_info=True)

    # Sort by edge (highest first)
    all_opps.sort(key=lambda o: o.edge, reverse=True)

    logger.info(f"SCAN ALL COMPLETE: {len(all_opps)} opportunities")
    for opp in all_opps:
        logger.info(
            f"  [{opp.opportunity_type.value}] {opp.series_ticker} "
            f"{opp.target_date}: edge={opp.edge:.1%}"
        )

    return all_opps