---
source_url: https://github.com/suislanchez/polymarket-kalshi-weather-bot
ingested: 2026-04-26
sha256: af24b1e5bc93e7f2
---

# Polymarket + Kalshi Weather Bot (suislanchez)

## Overview
Multi-strategy Python+React trading bot that trades both Kalshi and Polymarket weather temperature markets using 31-member GFS ensemble forecasts. Also includes a BTC 5-minute microstructure strategy. Full React dashboard.

## Architecture
- Backend: FastAPI + Python 3.10+ + SQLite + APScheduler
- Frontend: React 18 + TypeScript + TanStack Query + Tailwind
- Deployment: Railway (backend) + Vercel (frontend)
- Data Sources: Open-Meteo (GFS ensemble), NWS, Coinbase/Kraken/Binance (BTC)

## Two Strategies

### Strategy 1: BTC 5-Minute Up/Down (Polymarket only)
- Scan Polymarket BTC 5-min markets every 60s
- Compute RSI(14), momentum (1m/5m/15m), VWAP deviation, SMA crossover, market skew
- Weighted composite -> model UP probability (0.35-0.65 range)
- Convergence filter: 2+ of 4 indicators must agree
- Trade when edge > 2%, fractional Kelly 15%, cap $75/trade

### Strategy 2: Weather Temperature (Kalshi + Polymarket)
- Scan weather markets every 5 min on both platforms
- 31-member GFS ensemble from Open-Meteo for probability estimation
- Count fraction of members above/below threshold -> model probability
- Trade when edge > 8%, fractional Kelly 15%, cap $100/trade
- Kalshi series: KXHIGHNY, KXHIGHCHI, KXHIGHMIA, KXHIGHLAX, KXHIGHDEN
- Polymarket: auto-discovered via Gamma API search

## Core Files (Backend)
- backend/data/weather.py (256 lines): Open-Meteo ensemble + NWS observations, 5 cities
- backend/data/weather_markets.py (276 lines): Polymarket weather market discovery + parsing
- backend/data/kalshi_markets.py (169 lines): Kalshi KXHIGH series discovery + ticker parsing
- backend/data/kalshi_client.py (99 lines): Kalshi API with RSA-PSS auth
- backend/data/crypto.py (467 lines): BTC microstructure from Coinbase/Binance/Kraken
- backend/data/btc_markets.py (261 lines): BTC 5-min market discovery from Polymarket
- backend/core/signals.py (401 lines): BTC signal generation + Kelly sizing
- backend/core/weather_signals.py (245 lines): Weather signal generation using ensemble
- backend/core/scheduler.py (484 lines): APScheduler jobs + trade execution
- backend/core/settlement.py (322 lines): Market resolution tracking + PnL calculation
- backend/config.py (75 lines): Pydantic settings with all parameters

## Key Parameters (defaults)
- BTC: KELLY_FRACTION=0.15, MIN_EDGE=2%, MAX_ENTRY_PRICE=0.55, SCAN=60s
- Weather: KELLY_FRACTION=0.15 (also described as 0.25 quarter-Kelly in ARCHITECTURE.md), MIN_EDGE=8%, MAX_ENTRY_PRICE=0.70, SCAN=5min, MAX_TRADE_SIZE=$100
- General: INITIAL_BANKROLL=$10,000, DAILY_LOSS_LIMIT=$300, SIMULATION_MODE=true default

## Supported Cities (weather)
nyc, chicago, miami, los_angeles, denver (5 cities)

## ARCHITECTURE.md vs Code Divergences
The ARCHITECTURE.md describes a grander vision:
- 3-layer weather pipeline (NWS + ECMWF 51-member + HRRR) — code only uses Open-Meteo (GFS 31-member)
- Economics pipeline (Fed/CPI/Jobs/GDP) — not implemented
- Edge filter chain with time decay — not implemented
- Limit order walking (1c every 5 min) — not implemented
- Cross-spread execution for high edge — not implemented
- Calibration + learning loop — partially implemented (tracking Brier scores conceptually)

## Risk Management
- Kelly criterion sizing (fractional)
- Per-trade caps ($75 BTC, $100 weather)
- Daily loss limit ($300)
- Entry price filter (BTC < 55c, Weather < 70c)
- Min time remaining (BTC: 60s, no weather filter)

## AI Integration
- Claude (anthropic>=0.40.0) — referenced but usage unclear in code
- Groq (llama-3.1-8b-instant) — referenced but no clear trading logic usage
- AI_DAILY_BUDGET_USD: $1.00 default

## Limitations
- No actual Kalshi trade execution (API key required, only market discovery implemented)
- No actual Polymarket trade execution (only signal generation + paper trading)
- Simulation mode is the default and only tested mode
- ARCHITECTURE.md describes features not implemented in code
- 5 cities only for weather (not 50+ like Guillermo's approach allows)
- AI integration appears decorative
- No cross-platform arbitrage logic
- No ensemble blending (NWS + ECMWF + HRRR) as described in architecture doc
