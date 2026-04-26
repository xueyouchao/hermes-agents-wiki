# Other — 04-26

# Kalshi Weather Arbitrage Bot — Project Documentation

## Purpose

This project builds a Python trading bot that executes weather prediction market strategies on Kalshi (CFTC-regulated, US-legal). It was designed by analyzing two existing open-source bots, extracting their strengths, and filling their gaps — particularly the lack of actual trade execution.

The bot targets daily high-temperature bracket markets where exactly one bracket must resolve YES. This structural guarantee enables both arbitrage and probabilistic strategies.

## Strategy Portfolio

Three strategies, prioritized by implementation order:

| Strategy | Edge Source | Needs Weather Data? | Risk Level | Status |
|----------|------------|---------------------|------------|--------|
| **B: Cross-bracket sum** | All YES prices sum < $1.00 (pure arbitrage) | No | Near-zero | **Implemented** |
| **A: Ultra-low bracket** | Underpriced long-shot brackets where ensemble prob >> price | Yes (ensemble) | Low hit rate, high payoff | Not yet |
| **C: Ensemble edge** | Model probability vs market probability disagreement | Yes (full ensemble) | Medium (model risk) | Not yet |

**Strategy B** is the first to live because it requires no weather model — it's pure price arbitrage. If the sum of all YES prices across a temperature event's brackets is less than $1.00, buying one contract in every bracket guarantees a $1.00 payout regardless of outcome.

**Strategy A** (the "ColdMath" approach) buys YES on ultra-cheap brackets (1–15¢) where ensemble forecasts suggest the true probability exceeds the price. Even a 4–6% hit rate on 1–2¢ brackets is profitable.

**Strategy C** uses the full 31-member GFS ensemble to estimate true probability per bracket, then trades when `|model_prob - market_prob| > 8%`.

## Reference Bots — What We Learned

### GuillermoEguilaz/Polymarket-Weather-Bot

TypeScript/Node.js bot trading Polymarket daily temperature markets using deterministic NWS forecasts.

**What we kept:**
- Three execution modes (signal-only, paper, live) — we use the same pattern
- CLOB order placement patterns — reference for future Polymarket integration
- NWS observation + forecast blend for daily max temperature

**What we rejected:**
- No probability estimation — just finds which bracket the forecast falls into
- No ensemble — single deterministic NWS forecast, no uncertainty quantification
- Fixed thresholds (buy < 15¢, sell >= 45¢) — no dynamic sizing
- Polymarket-only — no Kalshi access
- 6 hardcoded cities, no fee awareness, no risk management beyond position sizing

### suislanchez/polymarket-kalshi-weather-bot

Python/React multi-strategy bot with BTC 5-minute and weather ensemble strategies.

**What we kept:**
- Kalshi API client with RSA-PSS authentication (`kalshi_client.py`)
- Kalshi series discovery and ticker parsing (`kalshi_markets.py`)
- Open-Meteo GFS 31-member ensemble pipeline (`weather.py`)
- Kelly criterion position sizing
- FastAPI + APScheduler architecture
- React dashboard concept

**What we rejected:**
- Zero execution capability — signal generator only, cannot place orders
- ARCHITECTURE.md overpromises (ECMWF, HRRR, economics pipeline — none implemented)
- AI integration is decorative (Claude/Groq listed but unused in trading logic)
- SQLite for paper trading — not suitable for concurrent order management
- 5 cities only

## Architecture

```mermaid
graph TD
    subgraph CLI
        T[trade.py<br/>--sim / --live / --once]
    end

    subgraph Scheduler
        S[scheduler_v2.py<br/>APScheduler]
    end

    subgraph TradingEngine
        TE[trader.py<br/>scan → risk → execute]
    end

    subgraph Scanner
        OS[opportunity_scanner.py]
        SB[strategy_b.py<br/>Cross-bracket arb]
        SA[strategy_a.py<br/>Low-bracket<br/>(not yet)]
        SC[strategy_c.py<br/>Ensemble edge<br/>(not yet)]
    end

    subgraph Risk
        RM[risk.py<br/>Daily limits, caps,<br/>kill switch]
    end

    subgraph Exchange
        EB[base.py<br/>ExchangeClient ABC]
        EK[kalshi.py<br/>KalshiExchange]
    end

    subgraph Data
        KC[kalshi_client.py<br/>RSA-PSS auth]
        KM[kalshi_markets.py<br/>Series discovery]
        WD[weather.py<br/>GFS ensemble]
    end

    T --> TE
    S --> TE
    TE --> OS
    OS --> SB
    OS --> SA
    OS --> SC
    TE --> RM
    TE --> EB
    EB --> EK
    EK --> KC
    SB --> KM
    SC --> WD
```

