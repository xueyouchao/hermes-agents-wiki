---
title: Risk, Scanning & Code Review — Gap Analysis
created: 2026-04-26
updated: 2026-04-26
type: review
branch: weather-arbitrage
---

# Risk, Scanning & Code Review — Gap Analysis

Sourced from:
1. QuantVPS blog on automated Polymarket trading (risk controls)
2. ArbBets product on Polymarket (scanning improvements)
3. minimax-m2.7 codebase review (bugs, architecture, testing gaps)

---

## 1. RISK CONTROL GAPS (from QuantVPS + Code Review)

### What We Have
| Control | Status |
|---------|--------|
| Daily loss limit ($300) | PRESENT |
| Max trade size ($100) | PRESENT |
| Max event concentration (15%) | PRESENT (but dead code — see bug) |
| Max daily trades (50) | PRESENT |
| Max pending trades (20) | PRESENT |
| Min edge threshold (2%) | PRESENT |
| Kelly fraction cap (0.25) | PRESENT |
| Kill switch | PRESENT |
| Kelly-based position sizing (Strategy B) | PRESENT |

### What We're MISSING (Priority Order)

**P0 — Must Fix Before Live Trading:**

1. **Kalshi fee modeling in edge calculation** — `strategy_b.py:155` assumes 0% fees. If `sum(YES) = $0.97` and there's a 1% fee, edge evaporates. Need `KALSHI_FEE_RATE` config var (even if 0%) and subtract from calculated edge.

2. **Circuit breaker for extreme volatility** — No mechanism to detect abnormal market conditions and auto-pause. A black swan event could trigger a burst of false arb signals.

3. **Stop-loss per position** — We track daily realized P&L but have no per-position stop-loss to auto-cut a losing trade.

4. **Max drawdown from high-water mark** — Our daily loss limit is a flat $300. We need a drawdown-from-peak metric (e.g., 10% drawdown pauses trading) to catch slow bleeds.

5. **Liquidity / slippage filter** — No check for order book depth before placing trades. Markets under $1,000 in volume should be skipped. Position size should be 1-5% of available liquidity.

6. **Auto-cancel open orders on kill/daily-limit breach** — When `is_trading_allowed()` returns False, we don't cancel pending orders. Stale orders could execute after the halt.

**P1 — Should Fix Soon:**

7. **Persist risk state to database** — `_daily_stats` is in-memory only. A crash mid-day resets the daily loss counter, bypassing limits. Must write to `Trade` / `BotState` tables.

8. **Consecutive loss limit** — Pause after N consecutive losing trades (e.g., 5).

9. **Rolling window loss limit** — Add hourly or 4-hour caps, not just daily.

10. **Rate limit / exponential backoff** — `kalshi_client.py` creates a new `httpx.AsyncClient` per request with no retry on 429/5xx. Need shared session + `tenacity` backoff.

11. **FOK order type enforcement for Strategy B** — Currently using IOC. Fill-or-Kill prevents "legged" partial arb positions entirely.

12. **Position size relative to order book depth** — `max_trade_size` is a flat dollar amount. Should be `min($100, 5% of available_liquidity)`.

**P2 — Nice to Have:**

13. **Fill rate & slippage tracking** — Log actual vs expected fill prices. Essential for monitoring execution quality.

14. **Alerting system** — Telegram/Discord notifications on kill switch activation, daily limit breach, API failures.

15. **Gradual scaling / reduced-size mode** — A "dry run" mode that operates at 10% of normal sizing for live testing.

16. **Portfolio-level exposure cap** — Max percent of bankroll deployed across ALL positions at once (not just per-event).

---

## 2. SCANNING IMPROVEMENTS (from ArbBets Analysis)

### What ArbBets Does That We Don't

| Feature | ArbBets | Our Scanner | Priority |
|---------|---------|-------------|----------|
| Orderbook ask prices (not mid/last) | Uses best ask | Uses `last_price`/`mid` | **P0** |
| Liquidity/volume filtering | Skips empty asks | No volume filter | **P0** |
| Skip-reason tracking | Detailed `skip_reasons` | Silent skip | **P1** |
| Min profit after fees | `min_profit` param | No fee modeling | **P0** |
| Bet sizing & ROI calculation | Exact allocation | Kelly approx | **P1** |
| Combination strategy (YES/NO combos) | Enumerates all 2^n | Buy YES only | **P2** |
| Cross-exchange matching | Kalshi↔Polymarket↔Opinion | Kalshi only | **P3** |
| Direct trade links | `url_a`/`url_b` deep links | No URLs generated | **P2** |
| +EV detection | Model vs market probability | Not implemented | **P4** |
| Real-time WebSocket scanning | Every second | APscheduler 2-5min | **P3** |

### Priority Actions

**P0 — Must Fix:**
- Switch from `last_price` to `yes_ask` (best ask price) in edge calculation. Arb opportunities that appear at mid/last may not be executable at the ask.
- Add volume/liquidity filtering: skip markets with < $1,000 volume or empty orderbook.
- Add `KALSHI_FEE_RATE` to profit calculation: `net_edge = 1.00 - sum(yes_ask) - total_fees`.

**P1 — Should Fix:**
- Add `skip_reasons` list to `Opportunity` — track why markets were skipped (no data, too thin, expired, duplicate).
- Calculate exact ROI: `profit_per_dollar = 1.00 - sum(YES) - fees`, `roi_pct = profit / total_cost`.
- Add `min_profit` threshold config (default: $0.02 profit per set after fees).

