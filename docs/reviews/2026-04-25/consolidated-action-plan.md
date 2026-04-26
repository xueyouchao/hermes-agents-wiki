# SpeedGap Prototype — Consolidated Action Plan

**Date:** 2026-04-25
**Sources:** 5 review reports (deepseek-v4-flash, glm-5.1, minimax-m2.7, combined code review, glm-5.1 architecture review)
**Method:** All findings merged, deduplicated, and filtered. Only items that are genuinely correct and actionable are included. Phantom issues and low-impact suggestions are excluded.

---

## How This Was Derived

| Source Report | Type | Items Covered |
|---------------|------|---------------|
| review-deepseek-v4-flash.md | Code review | 5 critical, 9 warning, 10 suggestion |
| review-glm-5.1.md | Code review | 4 critical, 11 warning, 13 suggestion |
| review-combined.md | Merged code review | 6 critical, 8 warning, 9 suggestion |
| architecture-review-glm-5.1.md | Architecture review | 6 architecture issues, 7 improvements, 5 ideas |
| architecture-review-minimax27.md | Architecture review | 7 critical issues, 6 improvements, 5 ideas |

Many findings overlap across reports. I have merged them into single items with attribution.

---

## P0 — Must Fix (system is semantically broken without these)

### P0-1. Price comparison is apples-to-oranges (ALL architecture reviewers agree)

**The core arbitrage logic is wrong.** The screener compares:
- OKX BTC-USDT spot price (~$78,000)
- Polymarket YES token price (0.0–1.0, e.g. $0.52)

These are fundamentally different instruments. The current code "solves" this with:
```go
scaled := val / 0.52 * 78000.0
```
This linear heuristic only works when BTC is exactly $78K and the token price is exactly $0.52. It produces phantom spreads otherwise.

**What the spread actually is:**
```
implied_prob  = Polymarket YES token price (0.0–1.0)
actual_prob   = N(d2) from Black-Scholes using OKX spot + volatility + time-to-expiry
spread_bps    = (implied_prob - actual_prob) * notional * 10000
```

**Action:** Replace `valueobject.CalculateSpread` with a probability-vs-probability comparison. Add:
- `valueobject.ImpliedProbability` struct (Source, Probability, Strike, Expiry, RawPrice)
- `service.ActualProbFromSpot(spot, strike, vol, tte)` using Black-Scholes N(d2)
- Remove the `0.52 * 78000.0` scaling heuristic from all 3+ files

**Files to change:** `internal/domain/valueobject/spread.go`, `polymarket/client.go`, `polymarket/clob_client.go`, `polymarket/clob_types.go`

### P0-2. No HTTP status code checks (ALL code reviewers agree)

Both OKX and Polymarket HTTP clients decode response bodies without checking `resp.StatusCode`. A 429/403/500 response silently decodes into a zero struct, producing garbage prices that propagate through the spread calculator.

**Action:** After every `resp, err := client.Do(req)`, add:
```go
if resp.StatusCode < 200 || resp.StatusCode >= 300 {
    body, _ := io.ReadAll(resp.Body)
    resp.Body.Close()
    return fmt.Errorf("HTTP %d: %s", resp.StatusCode, string(body[:200]))
}
```

**Files to change:** `internal/infrastructure/okx/client.go`, `internal/infrastructure/polymarket/clob_client.go`

### P0-3. Zero-price guards (ALL code reviewers agree — silent parse failures)

Multiple parse functions silently return 0 on failure:
- `strconv.ParseFloat` in `clob_types.go:59` — discards error
- `fmt.Sscanf` in `okx/client.go:63-64` — discards error
- `fmt.Sscanf` in `binance/client.go:59-60` — discards error

A zero price propagating into `CalculateSpread` causes division-by-near-zero, producing garbage bps values.

**Action:** Replace `fmt.Sscanf` with `strconv.ParseFloat`. Return errors on parse failure. Skip price updates when bid or ask is 0.

