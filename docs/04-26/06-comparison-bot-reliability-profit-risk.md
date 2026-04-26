---
title: Prediction Market Bot Comparison — Guillermo vs Suislanchez vs Speedgap
created: 2026-04-26
updated: 2026-04-26
type: comparison
tags: [prediction-market, polymarket, kalshi, weather-bot, comparison]
sources: [raw/articles/polymarket-weather-bot-guillermo.md, raw/articles/polymarket-kalshi-weather-bot-suislanchez.md]
---

# Prediction Market Bot Comparison

> Side-by-side analysis of three approaches to weather prediction market trading, evaluating reliability, profit potential, and risk factors.

## Candidates

| Dimension | GuillermoEguilaz Bot | Suislanchez Bot | Speedgap Prototype |
|-----------|----------------------|-----------------|---------------------|
| **Language** | TypeScript / Node.js | Python + React (FastAPI backend) | Go |
| **Platforms** | Polymarket only | Kalshi + Polymarket (signals only) | Polymarket (planned Kalshi) |
| **Strategy** | Strategy A (low-bracket buying) | Strategy C (ensemble edge) | Strategy A (planned B+C) |
| **Weather Data** | NWS deterministic forecast | Open-Meteo (GFS 31-member ensemble) | Planned NWS + ensemble |
| **Execution** | Working CLOB orders | Signal generation only (no execution) | Placeholders (PLACEHOLDER_REPLACE_ME) |
| **Sizing** | 5% flat per trade | Fractional Kelly (15%) | Planned Kelly |
| **Risk Mgmt** | Max trades per run | Daily loss limit, per-trade cap | Planned (inert risk manager) |
| **Cities** | 6 (hardcoded NWS endpoints) | 5 (NYC, Chicago, Miami, LA, Denver) | Planned (API discovery) |
| **Fees** | Not modeled | Not modeled | 15bps drag accounted |
| **Tests** | 0 | 0 | 0 |
| **Deployment** | CLI (npm run trade --interval 30) | Docker-ready (Railway + Vercel) | CLI (planned) |
| **Dashboard** | Terminal colored output | Full React dashboard | None |
| **Code Quality** | Clean, small scope, well-structured | Ambitious, partially implemented | Has P0 bugs (price mismatch) |
| **US-legal** | No (Polymarket blocks US) | Partially (Kalshi is CFTC-regulated) | No (Polymarket blocks US) |

## Reliability Assessment

### Guillermo Bot: MODERATE-HIGH reliability
- **Pro:** Actually works for Polymarket execution. CLOB integration tested and functional.
- **Pro:** Simple scope means fewer failure modes.
- **Con:** Single weather source (NWS). If NWS API goes down or data is stale, bot is blind.
- **Con:** No atomic state persistence. simulation.json corruption risk.
- **Con:** Fixed thresholds don't adapt to market conditions.
- **Estimated uptime:** Can run unattended for days with --interval mode.

### Suislanchez Bot: LOW reliability as a trading bot
- **Pro:** Good signal generation with ensemble probability estimation.
- **Pro:** Clean architecture (data/signals/execution separation).
- **Critical con:** Cannot actually place orders. It's a signal generator, not a trading bot.
- **Critical con:** ARCHITECTURE.md overpromises — ECMWF, HRRR, Econ pipeline not implemented.
- **Con:** 5 cities only limits market coverage significantly.
- **Con:** SQLite not suitable for concurrent order management.
- **Estimated uptime:** Can run as a dashboard, but cannot execute trades.

### Speedgap Prototype: LOW reliability
- **Critical:** P0 bug comparing BTC spot price to YES token price (scale mismatch).
- **Critical:** All Polymarket API calls are stubbed (PLACEHOLDER_REPLACE_ME).
- **Con:** REST polling (2-3s) kills speed-gap strategy.
- **Con:** LLM signal disconnected from execution.
- **Con:** Zero tests.
- **Pro:** Go performance is excellent for low-latency strategies.
- **Pro:** Temporal SAGA pattern is architecturally sound for order management.

## Profit Potential Assessment

### Guillermo Bot: 5-15% monthly on deployed capital (Polymarket Strategy A)
- **Expected:** With 6 cities, ~2-3 actionable opportunities per day at 15c entry threshold.
- **Win rate:** Low-bracket strategy has ~5-10% hit rate per bracket, but each hit pays 5-10x.
- **Edge decay:** As more bots use this approach, ultra-low brackets get priced more efficiently.
- **Fees:** Polymarket CLOB has no trading fees, so edge is not eroded.
- **Capital efficiency:** Low — capital sits in cheap positions that often expire worthless.