### Execution Flow

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

### Key Components

| File | Purpose |
|------|---------|
| `backend/trader.py` | `TradingEngine` — orchestrates scan → risk → execute cycle |
| `backend/core/scheduler_v2.py` | APScheduler: Strategy B every 2min, full scan every 5min, heartbeat every 60s |
| `backend/exchange/base.py` | `ExchangeClient` ABC + dataclasses (`OrderResult`, `OrderSide`, `OrderType`, `Position`, `Balance`) |
| `backend/exchange/kalshi.py` | Kalshi exchange client implementing `ExchangeClient` |
| `backend/scanner/opportunity.py` | `BracketMarket`, `Opportunity`, `OpportunityType`, `OpportunityStatus` dataclasses |
| `backend/scanner/strategy_b.py` | `scan_strategy_b()` — fetches markets, groups by event, computes `sum(YES)`, flags arb when sum < $1.00 |
| `backend/scanner/opportunity_scanner.py` | `scan_all()` dispatcher for A/B/C strategies |
| `backend/core/risk.py` | `RiskManager` — daily loss limit, concentration caps, kill switch, Kelly sizing |
| `backend/data/kalshi_client.py` | Kalshi HTTP client with RSA-PSS auth (extended with `post()` and `delete()`) |
| `backend/data/kalshi_markets.py` | KXHIGH series discovery and ticker parsing |
| `trade.py` | CLI runner: `--sim`, `--live`, `--once`, `--status` |

### CLI Usage

```bash
python trade.py --sim                  # Paper trading (default)
python trade.py --live                 # Live trading (REAL MONEY)
python trade.py --once                 # Single scan cycle, exit
python trade.py --once --strategy-b    # Strategy B fast scan only
python trade.py --status               # Check Kalshi balance + positions
```

## Risk Controls

### Implemented

| Control | Default | Location |
|---------|---------|----------|
| Daily loss limit | $300 | `risk.py` |
| Max trade size | $100 | `risk.py` |
| Max event concentration | 15% of bankroll | `risk.py` (has bug — see below) |
| Max daily trades | 50 | `risk.py` |
| Max pending trades | 20 | `risk.py` |
| Min edge threshold | 2% | `risk.py` |
| Kelly fraction cap | 0.25 | `risk.py` |
| Kill switch | API endpoint | `risk.py` |

### Known Bugs in Risk Controls

1. **`risk.py:134` — Floor of 1 contract overrides risk cap**: When `adjusted_size < 1`, code sets `adjusted_size = 1`, bypassing the intended cap. Should reject the opportunity instead of rounding up.

2. **`risk.py:97-98` — Concentration check is dead code**: `approve_opportunity()` accepts a `current_positions` parameter, but `TradingEngine.run_cycle()` never passes it. The 15% concentration limit does nothing.

3. **`risk.py:127` — Strategy B size formula uses `max(yes_price)`**: Divides `max_trade_size` by the most expensive bracket, producing the fewest sets. Should use `total_cost_per_set` for optimal sizing.

## Critical Gaps Before Live Trading

These must be fixed before deploying real money:

### P0 — Fee Modeling

`strategy_b.py:155` assumes 0% fees. If `sum(YES) = $0.97` and Kalshi charges even 1%, the edge evaporates. Add `KALSHI_FEE_RATE` config and subtract from calculated edge:

```python
net_edge = 1.00 - sum(yes_ask) - total_fees
```

### P0 — Orderbook Ask Prices, Not Mid/Last

The scanner currently uses `last_price` or `mid` for edge calculation. Arb opportunities that appear at mid may not be executable at the ask. Switch to `yes_ask` (best ask price).

### P0 — Liquidity Filter

No check for order book depth before placing trades. Markets under $1,000 in volume should be skipped. Position size should be capped at 1–5% of available liquidity.

### P0 — Persist Risk State

`RiskManager._daily_stats` and `TradingEngine._results` are in-memory only. A crash mid-day resets the daily loss counter, bypassing limits. Must write to `Trade` / `BotState` database tables.

### P0 — Order Timeouts