**Files to change:** `okx/client.go`, `clob_types.go`, `binance/client.go`

---

## P1 — High Impact (system can't function as intended without these)

### P1-1. Replace REST polling with WebSocket (ALL architecture reviewers)

OKX REST poll is every 2s, Polymarket every 3s. In 2 seconds BTC can move $50–200. A 274 bps spread can flip sign in 100ms. For a system named "speed-gap", sub-second latency is the whole point.

**Action:**
- OKX WebSocket: `wss://ws.okx.com:8443/ws/v5/public`, subscribe to `tickers` channel for `BTC-USDT`
- Polymarket CLOB WebSocket for order book delta updates
- Reuse `gorilla/websocket` (already in go.mod, currently only used by dead Binance client)

**Files to change:** `internal/infrastructure/okx/client.go` (rewrite `StreamBTCUSDT`), new `internal/infrastructure/polymarket/ws_client.go`

### P1-2. Connect LLM signal to execution (ALL reviewers agree)

The LLM fires every 20s and logs a signal, but it never influences the screener or execution. The `LLMSignal` VO is never used in the main loop. The "reasoning-gap" strategy is non-functional.

**Action:** Add a shared signal holder that the screener or net router can read:
```go
type SignalFilter struct {
    latest *valueobject.LLMSignal
    mu     sync.RWMutex
}

func (f *SignalFilter) Update(s *valueobject.LLMSignal) {
    f.mu.Lock()
    defer f.mu.Unlock()
    f.latest = s
}

func (f *SignalFilter) Enrich(opp *aggregate.Opportunity) *aggregate.Opportunity {
    f.mu.RLock()
    defer f.mu.RUnlock()
    if f.latest == nil || f.latest.Action == "HOLD" {
        return nil // skip
    }
    opp.LLMSignal = f.latest
    return opp
}
```

Wire the LLM goroutine to write via `SignalFilter.Update()` and the main loop to call `SignalFilter.Enrich()` before `netRouter.PaperOnly()`.

**Files to change:** `cmd/speedgap/main.go`, new `internal/domain/service/signal_filter.go`

### P1-3. Add Executor interface (glm-5.1 arch + minimax-27)

`NetRouter.PaperOnly` directly does `fmt.Printf`. No abstraction for execution. To go live you'd need to rewrite it.

**Action:**
```go
type Executor interface {
    Execute(ctx context.Context, opp *aggregate.Opportunity, okxP, polyP *valueobject.Price) (ExecutionResult, error)
}

type ExecutionResult struct {
    Direction string
    GrossBps  float64
    NetBps    float64
    Leg1Fill  string
    Leg2Fill  string
}
```
Implementations: `PaperExecutor` (current behavior), `OKXExecutor`, `PolymarketExecutor`.

Also fixes: `PaperOnly` currently returns a `string` instead of a struct (noted by glm-5.1 S13).

**Files to change:** `internal/engine/net_router.go`, new `internal/domain/service/executor.go`

### P1-4. Fix risk manager (ALL reviewers agree)

`risk.Manager.currentUSD` starts at 0 and is never incremented. The position limit check always passes. The risk manager is completely inert.

The notional calculation is also wrong: `notional := absBps * 10.0` — "1 bps = $10" is a made-up heuristic that doesn't correspond to any real position sizing.

**Action:**
- Add `RecordTrade(notional float64)` method that increments `currentUSD`
- Replace the heuristic notional with a real calculation based on position size and spread
- Wire `RecordTrade` into the main loop after each paper execution

**Files to change:** `internal/infrastructure/risk/manager.go`, `cmd/speedgap/main.go`

---

## P2 — Important Cleanup (code quality, safety, correctness)

### P2-1. Add unit tests for domain layer (ALL reviewers agree)

Zero test files in the entire project. The domain layer is pure functions with zero dependencies — trivially testable.

