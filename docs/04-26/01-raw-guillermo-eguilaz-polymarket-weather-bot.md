---
source_url: https://github.com/GuillermoEguilaz/Polymarket-Weather-Bot
ingested: 2026-04-26
sha256: 16c894d9c5f78bcb
---

# Polymarket Weather Bot (GuillermoEguilaz)

## Overview
TypeScript Node.js bot that trades Polymarket daily temperature markets using NWS forecast data. Single-platform (Polymarket only). Three execution modes: signal-only, paper trading, live CLOB orders.

## Architecture
- Language: TypeScript / Node.js 18+
- Chain: Polygon (chain ID 137)
- CLOB Client: @polymarket/clob-client v4.22.8
- Wallet: MetaMask EOA + optional proxy/safe wallet (signature types 0/1/2)
- Weather: NWS api.weather.gov (hourly forecasts + station observations, 6 cities hardcoded)
- Config: .env for all runtime settings; config.json is legacy

## Core Files
- src/strategy.ts (501 lines): Main strategy loop — scans cities, matches forecast temp to market brackets, buy YES when price < entry_threshold, sell when price >= exit_threshold
- src/nws.ts (85 lines): NWS API client — fetches observations + hourly forecasts, derives daily max temp per city per date
- src/polymarket.ts (69 lines): Gamma API client — finds events by slug, gets market YES prices
- src/clob.ts (136 lines): CLOB client setup — wallet signer, API key derivation, buy/sell YES limit orders
- src/simState.ts (87 lines): Paper trading ledger in simulation.json
- src/parsing.ts (39 lines): Temperature range parser from market question text

## Strategy Logic
1. For each configured city, fetch daily max temp forecast from NWS
2. Look up the matching Polymarket event (slug-based search)
3. Find the bracket containing forecast temp
4. If YES price < ENTRY_THRESHOLD (default 0.15), buy YES
5. If YES price >= EXIT_THRESHOLD (default 0.45), sell existing position
6. Position sizing: 5% of balance per trade
7. Max trades per run: configurable (default 5)
8. Skip if < MIN_HOURS_TO_RESOLUTION (default 2)

## Key Parameters (defaults)
- ENTRY_THRESHOLD: $0.15 (buy if YES < 15 cents)
- EXIT_THRESHOLD: $0.45 (sell if YES >= 45 cents)
- POSITION_PCT: 5% of balance
- MIN_HOURS_TO_RESOLUTION: 2
- MAX_TRADES_PER_RUN: 5

## Supported Cities (hardcoded)
nyc, chicago, miami, dallas, seattle, atlanta

## Limitations
- Polymarket ONLY — no Kalshi support
- 6 cities only (hardcoded NWS endpoints)
- No ensemble forecasting — single NWS deterministic forecast
- No probability estimation — just "forecast temp falls in bucket X"
- No cross-bracket arbitrage (Strategy B)
- Single weather data source (NWS only)
- No fee awareness
- Exit logic is crude (sell at 45c regardless of time to resolution)
- No risk management beyond position sizing cap
- Simulation ledger is a local JSON file (no persistence guarantees)
- No tests