`trader.py` has no timeout on `place_order` calls. A hung order in `_execute_strategy_b` blocks the entire cycle. Wrap with `asyncio.wait_for()`.

### P0 — Auto-Cancel on Kill

When `is_trading_allowed()` returns False, pending orders are not cancelled. Stale orders could execute after the halt.

## Other Known Issues

| Issue | Severity | Location |
|-------|----------|----------|
| `trader.py:296` — Direction heuristic parses `opp.reasoning` string for YES/NO | Medium | `_execute_single_market` |
| `datetime.utcnow()` deprecated | Low | `trader.py:73`, `risk.py:46`, `opportunity.py:87` |
| `kalshi.py:91` — `filled_price_cents / 100.0` unit ambiguity | Medium | Verify Kalshi returns cents vs dollars |
| `kalshi_client.py` — New `httpx.AsyncClient` per request, no retry on 429/5xx | Medium | Needs shared session + `tenacity` |
| `_pending_orders` dict in `kalshi.py` never cleaned | Low | Memory leak |
| No transaction atomicity for Strategy B — 5 brackets bought sequentially | Medium | Use `asyncio.gather()` |
| `config.py` docstring says "BTC 5-min trading bot" | Low | Copy-paste leftover |
| `opportunity_scanner.py:19` — Function name shadows import | Low | Rename one |

## Test Coverage

13 tests passing across two files:

| File | Tests | Coverage |
|------|-------|----------|
| `tests/test_strategy_b.py` | 8 | Arb detection, grouping, risk |
| `tests/test_trading_pipeline.py` | 5 | Mock exchange, sim cycle, live cycle, kill switch, daily limit |

**Not tested:**
- `kalshi.py` (exchange client, real order placement)
- `kalshi_client.py` (auth, request signing)
- Strategy B partial fill path
- `_extract_bracket_markets` (raw data parsing)
- `opportunity_scanner.py` dispatcher
- `scheduler_v2.py` lifecycle
- Negative/risk edge cases (size=0, cost=0, empty brackets)
- `trade.py` CLI argument parsing
- `MockExchange` doesn't simulate failures (timeouts, rejections, partial fills)

## Configuration

Key parameters with defaults:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `SIMULATION_MODE` | `true` | Paper trading (no real orders) |
| `INITIAL_BANKROLL` | $10,000 | Starting balance for risk calculations |
| `DAILY_LOSS_LIMIT` | $300 | Max daily loss before auto-shutdown |
| `MAX_TRADE_SIZE` | $100 | Per-trade cap |
| `MAX_EVENT_CONCENTRATION` | 0.15 | Max % of bankroll per event |
| `MIN_EDGE` | 0.02 | Minimum edge to enter a trade |
| `KELLY_FRACTION` | 0.25 | Fractional Kelly for position sizing |
| `KALSHI_API_KEY_ID` | — | Kalshi API credential |
| `KALSHI_PRIVATE_KEY_PATH` | — | RSA private key path |

## Kalshi Market Coverage

| Phase | Cities | Series Tickers |
|-------|--------|---------------|
| MVP | NYC, Chicago, Miami | KXHIGHNY, KXHIGHCHI, KXHIGHMIA |
| Expand | + LA, Denver | KXHIGHLAX, KXHIGHDEN |
| Full | + all available (~20) | KXHIGHTDAL, KXHIGHLAS, KXHIGHPHX, etc. |

## Build Status

**Phase 1 (Scanner + Exchange + Risk):** Complete
**Phase 2 (TradingEngine + Scheduler + CLI):** Complete
**Phase 3 (Kalshi Live Execution):** Blocked on API credentials
**Phase 4 (Risk Hardening):** Not started
**Phase 5 (Validation):** Not started
**Phase 6 (Polymarket Support):** Future

### Blocked On

Kalshi API credentials (`KALSHI_API_KEY_ID` and `KALSHI_PRIVATE_KEY_PATH`). Cannot validate against live market data or place real orders until these are configured.

### Next Steps

1. Set up Kalshi API credentials (register account, generate RSA key pair)
2. Paper trading validation with real market data: `python trade.py --once --strategy-b`
3. Fix P0 gaps (fee modeling, ask prices, liquidity filter, state persistence, order timeouts)
4. Build Strategy A scanner (ensemble weather → low-bracket edge detection)
5. Build Strategy C scanner (full ensemble disagreement → actionable signals)
6. Settlement monitoring (detect resolved markets, calculate realized P&L)