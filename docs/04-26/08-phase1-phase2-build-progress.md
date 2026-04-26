---
title: Phase 1-2 Build Progress — Kalshi Weather Arbitrage Bot
created: 2026-04-26
updated: 2026-04-26
type: progress-log
branch: weather-arbitrage
repo: speedgap-prototype
---

# Build Progress — Kalshi Weather Arbitrage Bot

## Overview

Two phases completed. The bot can now scan Kalshi weather markets, detect cross-bracket sum arbitrage (Strategy B), approve/reject via risk management, and execute orders — all orchestrated by a main loop with APScheduler.

## Phase 1: Scanner + Exchange Layer + Risk Management

**Commit:** `Phase 1: Clean Go code, build exchange layer + Strategy B scanner + risk manager`

### What was built

| File | Purpose |
|------|---------|
| `backend/exchange/base.py` | `ExchangeClient` ABC + dataclasses (`OrderResult`, `OrderSide`, `OrderType`, `PositionSide`, `OrderBook`, `Position`, `Balance`) |
| `backend/exchange/kalshi.py` | Kalshi exchange client — implements `ExchangeClient` using `kalshi_client.py` auth (RSA-PSS for order placement) |
| `backend/scanner/opportunity.py` | `BracketMarket`, `Opportunity`, `OpportunityType`, `OpportunityStatus` dataclasses |
| `backend/scanner/strategy_b.py` | `StrategyBScanner` — fetches markets, groups by event, computes `sum(YES)`, flags arb when sum < $1.00, calculates edge and sizing |
| `backend/scanner/opportunity_scanner.py` | `scan_all()` dispatcher for A/B/C strategies, `scan_strategy_b()` standalone fast-scan |
| `backend/core/risk.py` | `RiskManager` — daily loss limit, max event concentration cap (15%), min edge threshold (2%), kill switch, Kelly-based position sizing for Strategy B |
| `backend/data/kalshi_client.py` | Extended with `post()` and `delete()` methods (was only `get()` before) — needed for order placement |
| `tests/test_strategy_b.py` | 8 unit tests — all passing |

### Key decisions

- **asyncio + httpx, single process** — daily-resolution weather markets only need ~120 API calls every 2-5 min, entirely I/O-bound
- **APScheduler intervals** — Strategy B every 2min, A+C every 5min
- **Strategy B first** — pure price arbitrage, no weather model, near-100% win rate
- **IOC orders for Strategy B** — immediate-or-cancel guarantees we don't hold partial arb positions

### Repo cleanup

- Removed all Go code (`code/go/`, `internal/`, old `code/python/weather_bot/`)
- Removed stale `code/python/main.py` and `requirements.txt`
- Added `.gitignore` (venv, __pycache__, .env, etc.)
- Copied `venv/` into project for self-contained setup

---

## Phase 2: Main Loop — TradingEngine + Scheduler + CLI

**Commit:** `Phase 2: Wire main loop — TradingEngine + scheduler + CLI runner`

### What was built

| File | Purpose |
|------|---------|
| `backend/trader.py` | `TradingEngine` — orchestrates scan → risk → execute cycle. Handles simulation mode, partial fills, position reconciliation, kill switch |
| `backend/core/scheduler_v2.py` | APScheduler-based background jobs: Strategy B fast scan (2min), full scan B+A+C (5min), heartbeat (60s), event log |
| `trade.py` | Standalone CLI runner for headless operation |
| `tests/test_trading_pipeline.py` | 5 e2e tests with `MockExchange` (all passing) |

### trader.py — The Drivetrain

```
TradingEngine.run_cycle()
    ├── Step 1: scan_all(exchange)  →  List[Opportunity]
    ├── Step 2: RiskManager.approve_opportunity(opp)  →  (allowed, adjusted_size, reason)
    ├── Step 3: _execute_opportunity(opp)
    │   ├── SIMULATION: log decisions, no orders placed
    │   ├── Strategy B: buy YES on every bracket via IOC
    │   └── Strategy A/C: single market via LIMIT
    └── Step 4: Summary log (found/approved/executed/simulated/edge)
```

**Partial fill handling for Strategy B:**
- If all brackets fill → `COMPLETE` (guaranteed profit)
- If some fill → `PARTIAL` (incomplete arb, still likely profitable)
- If zero fill → `CANCELLED`
- Risk manager tracks every executed trade for daily P&L and concentration

**Simulation mode (`SIMULATION_MODE=true`):**
- Runs the full scan → risk pipeline
- Logs every decision with `[SIM]` prefix
- Places zero orders on the exchange
- Validates against mock data (5 e2e tests)

