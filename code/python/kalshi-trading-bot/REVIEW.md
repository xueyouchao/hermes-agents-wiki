# Independent Architecture Review — Kalshi Weather Arbitrage Trading Bot

**Reviewer:** Senior Software Architect  
**Date:** 2026-04-26  
**Scope:** Full codebase review focusing on Strategy B readiness for live trading  

---

## A. Architecture Gaps

### A1. CRITICAL: strategy_b_job() bypasses the TradingEngine and RiskManager entirely
The `weather_scheduler.py` `strategy_b_job()` creates a fresh `KalshiExchange()`, calls `scan_strategy_b()` directly, and only LOGS opportunities — it never passes them through risk checks or execution. Meanwhile, `weather_arbitrage_job()` uses the `TradingEngine.run_cycle()` which DOES go through risk→execute. Result: the 2-minute fast scan is **completely disconnected from execution**. If you want Strategy B to actually trade on its 2-minute cadence, only the 5-minute full scan will execute — making the 2-minute timer pointless.

### A2. KalshiExchange() instantiated repeatedly without session reuse
Every scheduler job creates a new `KalshiExchange()` → new `KalshiClient()` → new `httpx.AsyncClient()`. The client is designed with lazy session creation but NEVER CLOSED after the job completes. Each 2-minute cycle leaks an HTTP client session. Over hours/days, this accumulates unclosed file descriptors and connections.

### A3. No Strategy A or C implementation
`opportunity_scanner.py` stubs return `[]` for strategies A and C. This is documented as "Phase 2" but the scanner framework has hard-coded branching logic for these strategies. Weather signals and ensemble data are fetched but never used by any live strategy.

### A4. Exchange abstraction leaks Kalshi specifics
`strategy_b.py` imports `CITY_SERIES` and `_parse_kalshi_ticker` directly from `backend.common.data.kalshi_markets` — these are Kalshi-specific. The "exchange abstraction" is bypassed when discovering which series to scan. A true Polymarket swap would require rewriting the scanner.

### A5. No state persistence between cycles
The `TradingEngine` stores `_results` in memory (capped at 1000). Risk manager's `DailyStats` are in-memory only. If the process restarts, all daily risk tracking resets to zero — effectively allowing the bot to double its daily loss limit after a crash+restart.

### A6. Two parallel scan paths for Strategy B
`opportunity_scanner.py` defines `scan_strategy_b()` which wraps the real `strategy_b.scan_strategy_b()`, while `weather_scheduler.py` also calls `strategy_b.scan_strategy_b()` directly. This dual path creates confusion about which code actually runs.

---

## B. Code Quality Issues

### B1. CRITICAL: Race condition — strategy_b_job and weather_arbitrage_job can run concurrently
Both are scheduled with `max_instances=1` per job, but they are DIFFERENT jobs. Both can execute Strategy B simultaneously. If both create `KalshiExchange()` and place orders, the bot could double-trade the same arbitrage opportunity. APScheduler's `max_instances` is per-job-id, not global.

### B2. Global mutable state
`weather_scheduler.py` uses module-level globals (`scheduler`, `engine`, `event_log`). The `_CACHED_CITIES` in `strategy_b.py` uses a global mutable cache. These create hidden coupling and make testing unreliable.

### B3. Daily stats never reset
`RiskManager._daily_stats` is initialized once and never reset. The `date` field is set in `__post_init__` but never checked. After midnight, the daily loss counter, trade count, and consecutive loss tracking continue accumulating. A bot running for 3 days would have 3 days of losses in a "daily" stat.

### B4. KalshiClient retry logic has a flaw on final attempt
In `_request_with_retry`, after the last retry fails with a 429/5xx, the loop ends and falls through to `response.raise_for_status()` — but `response` is the LAST failed response, not the current one. If the loop exhausted all retries on connection errors (the except branch raises on the last attempt), `response` may be unbound, causing an `UnboundLocalError`.

### B5. `datetime.utcnow()` is deprecated
Used throughout (database.py, weather.py, settlement.py). Should use `datetime.now(timezone.utc)`. The settlement code uses `datetime.utcnow()` while risk.py uses `datetime.now(timezone.utc)` — inconsistent timezone handling.

### B6. No type checking on API responses
`kalshi_client.py` returns `response.json()` without validation. If Kalshi changes their API shape, the bot will crash with opaque `KeyError` or `TypeError` deep in processing rather than a clear parse error at the boundary.

### B7. Silent failures everywhere
`KalshiExchange.get_positions()` returns `[]` on error. `get_balance()` returns `Balance()` (all zeros) on error. `get_orderbook()` returns `OrderBook(ticker=ticker)` on error. The caller cannot distinguish "no positions" from "API crashed." Trading on stale/zero data is dangerous.

