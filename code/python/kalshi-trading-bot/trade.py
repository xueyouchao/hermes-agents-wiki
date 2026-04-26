#!/usr/bin/env python3
"""Weather Arbitrage Trading Bot — standalone runner.

Usage:
    # Paper trading (simulation mode, no API keys needed)
    python trade.py --sim

    # Live trading (needs Kalshi API key + RSA key)
    python trade.py --live

    # Single scan cycle (no scheduler, just run once)
    python trade.py --once

    # Strategy B only (fast scan, no weather model)
    python trade.py --once --strategy-b

    # Check positions and balance
    python trade.py --status
"""
import argparse
import asyncio
import json
import logging
import signal
import sys

# Set up logging before importing backend modules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("trading_bot")


def parse_args():
    parser = argparse.ArgumentParser(description="Weather Arbitrage Trading Bot")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--sim", action="store_true", default=True,
                       help="Run in simulation/paper trading mode (default)")
    mode.add_argument("--live", action="store_true",
                       help="Run in live trading mode (REAL MONEY)")
    parser.add_argument("--once", action="store_true",
                        help="Run a single scan cycle, then exit")
    parser.add_argument("--strategy-b", action="store_true",
                        help="Only run Strategy B (cross-bracket arb)")
    parser.add_argument("--status", action="store_true",
                        help="Check positions and balance, then exit")
    parser.add_argument("--cities", type=str, default=None,
                        help="Comma-separated city keys (default: from config)")
    return parser.parse_args()


async def run_once(simulation: bool, strategy_b_only: bool, cities: str = None):
    """Run a single scan cycle and print results."""
    from backend.common.trader import TradingEngine
    from backend.common.exchange.kalshi import KalshiExchange

    engine = TradingEngine(
        exchange=KalshiExchange(),
        simulation_mode=simulation,
    )

    if strategy_b_only:
        from backend.weather.scanner.strategy_b import scan_strategy_b
        logger.info("Running Strategy B scan only...")
        opportunities = await scan_strategy_b(engine.exchange)
        print(f"\n{'='*60}")
        print(f"STRATEGY B RESULTS: {len(opportunities)} arbitrage opportunities")
        print(f"{'='*60}")
        for opp in opportunities:
            print(f"\n  {opp.series_ticker} {opp.target_date}")
            print(f"  Edge: {opp.edge:.1%} (${opp.edge_dollars:.4f} per event)")
            print(f"  Cost: ${opp.total_cost:.4f} (sum of all YES)")
            print(f"  Brackets: {opp.num_brackets}")
            for b in opp.brackets:
                print(f"    {b.ticker}: YES@{b.yes_price:.2f} vol=${b.volume:.0f}")
        print()
        return

    results = await engine.run_cycle()

    print(f"\n{'='*60}")
    print(f"SCAN RESULTS: {len(results)} opportunities")
    print(f"{'='*60}")
    for r in results:
        status_icon = {
            "validated": "[APPROVED]",
            "complete": "[EXECUTED]",
            "partial": "[PARTIAL]",
            "cancelled": "[REJECTED]",
            "detected": "[DETECTED]",
        }.get(r.get("status", ""), "[???]")
        print(
            f"  {status_icon} {r.get('opportunity_type','')} "
            f"{r.get('series_ticker','')} {r.get('target_date','')} "
            f"edge={r.get('edge',0):.1%}"
        )
    print()


async def run_status():
    """Check positions and balance on Kalshi."""
    from backend.common.exchange.kalshi import KalshiExchange

    exchange = KalshiExchange()

    try:
        balance = await exchange.get_balance()
        print(f"\n  Balance: ${balance.available:.2f} available / ${balance.total:.2f} total")
    except Exception as e:
        print(f"\n  Balance: FAILED ({e})")
        print("  (Make sure KALSHI_API_KEY_ID and KALSHI_PRIVATE_KEY_PATH are set)")
        return

    try:
        positions = await exchange.get_positions()
        print(f"  Open positions: {len(positions)}")
        for p in positions:
            print(f"    {p.ticker}: {p.side} {p.size} @ {p.avg_price:.2f}")
    except Exception as e:
        print(f"  Positions: FAILED ({e})")

    print()


async def run_scheduled(simulation: bool):
    """Start the scheduler and run indefinitely."""
    from backend.weather.core.weather_scheduler import start_scheduler, stop_scheduler, log_event

    # Override simulation mode in settings for scheduler
    if simulation:
        # Settings are already set from .env, but let's be explicit
        from backend.common.config import settings
        settings.SIMULATION_MODE = True
    else:
        from backend.common.config import settings
        settings.SIMULATION_MODE = False
        logger.warning("!!! LIVE TRADING MODE — REAL MONEY AT RISK !!!")

    logger.info("Starting weather arbitrage bot...")
    logger.info(f"Mode: {'SIMULATION' if simulation else 'LIVE'}")

    start_scheduler()

    mode = "SIMULATION" if simulation else "LIVE"
    print(f"\n{'='*60}")
    print(f"  WEATHER ARBITRAGE TRADING BOT")
    print(f"  Mode: {mode}")
    print(f"  Ctrl+C to stop")
    print(f"{'='*60}\n")

    # Keep running until interrupted
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
        stop_scheduler()


def main():
    args = parse_args()

    if args.status:
        asyncio.run(run_status())
        return

    simulation = not args.live

    if args.once:
        asyncio.run(run_once(simulation, args.strategy_b, args.cities))
    else:
        asyncio.run(run_scheduled(simulation))


if __name__ == "__main__":
    main()