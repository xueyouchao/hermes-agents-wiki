---
title: Kalshi Weather Trading Bot — Implementation Plan
created: 2026-04-26
updated: 2026-04-26
type: plan
status: approved
branch: weather-arbitrage
base: suislanchez/polymarket-kalshi-weather-bot
---

# Kalshi Weather Trading Bot — Final Implementation Plan

## Decision Record

**2026-04-26:** Dropped speedgap-prototype Go architecture. Pivoting to hybrid approach:
- Base: suislanchez/polymarket-kalshi-weather-bot (Python + React)
- Execution: Borrow GuillermoEguilaz CLOB client patterns, rebuild for Kalshi
- Language: Python (Go is overkill for daily-resolution weather markets)
- Platform priority: **Kalshi first** (CFTC-regulated, US-legal, no VPN needed)
- Polymarket: Interface layer only, implemented later

## Strategy Portfolio

| Strategy | Edge Source | Needs Weather? | Risk | Priority |
|----------|------------|-----------------|------|----------|
| **B: Cross-bracket sum** | All YES prices sum < $1.00 (pure arbitrage) | No | Near-zero | **Phase 1 — first to live** |
| **A: Ultra-low bracket** | Underpriced long-shot brackets (ensemble prob >> price) | Yes (ensemble) | Low hit rate, high payoff | Phase 2 |
| **C: Ensemble edge** | Model probability vs market probability disagreement | Yes (full ensemble) | Medium (model risk) | Phase 2 |

### Strategy B — Cross-Bracket Sum Arbitrage (Priority)

On Kalshi, each weather event has 6 mutually exclusive brackets. Exactly one MUST resolve YES.
If sum(all YES prices) < $1.00, buy all brackets → guaranteed profit at resolution.

- **No weather model needed** — pure price check
- **Appears several times per week** on illiquid Kalshi markets
- **Edge per trade:** 2-8% (small but certain)
- **Win rate:** Near 100%
- **Capital requirement:** Higher (must buy all brackets)
- **Risk:** Near-zero if all orders fill; partial fill risk (mitigated with IOC or sequential fills)

Example: NYC High Temp event has 6 brackets with YES prices summing to $0.94. Buy all 6.
At resolution, one bracket pays $1.00. Profit = $0.06 per event regardless of outcome.

### Strategy A — Ultra-Low Bracket (ColdMath)

Buy YES on brackets priced 1-15 cents where ensemble says probability is higher.
Since exactly one bracket must resolve YES, even a 4-6% hit rate on ultra-cheap brackets is profitable.