### B8. `_parse_kalshi_ticker` called with empty string for city_key
In `strategy_b.py` line 74: `_parse_kalshi_ticker(ticker, "")` — the empty string city_key is never used by the function (it only uses the ticker), but this is misleading and makes the code hard to understand.

---

## C. Trading Logic Flaws — Could Lose Money

### C1. CRITICAL: Partial fill creates unhedged exposure — the biggest risk
Strategy B buys YES on ALL brackets. If 5 of 6 brackets fill but 1 fails (IOC order), you own 5 long YES positions with NO guaranteed payout. The code marks this as `PARTIAL` and logs a warning but DOES NOT attempt to:
- Cancel the filled brackets
- Sell the filled positions
- Hedge the exposure
The `result["executed"] = True` on partial fills means the risk manager records these as completed trades. You now have directional risk on 5 brackets that are unlikely to all resolve YES.

### C2. CRITICAL: IOC orders at ASK price may not fill
Strategy B uses `OrderType.IOC` at `bracket.yes_price` (the ASK price). But the ask price shown in the API may be stale. IOC means "fill immediately at this price or cancel." If the orderbook has moved even 1 cent, the IOC misses, creating the partial fill scenario above. The bot should either use limit orders with GTC (and cancel after all fill) or implement a two-phase commit: place all as limit orders, verify all filled, then cancel stragglers.

### C3. CRITICAL: Edge calculation ignores the B (bottom) vs T (top) bracket distinction
Kalshi uses "B" (bottom boundary = above threshold) and "T" (top boundary = below threshold). The `_parse_kalshi_ticker` distinguishes these, but `check_cross_bracket_arb` treats all brackets identically — it just sums `yes_price`. This works ONLY if the set of brackets is exactly complete (covers the full temperature range with no gaps and no overlaps). If Kalshi adds or removes a bracket between scans, the sum of YES prices < $1.00 could be normal (incomplete bracket set) rather than arbitrage.

### C4. The "guaranteed $1 payout" assumption is wrong for incomplete bracket sets
The docstring says "exactly one bracket MUST resolve YES" guaranteeing profit. This is ONLY true if the brackets are mutually exclusive AND collectively exhaustive. If you filtered out brackets (low volume, wide spread, near-certain resolution), the remaining brackets may not cover the full range. Buying YES on 4 out of 6 brackets means the actual temp could land in the 2 filtered-out brackets — and you get $0 payout.

The `_extract_bracket_markets` filter removes brackets with `yes_ask > 0.98` or `< 0.02` or low volume. After filtering, `check_cross_bracket_arb` only checks the remaining brackets. If the actual temperature falls in a filtered bracket, you lose on ALL positions.

### C5. Fee rate is zero by default — Kalshi DOES charge fees
`KALSHI_FEE_RATE: float = 0.0` in config.py. Kalshi charges $0.01 per contract side on trades under $1. With 6 brackets at 1 contract each, that's $0.06 in fees on a trade that might only net $0.04 in edge. The fee-adjusted edge check exists in the code but is useless with fee_rate=0.

### C6. Concentration check uses substring matching
`risk.py` line 219: `if event_key in pos_key` — this is a substring match. If an event_key is "KXHIGHNY-26MAY01", it would also match "KXHIGHNY-26MAY011" or "SOME_KXHIGHNY-26MAY01_OTHER". Should use exact or prefix-delimited matching.

### C7. Risk manager uses INITIAL_BANKROLL (static) instead of actual balance
`RiskManager.bankroll` returns `settings.INITIAL_BANKROLL` unless overridden in testing. After winning trades, the real bankroll increases, but the risk manager still uses the initial $10,000. This means:
- Concentration limits are too tight after wins
- But more critically: after losses that aren't recorded in daily_stats (e.g. from a previous session), the risk manager thinks it has MORE capital than it actually does

### C8. Settlement routes weather trades through Polymarket by default
`settlement.py` `check_weather_settlement` defaults `platform` to `"polymarket"` if not set. But Strategy B trades on Kalshi. If the Trade record doesn't have `platform="kalshi"` set, it will try to settle against Polymarket's API, which won't find the Kalshi market.

### C9. No deduplication of opportunities across cycles
If Strategy B finds the same arbitrage in consecutive 2-minute cycles, the bot will trade it again. The risk manager's concentration check should catch this, but it relies on `current_positions` which comes from `exchange.get_positions()` — which silently returns `[]` on API errors (see B7). On an API error, the bot trades the same opportunity repeatedly.

---

## D. Missing Infrastructure