**P2 — Consider:**
- Enumerate YES/NO combinations across brackets for maximum guaranteed profit.
- Generate Kalshi market URLs in scanner output for quick verification.

---

## 3. CODE REVIEW FINDINGS (from minimax-m2.7)

### Bugs

1. **`risk.py:134` — Floor of 1 contract overrides risk cap**: When `adjusted_size < 1`, code sets `adjusted_size = 1`, bypassing the intended cap. Should REJECT (return False, 0, "below minimum size") instead of rounding up.

2. **`risk.py:127` — Strategy B size formula uses `max(yes_price)`**: `max_trade_size / max(b.yes_price for b in opp.brackets)` divides by the most expensive bracket, producing the fewest sets. This is safe but suboptimal — it underestimates how many full sets we can afford. Should use `total_cost_per_set` instead.

3. **`trader.py:296` — Direction heuristic parses reasoning string**: `_execute_single_market` decides YES/NO by checking `"YES" in opp.reasoning.upper()`. This is brittle. Should add `direction` field to `Opportunity` model.

4. **`trader.py:73`, `risk.py:46`, `opportunity.py:87` — `datetime.utcnow()` deprecated**: Use `datetime.now(UTC)`.

5. **`kalshi.py:91` — `filled_price_cents / 100.0` unit ambiguity**: Verify whether Kalshi returns `filled_price` in cents or dollars. If dollars, division by 100 produces wrong prices.

6. **`risk.py:97-98` — Concentration check is dead code**: `approve_opportunity()` has a `current_positions` parameter, but `TradingEngine.run_cycle()` never passes it. The concentration limit does nothing.

### Missing Error Handling

7. **`kalshi_client.py` — No retry logic**: New `httpx.AsyncClient` per request, no exponential backoff on 429/5xx.

8. **`trader.py` — No timeout on `place_order` calls**: A hung order in `_execute_strategy_b` blocks the entire cycle. Need `asyncio.wait_for` timeout.

9. **`trader.py:252` — Partial fills have no defensive action**: When some brackets fill and others don't, remaining brackets are still purchased, creating an imbalanced position. No cancellation of pending orders.

10. **`opportunity_scanner.py:19` — Function name shadows import**: `scan_strategy_b` function shadows the imported `strategy_b.scan_strategy_b`.

### Architecture Issues

11. **No persistent state**: `RiskManager._daily_stats` and `TradingEngine._results` are in-memory. On crash, daily loss tracking resets. Must persist to database.

12. **No database writes in new pipeline**: Old `scheduler.py` writes to `Trade`/`BotState` tables. New `TradingEngine` only logs — no trade persistence.

13. **`KalshiClient` creates new connection per request**: Should share a single `httpx.AsyncClient` session.

14. **No transaction atomicity for Strategy B**: Buying 5 brackets sequentially means prices can move between order 1 and order 5. Should use `asyncio.gather()` for concurrent placement.

15. **`_pending_orders` dict in `kalshi.py` never cleaned**: Successful IOC fills leave stale entries. Memory leak.

### Documentation Inaccuracies

16. **`config.py` docstring says "BTC 5-min trading bot"**: Copy-paste leftover; should say "Kalshi Weather Arbitrage Bot".

17. **Doc claims `PositionSide` in `base.py`**: This enum doesn't exist in the current code.

18. **Doc lists `StrategyBScanner` class**: Actual code uses `scan_strategy_b()` function.

### Test Coverage Gaps

19. No tests for `kalshi.py` (exchange client, real order placement)
20. No tests for `kalshi_client.py` (auth, request signing)
21. No tests for Strategy B partial fill path
22. No tests for `_extract_bracket_markets` (raw data parsing)
23. No tests for `opportunity_scanner.py` dispatcher
24. No tests for `scheduler_v2.py` lifecycle
25. No negative/risk edge case tests (size=0, cost=0, empty brackets)
26. No test for `trade.py` CLI argument parsing
27. `MockExchange` doesn't simulate failures (timeouts, rejections, partial fills)

---

## 4. PRIORITY ACTION ITEMS

### Before Live Trading (Must Do)
| # | Item | Effort |
|---|------|--------|
| 1 | Add fee modeling to Strategy B edge calc | Low |
| 2 | Use orderbook ask prices, not mid/last | Low |
| 3 | Add liquidity/volume filter (skip < $1k vol) | Low |
| 4 | Fix `adjusted_size < 1` floor → reject instead | Low |
| 5 | Fix concentration check (pass positions) | Low |
| 6 | Add `asyncio.wait_for` timeout on orders | Low |
| 7 | Persist risk state + trades to database | Medium |

### Should Do Soon
| # | Item | Effort |
|---|------|--------|
| 8 | Circuit breaker for extreme volatility | Medium |
| 9 | Stop-loss per position | Medium |
| 10 | Skip-reason tracking in scanner | Low |
| 11 | Add `direction` field to `Opportunity` | Low |
| 12 | Share `httpx.AsyncClient` session | Low |
| 13 | Retry + rate limiting on API calls | Medium |
| 14 | Fix `datetime.utcnow()` deprecation | Low |
| 15 | Deprecate/remove old `scheduler.py` | Low |

### Nice to Have
| # | Item | Effort |
|---|------|--------|
| 16 | Telegram/Discord alerts | Medium |
| 17 | Fill rate & slippage tracking | Medium |
| 18 | Position size as % of order book depth | Medium |
| 19 | YES/NO combination enumeration | Medium |
| 20 | Cross-exchange market matching | High |
| 21 | WebSocket real-time scanning | High |
| 22 | +EV detection with external forecasts | High |