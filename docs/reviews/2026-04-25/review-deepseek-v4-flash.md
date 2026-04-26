# Code Review Report: SpeedGap-Prototype (DeepSeek-V4-Flash)

**Reviewer:** deepseek-v4-flash:cloud  
**Date:** 2026-04-25  

---

## CRITICAL (5 findings)

### 1. Data Race on `stats` struct in main loop
**File:** `cmd/speedgap/main.go:50-57, 102-118`  
The `stats` struct is read and written from two goroutine contexts: the `select` loop (which writes `stats.detected++`, `stats.totalGross += ...`, etc.) and the LLM goroutine (which does none of this currently but could in future). More critically, `stats.detected`, `stats.executed`, `stats.rejected`, `stats.totalGross` are mutated in the `case <-ticker.C` branch without any synchronization (no mutex protection). While currently all writes happen in the same goroutine (the main select loop), the stats are read at line 126-131 after the loop ends, which is safe. **However**, the `llmTicker.C` branch at line 82 spawns a goroutine, and while it doesn't touch `stats` today, the architecture invites future data races. The `stats` struct should use either atomic operations or a mutex to be future-proof.

### 2. `contains()` function is completely broken
**File:** `internal/infrastructure/polymarket/client.go:50-52`
```go
func contains(s, substr string) bool {
    return len(s) >= len(substr) && s == substr
}
```
This function is supposed to check if `substr` is contained in `s`, but instead it checks if `s` equals `substr`. The `len(s) >= len(substr)` guard is meaningless since `s == substr` already implies equal length. This is a logic bug if `contains` is ever called with a proper substring. Currently it appears to be unused, but if used in production it would silently fail. **Delete this dead code.**

### 3. Missing HTTP response status code checks
**File:** `internal/infrastructure/polymarket/clob_client.go:81-89, 98-107`  
**File:** `internal/infrastructure/okx/client.go:45-59`  
Neither the OKX client nor the Polymarket CLOB client checks `resp.StatusCode` before decoding the JSON body. A 4xx/5xx response would silently produce an empty/zero-value struct, which could be interpreted as valid data. This is especially dangerous for OKX (rate limits, IP blocks) and Polymarket (auth errors). Check `resp.StatusCode` and return an error for non-2xx statuses.

### 4. Potential panic from slice index in `bookToPrice`
**File:** `internal/infrastructure/polymarket/clob_client.go:121`
```go
AssetID: book.AssetID[:8],
```
If `book.AssetID` has fewer than 8 characters, this slice expression will panic at runtime. Should add a length check or use a safe truncation function.

### 5. Polymarket price scaling is a brittle hardcoded heuristic
**File:** `internal/infrastructure/polymarket/client.go:38-39`  
**File:** `internal/infrastructure/polymarket/clob_client.go:119, 134`  
**File:** `internal/infrastructure/polymarket/clob_types.go:73-74`  
Multiple files contain `scaled := val / 0.52 * 78000.0` or equivalent `bid / base * 78000.0` where `base = 0.52`. This magic-number scaling converts Polymarket contract prices (0–1 range) to a BTC/USD proxy. The hardcoded values (`0.52`, `78000.0`) are fragile — if BTC moves significantly or the contract price shifts, the scaling becomes wildly inaccurate. This should be parameterized or derived from live data.

---

## WARNINGS (9 findings)

### 6. `OpportunityScreener.seen` map is not thread-safe
**File:** `internal/domain/service/screener.go:15, 37-40`  
The `seen` map is read and written in `Screen()` which is called from the main goroutine only. But `Screen` is a public method on a shared struct — if ever called concurrently (e.g., from multiple goroutines or after future refactoring), it will race. Should document single-goroutine constraint or add a `sync.Mutex`.

### 7. `Screen()` error always returns `nil`
**File:** `internal/domain/service/screener.go:25, 102`  
`Screen()` returns `(*aggregate.Opportunity, error)` but never returns a non-nil error. The caller in `main.go:102` discards it with `opp, _ := screener.Screen(...)`. This is a code smell: the error return is unused dead code. Either implement meaningful error paths or simplify the signature.