### D1. No structured logging / log aggregation
All logging goes to Python's `logging` module with basic config. No JSON structured logs, no log levels per module, no log file rotation. In production, you'll need to tail logs manually.

### D2. No alerting
No integration with PagerDuty, Slack, Discord, email, or any notification system. When:
- Kill switch activates → no alert
- Daily loss limit hit → no alert
- Partial fills with unhedged exposure → no alert
- Exchange API errors → no alert beyond log lines
You will discover problems only by checking the terminal.

### D3. No health check endpoint
The FastAPI app has no `/health` endpoint. Deployment orchestrators (Railway, Docker, k8s) can't determine if the bot is alive.

### D4. No graceful shutdown
`stop_scheduler()` calls `scheduler.shutdown(wait=False)`. This abandons any in-progress trade execution. Partial fills from the current cycle won't be tracked or reconciled.

### D5. No position reconciliation on startup
`weather_scheduler.py` has a comment about reconciling positions but the actual implementation is a no-op. After a crash, the bot has no idea what positions it holds, which orders are open, or what its actual balance is.

### D6. No database migration strategy
`database.py` uses `ALTER TABLE` for schema changes with SQLite-specific workarounds. No Alembic or formal migrations. Schema drift between environments is inevitable.

### D7. No metrics/monitoring
No Prometheus metrics, no Grafana dashboard, no tracking of:
- Orders placed/filled/rejected
- Edge captured vs realized
- Slippage per trade
- API latency
- Position exposure over time

### D8. FastAPI app is a dashboard only — trading runs in a separate process
`run.py` starts uvicorn (API), while `trade.py` starts the scheduler (trading). These are two separate processes that share a SQLite DB but have no RPC between them. The API can show stale data, and you can't trigger trades or toggles from the API.

---

## E. Test Coverage Gaps

### E1. MockExchange returns same data for ALL cities — test passes by accident
`test_trading_pipeline.py` MockExchange.get_event_markets() returns the same 6 NYC brackets regardless of which series_ticker is requested. This means every city "finds" the same arbitrage. The test asserts `len(opportunities) == 5` because there are 5 configured cities — NOT because 5 actual arbs exist. In production, 5 arbs simultaneously is extremely unlikely.

### E2. No test for partial fill handling
The MockExchange always returns `success=True` and fills completely. There is zero test coverage for the most dangerous scenario: partial fills creating unhedged exposure.

### E3. No test for the stale data / API failure scenarios
MockExchange always returns valid data. No test verifies what happens when:
- `get_positions()` returns `[]` (is it empty or crashed?)
- `get_balance()` returns all zeros
- `place_order()` returns an error for one bracket in a 6-bracket arb

### E4. No test for daily stat reset
The daily stats never reset in production. No test checks what happens across "day boundaries."

### E5. No test for IOC order behavior
IOC orders are critical to Strategy B execution but no test validates that IOC is used, or what happens when IOC orders expire unfilled.

### E6. Risk manager tests don't test the actual bankroll
Tests inject bankroll overrides but never test the default path where `settings.INITIAL_BANKROLL` is used as a static value.

### E7. No integration test with real Kalshi API shape
All tests use synthetic data. The actual Kalshi API response format (prices in cents, nested structures) is only tested by the mock which returns simplified data.

### E8. No settlement test for Strategy B
Settlement is tested for single-market BTC trades (Polymarket). There is zero test coverage for settling a cross-bracket arbitrage position on Kalshi.

---

## F. Security Concerns

### F1. RSA private key loaded from filesystem with no validation
`kalshi_client.py:_load_private_key()` reads the PEM file directly. If the path is wrong or the file is corrupted, it fails with an opaque cryptography error. No validation that the key works before critical trading operations.

### F2. No API key rotation mechanism
If the Kalshi API key is compromised, there's no way to rotate it without restarting the process. Keys are loaded from environment variables once at startup.

### F3. Sim mode flag can be CHANGED at runtime
`trade.py` line 135: `settings.SIMULATION_MODE = True` — Pydantic Settings is mutable. Any code path could accidentally flip this to `False`. The FastAPI API has no auth — anyone hitting the API could potentially modify settings.

### F4. FastAPI dashboard has NO authentication
`api/main.py` exposes endpoints for kill switch, position data, trade history, and bot state with ZERO authentication. Anyone with network access can:
- See your positions and P&L
- Toggle the kill switch
- View your trading strategy details

### F5. SQL injection risk in migration code
`database.py` `ensure_schema()` uses string interpolation for column types: `f"ALTER TABLE signals ADD COLUMN {col} {coltype}"`. While the current values are hard-coded, this pattern is dangerous if extended.

### F6. API keys in process memory
All API keys live in `settings` object for the lifetime of the process. No key zeroing after use, no secure string handling. A memory dump exposes all credentials.

