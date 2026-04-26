---
title: Polymarket Weather Bot (GuillermoEguilaz)
created: 2026-04-26
updated: 2026-04-26
type: entity
tags: [prediction-market, polymarket, weather-bot]
sources: [raw/articles/polymarket-weather-bot-guillermo.md]
---

# Polymarket Weather Bot (GuillermoEguilaz)

TypeScript/Node.js bot that trades Polymarket daily temperature markets using deterministic NWS forecast data. Single-platform, single-strategy (Strategy A: low-bracket buying).

## Strengths

1. **Working Polymarket CLOB execution** — Real order placement via @polymarket/clob-client v4.22.8, with proxy wallet support (MetaMask EOA + Gnosis Safe). This is the strongest execution layer of all three bots.

2. **Three execution modes** — signal-only (dry-run), paper trading (simulation.json), and live CLOB orders. Clean separation for testing.

3. **Simple, auditable strategy** — Buy YES when price < 15c, sell when price >= 45c. Very easy to reason about. The cold-math ultra-low bracket approach (our Strategy A) is implemented here.

4. **NWS observation + forecast blend** — Uses both historical station observations AND hourly forecasts to derive daily max, which is more accurate than forecast-only.

5. **Low operational complexity** — Single language (TypeScript), no database, no web framework. Just run `npm run trade` and it works.

## Weaknesses

1. **Polymarket only** — No Kalshi support. Cannot access US-legal markets.

2. **No probability estimation** — Doesn't estimate "what's the probability the high is above X°F". Just finds which bracket the forecast falls into. This misses cross-bracket opportunities entirely.

3. **No ensemble forecasting** — Single NWS deterministic forecast. No uncertainty quantification. If NWS is wrong by 2°F, the bot might pick the wrong bracket.

4. **Fixed thresholds** — Entry at 15c and exit at 45c are hardcoded defaults. No dynamic threshold based on time-to-resolution, ensemble agreement, or market volume.

5. **6 cities only** — Hardcoded NWS gridpoints for nyc, chicago, miami, dallas, seattle, atlanta. Extending requires manual NWS gridpoint lookup.

6. **No risk management** — No stop-loss, no daily loss limit, no Kelly sizing. Just 5% per trade.

7. **No cross-bracket arbitrage** — Cannot implement Strategy B (buy all YES when sum < $1).

8. **No fee model** — Polymarket trading fees not factored into P&L.

9. **Paper trading ledger is fragile** — simulation.json is not an atomic write. Crash between write operations could corrupt it.

## Verdict
Best-in-class for simple Polymarket weather execution. Solid CLOB integration. Weak on intelligence (forecasting, sizing, risk management). Good starting point for Polymarket-only Strategy A.
