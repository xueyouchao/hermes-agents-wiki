"""Weather arbitrage scheduler — runs Strategy B (every 2 min), A+C (every 5 min),

Runs Strategy B (every 2 min), Strategy A + C (every 5 min),
settlement checks, and heartbeats via APScheduler.
Single process, asyncio event loop — no distributed coordination needed.
"""
import asyncio
import logging
from collections import deque
from datetime import datetime, timezone
from typing import List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.common.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trading_bot")

# Global scheduler instance
scheduler: Optional[AsyncIOScheduler] = None

# Global trading engine (created on startup)
engine = None

# Event log for terminal display (in-memory, last 200 events)
event_log = deque(maxlen=200)


def log_event(event_type: str, message: str, data: dict = None):
    """Log an event for terminal display."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": event_type,
        "message": message,
        "data": data or {}
    }
    event_log.append(event)

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
    return list(event_log)[-limit:]


# ---------------------------------------------------------------
# Trading jobs
# ---------------------------------------------------------------

# Lock to prevent Strategy B running concurrently from both jobs.
# Lazy-initialized: asyncio.Lock() must be created inside a running event loop,
# so we defer creation until first use.
_strategy_b_lock: Optional[asyncio.Lock] = None


def _get_strategy_b_lock() -> asyncio.Lock:
    """Get or lazily create the Strategy B lock."""
    global _strategy_b_lock
    if _strategy_b_lock is None:
        _strategy_b_lock = asyncio.Lock()
    return _strategy_b_lock


async def weather_arbitrage_job():
    """
    Main trading job: scan → approve → execute cycle.

    Uses the TradingEngine which orchestrates:
    1. Scanner (strategy B, A, C)
    2. Risk manager (position sizing, daily limits)
    3. Exchange client (Kalshi order placement)

    Uses shared lock with strategy_b_job to prevent concurrent Strategy B execution.
    """
    # Prevent concurrent execution with strategy_b_job — try-acquire without blocking
    lock = _get_strategy_b_lock()
    try:
        await asyncio.wait_for(lock.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        log_event("info", "Weather arbitrage scan skipped — Strategy B lock held")
        return

    try:
        log_event("info", "Weather arbitrage scan starting...")

        try:
            global engine
            if engine is None:
                from backend.common.trader import TradingEngine
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
    finally:
        lock.release()


async def strategy_b_job():
    """
    Fast job: Strategy B only (every 2 min).

    Pure price check — no weather data needed, so it's fast.
    Uses shared lock with weather_arbitrage_job to prevent concurrent execution.
    Routes through TradingEngine.run_cycle() for consistent risk checks.
    """
    # Prevent concurrent execution with weather_arbitrage_job — try-acquire without blocking
    lock = _get_strategy_b_lock()
    try:
        await asyncio.wait_for(lock.acquire(), timeout=0.01)
    except asyncio.TimeoutError:
        log_event("info", "Strategy B fast scan skipped — lock held")
        return

    try:
        log_event("info", "Strategy B fast scan...")
        try:
            global engine
            if engine is None:
                from backend.common.trader import TradingEngine
                engine = TradingEngine()
            results = await engine.run_cycle(strategies=["strategy_b"])
            executed = sum(1 for r in results if r.get("execution", {}).get("executed", False))
            simulated = sum(1 for r in results if r.get("execution", {}).get("simulated", False))
            log_event("data",
                f"Strategy B scan complete: {executed} executed, {simulated} simulated",
                {"executed": executed, "simulated": simulated},
            )
        except Exception as e:
            log_event("error", f"Strategy B scan error: {str(e)}")
            logger.exception("Error in strategy_b_job")
    finally:
        lock.release()


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
    from backend.common.trader import TradingEngine
    engine = TradingEngine()

    # Reconcile any open positions from a previous session.
    # This detects orphaned Strategy B positions (partial bracket fills
    # from before a crash) and attempts to flatten them.
    logger.info("Running startup position reconciliation...")
    try:
        # Create a one-off task for reconciliation (it's async, scheduler not started yet)
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already in an async context — schedule it
            asyncio.create_task(engine.reconcile_positions())
        else:
            # Not yet in async context — will run on first cycle
            logger.info("Reconciliation will run after event loop starts")
    except Exception as e:
        logger.warning(f"Could not schedule position reconciliation: {e}")

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


async def _shutdown_exchange():
    """Close the shared exchange client session on shutdown."""
    global engine
    if engine and engine.exchange:
        try:
            await engine.exchange.close()
            log_event("info", "Exchange client session closed")
        except Exception as e:
            log_event("warning", f"Failed to close exchange session: {e}")


def stop_scheduler():
    """Stop the background scheduler and clean up resources."""
    global scheduler, engine

    if scheduler is None or not scheduler.running:
        log_event("info", "Scheduler not running")
        return

    # Close exchange session (async, but best-effort)
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(_shutdown_exchange())
        else:
            loop.run_until_complete(_shutdown_exchange())
    except RuntimeError:
        pass  # No event loop — session will be garbage collected

    scheduler.shutdown(wait=False)
    scheduler = None
    engine = None
    log_event("info", "Scheduler stopped and exchange session cleaned up")


def is_scheduler_running() -> bool:
    """Check if scheduler is currently running."""
    return scheduler is not None and scheduler.running