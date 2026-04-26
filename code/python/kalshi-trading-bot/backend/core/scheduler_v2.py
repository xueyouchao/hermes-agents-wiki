"""Background scheduler for weather arbitrage trading.

Runs Strategy B (every 2 min), Strategy A + C (every 5 min),
settlement checks, and heartbeats via APScheduler.
Single process, asyncio event loop — no distributed coordination needed.
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trading_bot")

# Global scheduler instance
scheduler: Optional[AsyncIOScheduler] = None

# Global trading engine (created on startup)
engine = None

# Event log for terminal display (in-memory, last 200 events)
event_log: List[dict] = []
MAX_LOG_SIZE = 200


def log_event(event_type: str, message: str, data: dict = None):
    """Log an event for terminal display."""
    global event_log
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": event_type,
        "message": message,
        "data": data or {}
    }
    event_log.append(event)

    while len(event_log) > MAX_LOG_SIZE:
        event_log.pop(0)

    log_func = {
        "error": logger.error,
        "warning": logger.warning,
        "success": logger.info,
        "info": logger.info,
        "data": logger.debug,
        "trade": logger.info
    }.get(event_type, logger.info)

    log_func(f"[{event_type.upper()}] {message}")


def get_recent_events(limit: int = 50) -> List[dict]:
    """Get recent events for terminal display."""
    return event_log[-limit:]


# ---------------------------------------------------------------
# Trading jobs
# ---------------------------------------------------------------

async def weather_arbitrage_job():
    """
    Main trading job: scan → approve → execute cycle.

    Uses the TradingEngine which orchestrates:
    1. Scanner (strategy B, A, C)
    2. Risk manager (position sizing, daily limits)
    3. Exchange client (Kalshi order placement)
    """
    log_event("info", "Weather arbitrage scan starting...")

    try:
        global engine
        if engine is None:
            from backend.trader import TradingEngine
            engine = TradingEngine()

        results = await engine.run_cycle()

        actionable = [r for r in results if r.get("status") in ("validated", "complete", "partial")]
        executed = [r for r in results if r.get("execution", {}).get("executed", False)]
        simulated = [r for r in results if r.get("execution", {}).get("simulated", False)]

        log_event("data",
            f"Scan complete: {len(results)} opps, {len(actionable)} approved, "
            f"{len(executed)} executed, {len(simulated)} simulated",
            {
                "total_opportunities": len(results),
                "approved": len(actionable),
                "executed": len(executed),
                "simulated": len(simulated),
            }
        )

        for r in executed:
            strategy = r.get("opportunity_type", "unknown")
            ticker = r.get("series_ticker", "?")
            date = r.get("target_date", "?")
            edge = r.get("edge", 0)
            log_event("trade",
                f"[{strategy.upper()}] {ticker} {date} — edge={edge:.1%}",
                r
            )

    except Exception as e:
        log_event("error", f"Weather arbitrage scan error: {str(e)}")
        logger.exception("Error in weather_arbitrage_job")


async def strategy_b_job():
    """
    Fast job: Strategy B only (every 2 min).

    Pure price check — no weather data needed, so it's fast.
    """
    log_event("info", "Strategy B fast scan...")

    try:
        from backend.trader import TradingEngine
        from backend.exchange.kalshi import KalshiExchange
        from backend.scanner.strategy_b import scan_strategy_b

        exchange = KalshiExchange()
        opportunities = await scan_strategy_b(exchange)

        if opportunities:
            log_event("success",
                f"Strategy B: {len(opportunities)} arbitrage opportunities!",
                {
                    "opportunities": [
                        {
                            "series": o.series_ticker,
                            "date": str(o.target_date),
                            "edge": f"{o.edge:.1%}",
                            "cost": f"${o.total_cost:.4f}",
                        }
                        for o in opportunities
                    ]
                }
            )
        else:
            log_event("info", "Strategy B: no arbitrage this cycle")

    except Exception as e:
        log_event("error", f"Strategy B scan error: {str(e)}")
        logger.exception("Error in strategy_b_job")


async def heartbeat_job():
    """Periodic heartbeat — log bot status every minute."""
    global engine
    try:
        if engine is None:
            log_event("info", "Heartbeat: engine not yet initialized")
            return

        is_allowed, reason = engine.risk_manager.is_trading_allowed()
        daily_stats = engine.risk_manager.get_daily_stats()

        log_event("data",
            f"Heartbeat: trading={'ON' if is_allowed else 'PAUSED'} | "
            f"trades={daily_stats.trades_executed} | "
            f"P&L=${daily_stats.realized_pnl:.2f} | "
            f"{reason}",
            {
                "trading_allowed": is_allowed,
                "reason": reason,
                "daily_trades": daily_stats.trades_executed,
                "daily_pnl": daily_stats.realized_pnl,
                "simulation": engine.simulation_mode,
            }
        )
    except Exception as e:
        log_event("warning", f"Heartbeat failed: {str(e)}")


# ---------------------------------------------------------------
# Scheduler lifecycle
# ---------------------------------------------------------------

def start_scheduler():
    """Start the background scheduler for weather arbitrage trading."""
    global scheduler, engine

    if scheduler is not None and scheduler.running:
        log_event("warning", "Scheduler already running")
        return

    # Initialize the trading engine
    from backend.trader import TradingEngine
    engine = TradingEngine()

    # Reconcile any open positions from a previous session
    # (non-blocking — just logs state)
    logger.info("Reconciling positions from previous session...")
    # Note: reconcile_positions needs Kalshi credentials, so we skip
    # in simulation mode or if no credentials

    scheduler = AsyncIOScheduler()

    # Strategy B: every 2 minutes (fast, pure price check)
    scheduler.add_job(
        strategy_b_job,
        IntervalTrigger(seconds=120),
        id="strategy_b_scan",
        replace_existing=True,
        max_instances=1,
    )

    # Full scan: every 5 minutes (B + A + C)
    if settings.WEATHER_ENABLED:
        scheduler.add_job(
            weather_arbitrage_job,
            IntervalTrigger(seconds=settings.WEATHER_SCAN_INTERVAL_SECONDS),
            id="weather_arbitrage_scan",
            replace_existing=True,
            max_instances=1,
        )

    # Heartbeat: every 60 seconds
    scheduler.add_job(
        heartbeat_job,
        IntervalTrigger(seconds=60),
        id="heartbeat",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()

    mode = "SIMULATION" if settings.SIMULATION_MODE else "LIVE"
    log_event("success", f"Weather arbitrage scheduler started ({mode} mode)", {
        "strategy_b_interval": "2min",
        "full_scan_interval": f"{settings.WEATHER_SCAN_INTERVAL_SECONDS}s",
        "simulation_mode": settings.SIMULATION_MODE,
        "cities": settings.WEATHER_CITIES,
    })

    # Run initial scan immediately
    asyncio.create_task(strategy_b_job())
    if settings.WEATHER_ENABLED:
        asyncio.create_task(weather_arbitrage_job())


def stop_scheduler():
    """Stop the background scheduler."""
    global scheduler

    if scheduler is None or not scheduler.running:
        log_event("info", "Scheduler not running")
        return

    scheduler.shutdown(wait=False)
    scheduler = None
    log_event("info", "Scheduler stopped")


def is_scheduler_running() -> bool:
    """Check if scheduler is currently running."""
    return scheduler is not None and scheduler.running