**Action:** Add table-driven tests for:
- `valueobject.CalculateSpread` — spread math correctness
- `service.OpportunityScreener.Screen` — dedup and threshold logic
- `risk.Manager.Evaluate` — position limit boundary cases
- `llm.extractJSON` — various LLM output formats (plain JSON, markdown-fenced, prose with braces)
- `polymarket.parsePolymarketPriceStr` — edge cases

**Files to add:** `internal/domain/valueobject/spread_test.go`, `internal/domain/service/screener_test.go`, `internal/infrastructure/risk/manager_test.go`, etc.

### P2-2. Delete dead code (ALL reviewers agree)

- `internal/infrastructure/binance/client.go` — never called, README says "(unused — Binance blocked)"
- `polymarket/client.go` `contains()` helper — broken implementation (`s == substr` is exact equality, not substring), also never called
- `gorilla/websocket` dependency exists only for the dead Binance client

**Action:** Delete Binance client, delete `contains()`, run `go mod tidy` to remove websocket dep if unused elsewhere.

**Files to delete:** `internal/infrastructure/binance/client.go`

### P2-3. Fix Binance JSON struct (before deletion, or if kept)

If Binance client is kept for future use, fix the unexported fields:
```go
b string `json:"b"` // unexported — json.Unmarshal ignores this
c string `json:"c"` // shadowed by exported Bid/Ask fields
```

**Action:** If keeping Binance, delete the `b`/`c` fields. If deleting (P2-2), this is moot.

### P2-4. Fix `AssetID[:8]` potential panic

`polymarket/clob_client.go:121` — if `AssetID` is shorter than 8 chars, this panics at runtime.

**Action:**
```go
func safeTruncate(s string, n int) string {
    if len(s) < n { return s }
    return s[:n]
}
```

### P2-5. Fix `extractJSON` in LLM client

Current: first `{` to last `}` — breaks on LLM prose containing curly braces.