### trade.py — CLI Runner

```bash
python trade.py --sim                  # Paper trading (default)
python trade.py --live                 # Live trading (REAL MONEY)
python trade.py --once                 # Single scan cycle, exit
python trade.py --once --strategy-b    # Strategy B fast scan only
python trade.py --status               # Check Kalshi balance + positions
```

### Test Results

```
13 passed in 0.32s

tests/test_strategy_b.py          — 8 tests (arb detection, grouping, risk)
tests/test_trading_pipeline.py    — 5 tests (mock exchange, sim cycle, live cycle, kill switch, daily limit)
```

### Architecture Diagram

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌───────────────┐
│  APScheduler │────▶│ TradingEngine │────▶│ opportunity_    │────▶│ strategy_b.py │
│  (2min/5min) │     │   (trader.py) │     │ scanner.py      │────▶│ strategy_a.py │
└─────────────┘     │               │     └─────────────────┘────▶│ strategy_c.py │
                    │               │                                └───────────────┘
                    │               │     ┌─────────────────┐
                    │               ├────▶│  RiskManager    │ (approve/reject + sizing)
                    │               │     └─────────────────┘
                    │               │
                    │               │     ┌─────────────────┐
                    │               └────▶│  ExchangeClient │────▶│ KalshiExchange │
                    │                     │  (base.py)      │────▶│ (kalshi.py)    │
                    │                     └─────────────────┘     └────────────────┘
                    │
┌─────────────┐     │
│  trade.py    │─────┘ (CLI entry point)
│  --sim/--live│
│  --once      │
│  --status    │
└─────────────┘
```

---

## Current State

### Working
- Exchange abstraction layer (Kalshi client with RSA-PSS auth)
- Strategy B scanner (cross-bracket sum arbitrage detection)
- Risk manager (daily loss limits, concentration caps, kill switch)
- Trading engine (full scan → risk → execute pipeline)
- APScheduler background jobs (V2 scheduler)
- CLI runner (`trade.py`)
- Simulation mode (end-to-end with mock data, zero orders)
- 13 unit + integration tests, all passing

### Not Yet Built
- **Strategy A scanner** (`strategy_a.py`) — ultra-low bracket detection (needs ensemble weather data)
- **Strategy C scanner** (`strategy_c.py`) — ensemble edge vs market disagreement
- **Partial fill reconciliation** — what to do when not all Strategy B brackets fill
- **End-to-end validation with live Kalshi API** — blocked on API credentials
- **Paper trading with real Kalshi data** — need API key to read real market data
- **Settlement monitoring** — auto-detect resolved markets and calculate P&L

### Blocked
- **No Kalshi API credentials set up yet** — cannot validate against live data
- Need `KALSHI_API_KEY_ID` and `KALSHI_PRIVATE_KEY_PATH` environment variables

---

## Next Steps

1. **Set up Kalshi API credentials** — register account, generate RSA key pair, configure `.env`
2. **Paper trading validation** — `python trade.py --once --strategy-b` with real market data
3. **Strategy A scanner** — ensemble weather data → low-bracket edge detection
4. **Strategy C scanner** — full ensemble disagreement → actionable signals
5. **Settlement monitoring** — detect resolved markets, calculate realized P&L
6. **Dashboard** — FastAPI server for live monitoring (already scaffolded in `api/main.py`)

---

## File Manifest (New/Modified)

### Phase 1 (new files)
```
backend/exchange/__init__.py
backend/exchange/base.py          — ExchangeClient ABC + dataclasses
backend/exchange/kalshi.py        — KalshiExchange implementation
backend/scanner/__init__.py
backend/scanner/opportunity.py    — BracketMarket, Opportunity models
backend/scanner/strategy_b.py     — Cross-bracket arb scanner
backend/scanner/opportunity_scanner.py — Unified scanner dispatcher
backend/core/risk.py              — RiskManager with daily limits
tests/test_strategy_b.py          — 8 unit tests
```

### Phase 1 (modified)
```
backend/data/kalshi_client.py     — Added post() and delete() for authenticated HTTP
```

### Phase 2 (new files)
```
backend/trader.py                 — TradingEngine (scan → risk → execute)
backend/core/scheduler_v2.py      — APScheduler background jobs (V2)
trade.py                          — CLI runner (--sim/--live/--once/--status)
tests/test_trading_pipeline.py    — 5 e2e tests with MockExchange
```