### 8. `Risk.Manager.currentUSD` is never updated
**File:** `internal/infrastructure/risk/manager.go:13-14, 26-33`  
`currentUSD` starts at 0 and is never incremented. Every call to `Evaluate()` will see `currentUSD = 0`, so the max position limit (`maxPositionUSD = 10000`) is never approached. This means the risk manager always approves trades. A real implementation would need to track cumulative position size.

### 9. LLM goroutine is fire-and-forget
**File:** `cmd/speedgap/main.go:82-91`  
The LLM signal goroutine logs the result but doesn't feed it back into the trading decision. The LLM signal is purely decorative — it has zero effect on execution logic. This is misleading architecture; the README says "Trades on BOTH speed-gap + reasoning-gap simultaneously" but the code doesn't do that.

### 10. `time.Sleep` in production path
**File:** `internal/engine/net_router.go:62`
```go
time.Sleep(50 * time.Millisecond)
```
A `time.Sleep` in the execution path simulates latency but blocks the main event loop context. In a real execution engine this should not exist. It also doesn't respect context cancellation during the sleep.

### 11. JSON extraction is fragile
**File:** `internal/infrastructure/llm/client.go:134-141`  
`extractJSON` finds the first `{` and last `}` and returns everything between. This will break on LLM output that contains curly braces in natural language text before/after the JSON block. A more robust approach would look for ```json fences or use regex.

### 12. Ignored errors from `json.Marshal` and `http.NewRequestWithContext`
**File:** `internal/infrastructure/llm/client.go:75, 78`  
**File:** `internal/infrastructure/polymarket/clob_client.go:77, 97`  
`json.Marshal` and `http.NewRequestWithContext` errors are swallowed with `_`. While these are unlikely to fail with known-good data, silently ignoring errors is a bad habit, especially in a financial system.

### 13. `parsePolymarketPriceStr` silently returns 0 on parse failure
**File:** `internal/infrastructure/polymarket/clob_types.go:56-60`  
`strconv.ParseFloat` error is discarded, returning 0.0. A zero price propagating through the spread calculator would produce wildly incorrect results (division by near-zero in `CalculateSpread`).

### 14. Simulated client uses non-seeded `rand.Float64()`
**File:** `internal/infrastructure/polymarket/client.go:36`  
`math/rand` without explicit seeding produces deterministic output (as of Go 1.20+, it's auto-seeded, but older behavior was deterministic). Not a real bug in Go 1.23, but worth noting.

---

## SUGGESTIONS (10 findings)

### 15. No unit tests exist
There are zero `*_test.go` files in the entire project. Given that `CalculateSpread`, `Screen`, `PaperOnly`, `Evaluate`, and `extractJSON` are all deterministic functions, they would be straightforward to unit test. This is the single biggest gap for production readiness.

### 16. Binance client is dead code
**File:** `internal/infrastructure/binance/client.go`  
The Binance client is imported nowhere and unused (README says "Binance blocked"). It imports `gorilla/websocket` which is the only external dependency. Consider removing it or adding a build tag to exclude it.

### 17. DRY violation: Polymarket scaling constant duplicated
Files: `client.go:39`, `clob_client.go:119`, `clob_types.go:73`  
The scaling formula `(price / 0.52) * 78000.0` appears in 3 places with the magic numbers `0.52` and `78000.0`. Extract to a constant or helper function.

### 18. OKX client uses `fmt.Sscanf` instead of `strconv.ParseFloat`
**File:** `internal/infrastructure/okx/client.go:63-64`  
`fmt.Sscanf` is slower and less idiomatic than `strconv.ParseFloat`. Also, `fmt.Sscanf` doesn't report parse failure clearly. Same pattern in `binance/client.go:59-60`.

### 19. `Opportunity` struct has no state transitions or validation
**File:** `internal/domain/aggregate/opportunity.go:19-25`  
The aggregate has `State` but no methods to enforce valid state transitions (e.g., OPEN -> EXECUTING -> EXPIRED/FAILED). The state is mutated directly from `net_router.go:37,63`. This violates the aggregate pattern from DDD.

### 20. Hardcoded prompt and tick interval
**File:** `cmd/speedgap/main.go:84`  
The LLM prompt is a hardcoded string and the LLM tick is hardcoded to 20s. These should be configuration parameters. Similarly, the 500ms main loop ticker (line 59) and the Polymarket 3s poll interval should be configurable.

### 21. No structured logging
All logging uses `fmt.Printf` / `fmt.Println` / `log.Println`. A structured logger (like `slog`) would make logs machine-parseable and allow filtering by component, severity, etc.

### 22. Channel capacity of 1 may cause dropped updates
**File:** `cmd/speedgap/main.go:38-39`
```go
okxPrice := make(chan valueobject.Price, 1)
polyPrice := make(chan valueobject.Price, 1)
```
With buffered=1 channels, the send is non-blocking only if the previous value was consumed. The `select` in the main loop processes one message per iteration. Under high frequency, the most recent price may overwrite older ones, but since the channel is buffered(1), producers won't block — they'll just send the latest value. This is actually OK for this use case (stale prices are undesirable), but it should be documented as intentional.

### 23. NetRouter.PaperOnly mutates state via side effect
**File:** `internal/engine/net_router.go:37`  
`opp.State = aggregate.StateExecuting` — The router directly mutates the opportunity's state, coupling engine logic to domain state. State transitions should be encapsulated within the aggregate.

### 24. No graceful shutdown for HTTP clients
**File:** `internal/infrastructure/okx/client.go:32`  
The `httpClient` is created inside `StreamBTCUSDT` and never closed. While this is fine for a long-running goroutine, the `defer ticker.Stop()` runs but the HTTP client's idle connections are never cleaned up when the function exits.

---

## LOOKS GOOD (6 findings)

### 25. Clean DDD-style package structure
The project follows a clear domain-driven design with `domain/valueobject`, `domain/service`, `domain/aggregate`, and `infrastructure` layers. Dependencies point inward (infrastructure depends on domain, not vice versa). This is well-organized.

### 26. Proper context cancellation handling
**Files:** `cmd/speedgap/main.go:24`, `okx/client.go:38-40`, `polymarket/client.go:30-33`, `polymarket/clob_client.go:39-42`  
All streaming goroutines properly respect `ctx.Done()` for graceful shutdown. The main function uses `signal.NotifyContext` which is idiomatic.

### 27. Fee-aware execution logic is sound
**File:** `internal/engine/net_router.go:39-45`  
The net spread calculation correctly adjusts for taker fees on both legs and computes the fee-adjusted spread. The logic `(polyExec - okxExec) / mid * 10000` is correct.

### 28. Dedup mechanism is clever
**File:** `internal/domain/service/screener.go:33-40`  
The SHA256 hash bucket + 30s TTL dedup is a good pattern for preventing duplicate opportunity emission during the same time window.

### 29. Polymarket CLOB client has graceful fallback
**File:** `internal/infrastructure/polymarket/clob_client.go:46-49`  
The check for `PLACEHOLDER_REPLACE_ME` condition ID and fallback to simulated data is a pragmatic approach for development.

### 30. Spread calculation is correct
**File:** `internal/domain/valueobject/spread.go:14-26`  
`(poly - bin) / mid * 10000` correctly computes basis points with mid-price as the denominator, which is the standard convention for spread measurement.

---

## Summary

| Category | Count | Key Items |
|----------|-------|-----------|
| **Critical** | 5 | Data race risk, broken `contains()`, missing HTTP status checks, potential slice panic, hardcoded magic scaling |
| **Warning** | 9 | No thread safety on map, never-updated risk state, ignored errors, fire-and-forget LLM, `time.Sleep` in path, fragile JSON extraction |
| **Suggestion** | 10 | No tests, dead Binance code, DRY violations, no structured logging, hardcoded configs |
| **Looks Good** | 6 | Clean architecture, proper context cancellation, correct fee logic, good dedup pattern |

**Top 3 priorities for improvement:**
1. Add unit tests (zero test coverage is the biggest gap)
2. Add HTTP status code checks and proper error propagation (critical for a trading system)
3. Remove the broken `contains()` function and the dead Binance client, add safety checks for the `AssetID[:8]` slice