**Action:** Try `json.Unmarshal` on raw string first, then look for markdown-fenced (` ```json `) blocks, then fall back to current heuristic.

**Files to change:** `internal/infrastructure/llm/client.go`

### P2-6. Fix `screener.seen` map unbounded growth

Expired entries are checked but never cleaned up. The map grows forever.

**Action:** Add periodic cleanup (e.g., every 60s goroutine that deletes entries where `time.Now().After(exp)`), or switch to a bounded cache with eviction.

**Files to change:** `internal/domain/service/screener.go`

### P2-7. Enforce Opportunity aggregate state transitions

`net_router.go` directly mutates `opp.State` instead of calling domain methods:
```go
opp.State = aggregate.StateExecuting  // line 37
opp.State = aggregate.StateExpired    // line 63
```

**Action:** Add `opp.TransitionTo(state State) error` method with valid-transition validation.

**Files to change:** `internal/domain/aggregate/opportunity.go`, `internal/engine/net_router.go`

### P2-8. Remove `time.Sleep(50ms)` from PaperOnly

This blocks the main event loop for 50ms during which no price updates are processed.

**Action:** Delete the sleep, or make execution async.

**Files to change:** `internal/engine/net_router.go`

---

## P3 — Nice to Have (config, observability, future scale)

### P3-1. Extract hardcoded config to named constants or config struct

Magic numbers scattered across files: `0.52`, `78000.0` (3+ files), 20s LLM tick, 500ms loop ticker, 3s poll interval, fee schedules.

**Action:** Create `internal/config/config.go` with a structured config (from env vars or YAML).

### P3-2. Replace fmt.Printf with structured logging (slog)

All logging is unstructured stdout. Makes filtering/debugging in production impossible.

**Action:** Replace `fmt.Printf`/`log.Println` with `slog.Info`/`slog.Warn`/`slog.Error` with structured key-value fields.

### P3-3. Multi-market watchlist

Currently hardcoded to a single Polymarket condition_id. The architecture should support watching multiple markets simultaneously.

**Action:** Add `MarketWatchlist` type that manages multiple condition_ids with their strike/expiry config.

### P3-4. Latency measurement

`Price.Latency` field exists but is always 0. Measure clock drift between exchange timestamp and local processing time. Critical for understanding if a "spread" is real or stale.

### P3-5. Use strconv.ParseFloat instead of fmt.Sscanf

More idiomatic, better error handling. Only matters if Binance client is kept.

---

## New Ideas Worth Exploring

### Idea 1: Funding Rate Arbitrage (Complementary strategy)

OKX perpetual swaps have 8h funding payments. When funding > 10 bps per 8h (annualized ~13%), run delta-neutral basis capture: short perp + long spot. Requires OKX perp ticker and funding rate API.

### Idea 2: Order Book Imbalance (Leading indicator)

Compute `(bidVol - askVol) / (bidVol + askVol)` from full Polymarket book. This predicts probability drift before the BBO moves — useful for early signal.

### Idea 3: YES/NO Token Parity Arb

On the same Polymarket market, YES + NO should sum to ~$1.00. Arb the difference directly on Polymarket without needing OKX spot. Tighter, simpler, no external price reference needed.

### Idea 4: Circuit Breakers Instead of SAGA

Temporal's 10min activity timeout is too slow for sub-second arbitrage. Use local circuit breakers: if Polymarket doesn't acknowledge a fill within 200ms, cancel the OKX leg immediately.

### Idea 5: Vol Surface from OKX Options

For Black-Scholes probability calculation (P0-1), you need BTC vol. OKX options market data gives an implied vol surface. Even a simplified model (rolling 30d ATM vol) dramatically improves probability comparison.

---

## Execution Order

```
Phase 1 (P0): Fix the core pricing model + HTTP safety + zero-price guards
  └─ Without P0-1, all detected spreads are phantom — everything else is pointless
  └─ Without P0-2 and P0-3, garbage data flows through the system

Phase 2 (P1): Make the strategy actually work
  └─ WebSocket (P1-1) + LLM connection (P1-2) + Executor interface (P1-3)
  └─ Fix risk manager (P1-4)

Phase 3 (P2): Code quality and safety
  └─ Tests (P2-1) + Dead code cleanup (P2-2) + Bug fixes (P2-3 through P2-8)

Phase 4 (P3): Observability and scale
  └─ Config, logging, multi-market, latency
  └─ Explore new ideas in parallel
```

---

## Items Explicitly Excluded (and why)

| Excluded Item | Source(s) | Reason |
|---------------|-----------|--------|
| "Data race on stats struct" | deepseek | Not a real race — all stats writes happen in the same goroutine (main select loop). Future-proofing via atomics is premature. |
| "Race condition on okxP/polyP pointers" | glm-5.1 | The reviewer themselves noted it's "actually safe" — values are copied under the lock. Not a real issue. |
| "No WaitGroup for goroutine cleanup" | glm-5.1 S5 | The goroutines exit on ctx.Done(). Stats print after `break loop` is fine. Adding a WaitGroup would be cosmetic. |
| "Channel buffer size 1 may cause stale prices" | glm-5.1 S7, deepseek S22 | This is intentional — keeps latest price, drops stale ones. Both reviewers acknowledged this. |
| "Screen() error return is unused" | glm-5.1 W4, deepseek S7 | Cosmetic. The nil error return is a placeholder for future error paths when real APIs are used. |
| "Use math/rand/v2" | glm-5.1 S4 | Go 1.23 auto-seeds math/rand. The simulated client will be replaced by real data. No impact. |
| "CLOB apiKey never validated" | glm-5.1 W9 | The CLOB client is unused (main uses SimulatedClient). Validate when wiring it up. |
| "Spread.TTL is hardcoded" | glm-5.1 S11 | 2500ms is a reasonable default. Config can override later. |
| "Opportunity ID collision risk" | glm-5.1 S12 | 48 bits of hash is sufficient for a dedup key on a single-machine prototype. |
| "stats.totalNet never updated" | glm-5.1 S6, review-combined S6 | The net spread is printed by `PaperOnly` but not accumulated. Trivial fix, but stats are session-only and cosmetic. |