"""Alerting module for critical trading bot events.

Provides hooks for:
- Risk halt triggered (kill switch, daily loss limit, drawdown)
- Partial fill exposure (Strategy B brackets incomplete)
- Exchange API errors (repeated failures)
- Daily stats reset (P&L summary)
- Execution failures

Alerts are logged at CRITICAL/ERROR level and can be extended to push
notifications (email, webhook, Slack) by registering alert handlers.

Usage:
    from backend.common.alerting import alert, AlertLevel

    alert(AlertLevel.CRITICAL, "Kill switch activated", details={...})
"""
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Dict, List, Optional

logger = logging.getLogger("trading_bot.alerts")


class AlertLevel(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# Registered alert handlers (beyond logging)
_alert_handlers: List[Callable[[AlertLevel, str, Dict], None]] = []


def register_handler(handler: Callable[[AlertLevel, str, Dict], None]):
    """Register an external alert handler (e.g., Slack webhook, email).

    The handler receives (level, message, details_dict).
    """
    _alert_handlers.append(handler)


def alert(level: AlertLevel, message: str, details: Optional[Dict] = None):
    """Emit an alert for a critical event.

    Logs the alert at the appropriate level and dispatches to all
    registered handlers. This is the single entry point for all
    trading bot alerts.

    Args:
        level: Severity level
        message: Human-readable description
        details: Optional dict with structured context
    """
    details = details or {}
    timestamp = datetime.now(timezone.utc).isoformat()

    # Structured log line
    log_line = f"[ALERT:{level.value.upper()}] {message}"
    if details:
        log_line += f" | {details}"

    # Log at appropriate Python level
    log_map = {
        AlertLevel.INFO: logger.info,
        AlertLevel.WARNING: logger.warning,
        AlertLevel.ERROR: logger.error,
        AlertLevel.CRITICAL: logger.critical,
    }
    log_func = log_map.get(level, logger.info)
    log_func(log_line)

    # Dispatch to registered handlers
    for handler in _alert_handlers:
        try:
            handler(level, message, {**details, "timestamp": timestamp})
        except Exception as e:
            logger.error(f"Alert handler {handler.__name__} failed: {e}")


def alert_risk_halt(reason: str, details: Optional[Dict] = None):
    """Alert when trading is halted by risk manager."""
    alert(
        AlertLevel.CRITICAL,
        f"TRADING HALTED: {reason}",
        details={"reason": reason, **(details or {})},
    )


def alert_partial_fill(brackets_filled: int, brackets_total: int, tickers: List[str]):
    """Alert when a Strategy B execution results in partial fill."""
    alert(
        AlertLevel.CRITICAL,
        f"PARTIAL FILL: {brackets_filled}/{brackets_total} brackets filled — FLATTENING",
        details={
            "brackets_filled": brackets_filled,
            "brackets_total": brackets_total,
            "tickers": tickers,
            "action": "flatten_all_positions",
        },
    )


def alert_exchange_error(operation: str, error: str, ticker: str = ""):
    """Alert on repeated exchange API errors."""
    alert(
        AlertLevel.ERROR,
        f"Exchange error during {operation}: {error}",
        details={"operation": operation, "error": error, "ticker": ticker},
    )


def alert_daily_reset(yesterday_pnl: float, trades: int, date_str: str):
    """Alert when daily stats reset at UTC midnight."""
    alert(
        AlertLevel.INFO,
        f"Daily stats reset for {date_str}: P&L=${yesterday_pnl:.2f}, {trades} trades",
        details={"yesterday_pnl": yesterday_pnl, "trades": trades, "date": date_str},
    )


def alert_execution_failure(strategy: str, ticker: str, error: str):
    """Alert when an order execution fails."""
    alert(
        AlertLevel.ERROR,
        f"Execution failure for {strategy} on {ticker}: {error}",
        details={"strategy": strategy, "ticker": ticker, "error": error},
    )