- Kalshi minimum price ~3-4 cents (vs Polymarket's 0.1 cents — less extreme but still viable)
- Needs ensemble probability to confirm bracket is mispriced
- Position sizing: fractional Kelly

### Strategy C — Ensemble Edge

Use 31-member GFS ensemble via Open-Meteo to estimate true probability for each bracket.
Trade when |model_prob - market_prob| > 8%.

- Most nuanced strategy — requires model calibration
- Benefits from Kalshi's NWS Climatological Report resolution (clear settlement source)
- Higher win rate (50-70%) but requires model to be well-calibrated

## Architecture

Build on saislanchez's codebase. Extend, don't rewrite.

```
backend/
├── config.py                     # Extend with Kalshi trading params
├── data/
│   ├── kalshi_client.py          # KEEP — RSA-PSS auth (crown jewel)
│   ├── kalshi_markets.py         # KEEP — series discovery + ticker parsing
│   ├── kalshi_orders.py          # NEW — order placement + management
│   ├── weather.py                # KEEP — Open-Meteo + NWS ensemble
│   ├── weather_markets.py        # KEEP — Polymarket discovery (future)
│   ├── crypto.py                 # KEEP — BTC microstructure (future)
│   └── btc_markets.py            # KEEP — BTC 5-min (future)
├── scanner/
│   ├── opportunity.py            # NEW — unified scanner dispatching A, B, C
│   ├── strategy_a.py             # NEW — low-bracket finder (needs ensemble)
│   ├── strategy_b.py             # NEW — cross-bracket sum arbitrage (price-only)
│   └── strategy_c.py             # RENAMED from weather_signals.py — ensemble edge
├── exchange/
│   ├── base.py                   # NEW — ABC interface for any exchange
│   ├── kalshi.py                 # NEW — Kalshi implementation (Phase 1)
│   └── polymarket.py             # NEW — Stub/interface only (future)
├── core/
│   ├── scheduler.py              # KEEP — extend scan intervals per strategy
│   ├── settlement.py             # KEEP — extend for Kalshi resolution
│   └── risk.py                   # NEW — daily loss limit, position caps, concentration
├── models/
│   └── database.py               # KEEP — add Kalshi-specific fields
└── api/
    └── main.py                   # KEEP — extend endpoints for new strategies
```

### exchange/base.py — Exchange Interface

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class OrderResult:
    success: bool
    order_id: str = ""
    filled_size: float = 0.0
    filled_price: float = 0.0
    error: str = ""

class ExchangeClient(ABC):
    @abstractmethod
    async def place_order(self, ticker: str, side: str, price: float, size: float, order_type: str = "limit") -> OrderResult:
        ...

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        ...

    @abstractmethod
    async def get_positions(self) -> List[dict]:
        ...

    @abstractmethod
    async def get_balance(self) -> float:
        ...

    @abstractmethod
    async def get_orderbook(self, ticker: str) -> dict:
        ...
```

### scanner/opportunity.py — Unified Scanner

Single scan cycle per event:
1. Fetch all bracket prices for the event
2. Run Strategy B (sum check — no weather data needed)
3. Run Strategy A (find ultra-low brackets with ensemble support)
4. Run Strategy C (full ensemble edge calculation)
5. Score and rank all opportunities
6. Pass to risk manager for approval
7. Forward to execution layer

### scanner/strategy_b.py — Cross-Bracket Sum Arbitrage

```python
async def scan_bracket_sums(event_ticker: str, markets: List[dict]) -> List[Opportunity]:
    total_yes = sum(m["yes_price"] for m in markets)
    if total_yes < 1.0:
        edge = 1.0 - total_yes
        # Calculate total cost to buy all brackets
        # Return opportunity with guaranteed profit = edge * total_cost
```

No weather data. Pure price arbitrage. Fastest to implement and safest to deploy.

## Implementation Phases

### Phase 1: Scanner + Strategy B + Kalshi Execution (Days 1-4)

**Goal:** Strategy B live on Kalshi — first dollar earned.

| Day | Task | Details |
|-----|------|---------|
| 1 | Fork suislanchez repo, set up local dev | Clone, venv, pip install, verify FastAPI runs |
| 1 | Create scanner/ module skeleton | opportunity.py, strategy_b.py with type stubs |
| 1 | Implement Strategy B scanner | Fetch all brackets per event, compute YES sum, flag if < $1.00 |
| 2 | Build exchange/base.py interface | ABC with place_order, cancel, get_positions, get_balance |
| 2 | Build exchange/kalshi.py | Extend kalshi_client.py with order placement (POST /orders) |
| 2-3 | Implement Kalshi order placement | Build order payload, sign with RSA-PSS, submit, handle responses |
| 3 | Wire scanner → exchange | Strategy B opportunities auto-execute via exchange layer |
| 3 | Add risk.py skeleton | Daily loss limit, per-event concentration cap |
| 4 | Integration test | Paper-trade Strategy B on live Kalshi data |
| 4 | Deploy paper mode | Run 24h with SIMULATION_MODE=true, verify bracket sums |

**Deliverable:** Working bot that detects cross-bracket arbitrage on Kalshi and (in sim mode) would execute it.

### Phase 2: Strategy A + C Signals (Days 5-7)

**Goal:** Ensemble-based signal generation for weather markets.

| Day | Task | Details |
|-----|------|---------|
| 5 | Port weather.py ensemble pipeline | Verify Open-Meteo GFS 31-member fetch works |
| 5 | Create scanner/strategy_a.py | Find brackets priced < 15c where ensemble prob > 2x price |
| 6 | Create scanner/strategy_c.py | Rename+extend weather_signals.py, add Kalshi market support |
| 6 | Wire strategy_a into scanner | Ensemble probability + Kalshi bracket prices → edge calc |
| 7 | Unified scanner pass | One scan cycle runs B, A, C on all Kalshi events |
| 7 | Dashboard updates | Show B/A/C opportunities separately in React frontend |

**Deliverable:** Full signal pipeline for all three strategies, paper-trading mode.

### Phase 3: Kalshi Live Execution (Days 8-11)

**Goal:** Real money on Kalshi.

| Day | Task | Details |
|-----|------|---------|
| 8 | Set up Kalshi trading account | Register, deposit, generate API key + RSA key pair |
| 8 | Test kalshi_orders.py with real auth | Place tiny test order, verify fill, cancel |
| 9 | Wire Strategy B to live execution | Cross-bracket arbitrage with real orders |
| 9 | Handle partial fills | If not all brackets fill, cancel remaining, or accept partial arb |
| 10 | Wire Strategy A to live execution | Low-bracket buying with Kelly sizing |
| 10 | Wire Strategy C to live execution | Ensemble edge with entry price filters |
| 11 | Full integration test | All three strategies executing on Kalshi with $100 |

**Deliverable:** Live trading on Kalshi with all three strategies.

### Phase 4: Risk Management Hardening (Days 12-13)

| Day | Task |
|-----|------|
| 12 | Implement daily loss limit with auto-shutdown |
| 12 | Per-city concentration cap (15% of bankroll max) |
| 12 | Per-strategy trade count limits |
| 13 | Position monitoring — alert if any position drifts > 20% |
| 13 | Kill switch — API endpoint to pause all trading immediately |

### Phase 5: Validation — Paper + Live (Days 14-20)

| Days | Task |
|------|------|
| 14-20 | Run paper trading for 5-7 days against live Kalshi data |
| 14-17 | Analyze: How many Strategy B opportunities appear? What's average edge? |
| 15-18 | Analyze: Strategy A hit rate vs ensemble prediction accuracy |
| 16-19 | Analyze: Strategy C Brier score — is ensemble well-calibrated? |
| 18-20 | If Brier score > 0.25, adjust edge thresholds upward |
| 20 | Graduated live deployment: $500 capital, Strategy B first |

### Phase 6 (Future): Polymarket Support

| Task | Details |
|------|---------|
| Implement exchange/polymarket.py | Using py-clob-client SDK (from Guillermo's patterns) |
| Add proxy wallet auth | EIP-712 signing, Gnosis Safe support |
| Run Strategy A on Polymarket | Ultra-low brackets at 0.1c minimum — much higher edge |
| Cross-platform arbitrage | If same event on both platforms, detect price divergence |
| Deploy on non-US VPS | Japan or Singapore for Polymarket access |

## Cities to Cover (Kalshi)

Start with saislanchez's 5, then expand:

| Phase | Cities | Series Tickers |
|-------|--------|---------------|
| MVP | NYC, Chicago, Miami | KXHIGHNY, KXHIGHCHI, KXHIGHMIA |
| Expand | + LA, Denver | KXHIGHLAX, KXHIGHDEN |
| Full | + all available (~20) | KXHIGHTDAL, KXHIGHLAS, KXHIGHPHX, etc. |

## Key Technical Decisions

1. **Language: Python** — saislanchez's codebase is Python, ensemble/numerical libraries are Python-native, daily-resolution markets don't need Go's speed
2. **Framework: FastAPI** — already in saislanchez's stack, async-native, good for concurrent API calls
3. **Database: SQLite → PostgreSQL** — SQLite for MVP, PostgreSQL for production concurrent writes
4. **Scheduling: APScheduler** — already implemented, extend scan intervals
5. **Kalshi auth: RSA-PSS** — saislanchez's kalshi_client.py handles this correctly
6. **Weather: Open-Meteo GFS ensemble** — free, 31 members, 5 cities covered
7. **No Go code** — dropped speedgap-prototype architecture entirely

## Risk Register

| Risk | Mitigation |
|------|-----------|
| Kalshi API key takes time to get | Start registration now, build paper mode first |
| Strategy B partial fills | Limit IOC orders, accept partial arb or cancel |
| Ensemble miscalibration | Track Brier scores, raise edge threshold if > 0.25 |
| Kalshi fee structure | Model quadratic fees in edge calculation |
| Market illiquidity | Skip if orderbook depth < $200 |
| Rate limiting | Kalshi rate limits unknown — start conservative |
| Daily loss spiral | Hard daily loss limit with auto-shutdown |
| Bot crash during order sequence | Position reconciliation on restart (check open orders) |

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Strategy B opportunities/week | >= 3 | Count of sum < $1 events |
| Strategy B avg edge | >= 3% | Average (1.0 - sum_yes) across fills |
| Strategy A hit rate | >= 5% | Correct bucket predictions / total A trades |
| Strategy C Brier score | <= 0.20 | Tracked via calibration module |
| Weekly P&L (after $500 deployed) | Positive | net_pnl over 7 days |
| Max drawdown | < 10% of bankroll | Peak-to-trough balance |
| Bot uptime | >= 99% | Minutes running / minutes elapsed |

## Dependencies

- Kalshi account + API key + RSA key pair (user action needed)
- Python 3.10+
- Open-Meteo API (free, no key required)
- NWS API (free, User-Agent header only)
- FastAPI + uvicorn (in requirements.txt)
- cryptography (for RSA-PSS signing)
- httpx (async HTTP client)
- numpy + scipy (ensemble statistics)

## What We're NOT Building

- No Go code (speedgap-prototype is archived)
- No Polymarket execution (interface only, future phase)
- No BTC 5-min strategy (keep saislanchez's code but don't activate)
- No AI/LLM signal augmentation (Claude/Groq integration is decorative, skip)
- No economics pipeline (saislanchez's ARCHITECTURE.md concept, not implemented)
- No ECMWF/HRRR blending (Open-Meteo GFS 31-member is sufficient for MVP)
