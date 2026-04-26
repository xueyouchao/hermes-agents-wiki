---
title: Polymarket+Kalshi Weather Bot (suislanchez)
created: 2026-04-26
updated: 2026-04-26
type: entity
tags: [prediction-market, polymarket, kalshi, weather-bot, kelly-criterion, ensemble-forecast]
sources: [raw/articles/polymarket-kalshi-weather-bot-suislanchez.md]
---

# Polymarket+Kalshi Weather Bot (suislanchez)

Python/React multi-strategy bot with BTC 5-min and weather ensemble strategies. Trades both Kalshi and Polymarket. Full dashboard. 31-member GFS ensemble from Open-Meteo.

## Strengths

1. **Kalshi integration** — Only bot with Kalshi API client (RSA-PSS auth, series discovery, ticker parsing for KXHIGHNY/CHI/MIA/LAX/DEN). This is critical for US-legal access.

2. **Ensemble forecasting** — Uses Open-Meteo's 31-member GFS ensemble to estimate probability of threshold exceedance. The fraction of members above/below threshold IS the model probability. This is the correct approach for weather trading.

3. **Kelly criterion sizing** — Fractional Kelly (15%) with per-trade caps. Mathematically optimal position sizing.

4. **Multi-platform** — Same signal pipeline for both Kalshi and Polymarket. Can theoretically cross-platform arbitrage.

5. **BTC 5-min strategy** — Bonus strategy using crypto microstructure (RSI, momentum, VWAP, SMA). Not directly relevant to weather but shows mature signal generation.

6. **Professional dashboard** — React frontend with equity charts, signals table, calibration panel. Useful for monitoring.

7. **APScheduler** — Auto-scans every 60s (BTC) / 5min (weather). No need for cron.

8. **Edge threshold filtering** — Minimum 8% edge for weather (higher than Guillermo's 15c flat price threshold). This means fewer but higher-confidence trades.

## Weaknesses

1. **No actual trade execution** — Only signal generation + paper trading. Neither Kalshi nor Polymarket order placement is implemented. The `KALSHI_API_KEY_ID` and `KALSHI_PRIVATE_KEY_PATH` are referenced but the actual order placement code doesn't exist.

2. **Architecture doc overpromises** — The ARCHITECTURE.md describes ECMWF 51-member ensemble blending, HRRR 3km resolution, economics pipeline, limit order walking, and cross-spread execution. None of these are implemented in the actual code.

3. **5 cities only** — NYC, Chicago, Miami, LA, Denver. Less coverage than Guillermo (6 cities) or what Kalshi actually offers (~20 cities).

4. **AI integration is decorative** — Claude and Groq are listed as dependencies but no actual AI-augmented decision logic exists in the trading pipeline. AI_DAILY_BUDGET_USD=$1.00 suggests it's for minor dashboard text, not strategy.

5. **SQLite for paper trading** — Not suitable for production order management. No transaction safety for concurrent writes.

6. **No simulation vs live trade consistency verification** — Paper and live are fundamentally different code paths. No replay mechanism to validate strategy.

7. **Settlement tracking incomplete** — `settlement.py` can check Polymarket resolution but has no Kalshi settlement logic.

8. **Ensemble source confusion** — ARCHITECTURE.md says ECMWF (51 member) + HRRR + NWS blend, but code only uses Open-Meteo (GFS 31 member). The ensemble count and quality are different.

## Verdict
Most sophisticated signal pipeline (ensemble forecasting, Kelly sizing, edge filtering), but ZERO execution capability. It's a signal generator, not a trading bot. Would need significant work to actually place orders on either platform.