---

## G. Prioritized Fix List — Top 10 Before Going Live

### 1. FIX: Partial fill exposure (C1, C2) — CRITICAL, will lose money
**What:** When Strategy B gets partial fills (e.g., 5 of 6 brackets), you have unhedged directional risk.  
**Fix:** Implement a two-phase commit:  
- Phase 1: Place all orders as LIMIT (not IOC) with a tight timeout  
- Phase 2: After timeout, check fills. If any bracket unfilled, immediately cancel ALL remaining and sell filled positions at market.  
- Only mark COMPLETE if all brackets fill.

### 2. FIX: Incomplete bracket set invalidates arb guarantee (C3, C4) — CRITICAL
**What:** After filtering out low-volume/near-certain brackets, the remaining set may not be mutually exclusive and collectively exhaustive. The arbitrage guarantee breaks.  
**Fix:** After filtering, verify completeness:  
- Parse all bracket thresholds  
- Confirm they form a contiguous range (no gaps, no overlaps)  
- Only declare arb if the bracket set is complete  
- Alternative: don't filter ANY bracket for Strategy B; accept low-volume brackets as the cost of completeness.

### 3. FIX: Race condition on dual Strategy B execution (B1) — HIGH
**What:** `strategy_b_job` and `weather_arbitrage_job` can both run Strategy B concurrently, risking double-trades.  
**Fix:** Use an asyncio.Lock around the entire scan→execute cycle. Or: remove `strategy_b_job` and only run Strategy B through the TradingEngine path.

### 4. FIX: Daily stats never reset (B3) — HIGH
**What:** Daily loss limits, trade counts, and consecutive losses persist indefinitely. After 3 days, you've "spent" 3x the intended daily budget.  
**Fix:** Add a date check at the top of `is_trading_allowed()`. If `self._daily_stats.date != today`, reset the stats.

### 5. FIX: Fee rate is zero — Kalshi charges fees (C5) — HIGH
**What:** With `KALSHI_FEE_RATE=0.0`, the edge calculation assumes free trades. Kalshi charges ~$0.01/contract.  
**Fix:** Set `KALSHI_FEE_RATE=0.01` and verify edge is still positive after fees on realistic trades.

### 6. FIX: Repeated KalshiExchange instantiation leaks sessions (A2) — HIGH
**What:** Every scheduler job creates a new `KalshiExchange()` + `KalshiClient()` + `httpx.AsyncClient()` that's never closed.  
**Fix:** Make TradingEngine long-lived. Share one KalshiExchange instance across all jobs. Close it on shutdown.

### 7. FIX: Balance/position API errors silently return zero/empty (B7, C7) — HIGH
**What:** `get_positions()` returning `[]` on error means risk checks run with wrong data. `get_balance()` returning zeros means bankroll tracking is wrong.  
**Fix:** Raise exceptions on API errors instead of returning defaults. Let the caller handle failures explicitly. Or return `Result` types that distinguish success from failure.

### 8. FIX: Settlement platform defaulting to Polymarket (C8) — MEDIUM
**What:** Strategy B places trades on Kalshi but settlement may try Polymarket if `platform` isn't persisted.  
**Fix:** Ensure the Trade record gets `platform="kalshi"` when Strategy B executes. Add an explicit check in `settle_pending_trades()`.

### 9. FIX: Authentication on FastAPI dashboard (F4) — MEDIUM
**What:** Anyone with network access can toggle kill switch, view positions, see P&L.  
**Fix:** Add API key or basic auth middleware. Bind to 127.0.0.1 instead of 0.0.0.0 by default.

### 10. FIX: No alerting for critical events (D2) — MEDIUM
**What:** Kill switch, daily loss limits, partial fills, API errors — all invisible without checking logs.  
**Fix:** Add at minimum: file-based alerts, or a webhook to Slack/Discord on critical events. Key events: risk halt, partial fill, daily loss exceeded, API auth failure.

---

## Summary Verdict

**The codebase is well-structured and thoughtfully designed**, with clean abstractions and good separation of concerns. The test suite validates core logic. The risk manager has extensive safety mechanisms.

**However, the bot is NOT ready for live trading with real money.** The fundamental issue is partial fill handling (items 1-2): buying YES on 5 of 6 brackets gives you directional risk, not arbitrage. This alone could cause significant losses in a single event. Combined with the race condition (item 3), stale risk data (items 4, 7), and missing fees (item 5), the expected win rate of "near 100%" could easily be 60% or less in practice.

The recommended path: fix items 1-5 before any live deployment, then run in simulation with real Kalshi API data for at least 48 hours to validate bracket completeness and fill rates.