### Suislanchez Bot: 10-20% monthly IF execution were implemented (Strategy C on Kalshi)
- **Expected:** 8% edge threshold produces fewer but higher-quality signals.
- **Win rate:** Higher (50-70%) because ensemble forecast is genuinely informative.
- **Kalshi advantage:** CFTC-regulated, US-legal, broader institutional participation means more mispricing.
- **Fees:** Kalshi charges quadratic fees (small), reducing net edge by ~1-2%.
- **Capital efficiency:** Moderate — positions are held 1-3 days with clear resolution.

### Speedgap Prototype: THEORETICAL only
- Cannot generate profit in current state. Must fix P0 bugs and add real execution.

## Risk Factor Analysis

### Guillermo Bot Risks
| Risk | Severity | Likelihood | Impact |
|------|----------|-----------|--------|
| NWS data staleness | Medium | Low | Bot picks wrong bracket |
| Polymarket geo-blocking | High | Certain | Cannot trade from US/UK/FR/DE |
| Edge decay | High | Medium | As more bots enter, ultra-low brackets get priced up |
| Simulation corruption | Low | Low | Ledger lost, but positions tracked on-chain |
| Private key exposure | Critical | Low | If .env compromised |
| API changes | Medium | Low | Polymarket Gamma API could change |

### Suislanchez Bot Risks
| Risk | Severity | Likelihood | Impact |
|------|----------|-----------|--------|
| No execution capability | Critical | Certain | Cannot make money AT ALL |
| Architecture/code divergence | High | Certain | Wrong expectations, wrong time estimates |
| Ensemble model miscalibration | High | Medium | Systematic losses if GFS is biased |
| Kalshi API key not working | High | Medium | Cannot access Kalshi markets |
| AI cost overruns | Low | Low | $1/day cap limits damage |
| Dashboard attack surface | Medium | Low | CORS/auth not well-documented |

### Common Risks (both weather bots)
| Risk | Severity | Likelihood | Impact |
|------|----------|-----------|--------|
| Weather model errors | Medium | Medium | Wrong signal, systematic losses |
| Market manipulation | Low | Low | Someone could move thin markets |
| Regulatory changes | Low | Low | CFTC could restrict prediction markets |
| Platform downtime | Medium | Low | Miss resolution periods |

## Recommendation

### Should you use Guillermo's bot as-is?
**YES for Polymarket Strategy A, with modifications:**
1. Add VPN proxy setup for US access (or deploy on non-US VPS)
2. Add ensemble forecasting (import from suislanchez's weather.py)
3. Replace fixed thresholds with dynamic Kelly sizing
4. Add Kalshi support (adapt saislanchez's Kalshi client)
5. Add cross-bracket arbitrage detection (Strategy B)

### Should you use suislanchez's bot as-is?
**NO — it cannot execute trades. But borrow heavily:**
1. Use its Kalshi client architecture (RSA-PSS auth)
2. Use its ensemble forecasting pipeline (Open-Meteo + NWS blend)
3. Use its market discovery logic (Kalshi series ticker parsing)
4. Use its Kelly sizing formula
5. Use its React dashboard concept for monitoring

### Should you stick with speedgap-prototype?
**NO in its current state, but the Go architecture is worth keeping:**
- The Temporal SAGA pattern for order management is correct
- Go's performance is ideal for speed-sensitive strategies
- But the weather-arbitrage branch has a working Python skeleton already

### Optimal Path: Hybrid Approach

**Fork and merge the best parts into speedgap-prototype's weather-arbitrage branch:**

1. **Execution:** Use Guillermo's Polymarket CLOB client (TypeScript) as a reference to build Go execution, or call it as a subprocess
2. **Signal generation:** Use suislanchez's ensemble pipeline (weather.py, weather_signals.py) as the signal engine
3. **Kalshi access:** Use suislanchez's kalshi_client.py and kalshi_markets.py for Kalshi market data
4. **Strategy:** Run Strategy A (Guillermo's low-bracket buying on Polymarket) + Strategy C (ensemble edge on Kalshi)
5. **Risk management:** Use suislanchez's Kelly sizing and daily loss limits
6. **Dashboard:** Optional — borrow suislanchez's React frontend for monitoring
7. **Language:** Python for now (the weather_bot.py on the weather-arbitrage branch). Go is overkill for daily-resolution weather markets.

This avoids reinventing the wheel while getting working execution (from Guillermo) + intelligent signals (from suislanchez) + Kalshi legal access (from suislanchez).
