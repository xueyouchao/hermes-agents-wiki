# Code Review Report: SpeedGap-Prototype (GLM-5.1)

**Reviewer:** glm-5.1:cloud  
**Date:** 2026-04-25  
**Files reviewed:** 14 Go source files, ~1074 lines, 0 test files

---

## CRITICAL (4 findings)

### C1. Binance client: invalid JSON struct tags cause silent data loss
**File:** `internal/infrastructure/binance/client.go`, lines 48-49
```go
b string `json:"b"` // best bid
c string `json:"c"` // best ask
```
Unexported fields (`b`, `c`) are never populated by `json.Unmarshal` — Go's encoding/json ignores unexported fields. These are also shadowed by the exported fields on lines 51-52 which duplicate the same JSON tags (`"b"` and `"a"`). `go vet` correctly flags: "struct field b has json tag but is not exported" and "struct field Bid repeats json tag". The unexported fields `b` and `c` should simply be deleted. As written, the struct definition is misleading and wastes memory.

### C2. Race condition on `okxP` / `polyP` pointers in main loop
**File:** `cmd/speedgap/main.go`, lines 44-98  
The `select` block writes `okxP` and `polyP` under `mu.Lock()`, and the `ticker` case reads them under `mu.Lock()`. However the `llmTicker` goroutine (line 82) and the `ticker` case (line 93) run concurrently. While each individual access is mutex-protected, there is a TOCTOU gap: between reading `localOkx`/`localPoly` (line 95-96) and passing them to `screener.Screen` (line 102), another goroutine could update the originals. Since you copy the pointer values under the lock this is actually safe for the current code — but note that `*valueobject.Price` is a pointer to a stack value placed on the channel. If the channel sender reuses a `Price` object, the pointer would be stale. Currently each channel receive creates a fresh value, so this is borderline safe but fragile.

### C3. `netRouter.PaperOnly` mutates shared state without synchronization
**File:** `internal/engine/net_router.go`, lines 37, 63
```go
opp.State = aggregate.StateExecuting  // line 37
opp.State = aggregate.StateExpired    // line 63
```
The `Opportunity` object is shared between the screener, risk manager, and net router. Mutating `opp.State` is a side effect that could cause race conditions if the opportunity is ever accessed concurrently. In practice this is only called from the main loop so it's single-threaded, but it's a dangerous pattern for an aggregate root.

### C4. `extractJSON` in LLM client is fragile and can extract garbage
**File:** `internal/infrastructure/llm/client.go`, lines 134-141
```go
func extractJSON(s string) string {
    start := bytes.Index([]byte(s), []byte("{"))
    end := bytes.LastIndex([]byte(s), []byte("}"))
```
This finds the first `{` and last `}` in the LLM output. If the LLM embeds prose with curly braces before the JSON block, or if the JSON contains nested objects, this will produce invalid JSON. A more robust approach: try `json.Unmarshal` on the raw string first, then look for markdown-fenced blocks (```json ... ```), and only fall back to brute-force extraction.

---

## WARNINGS (11 findings)

### W1. No HTTP response status code checking
**File:** `internal/infrastructure/okx/client.go`, lines 45-56  
**File:** `internal/infrastructure/polymarket/clob_client.go`, lines 81-92, 95-107  
Neither the OKX client nor the CLOB client checks `resp.StatusCode` before decoding. A 429 (rate limit), 403 (forbidden), or 500 (server error) response will silently decode into a zero-value struct and produce garbage prices. Always check `resp.StatusCode >= 200 && resp.StatusCode < 300`.

### W2. `parsePolymarketPriceStr` silently swallows parse errors
**File:** `internal/infrastructure/polymarket/clob_types.go`, line 59
```go
f, _ := strconv.ParseFloat(s, 64)
```
If the string is non-numeric, `f` will be `0`. This could create a zero price that propagates through the system. Log a warning or return an error.

### W3. `fmt.Sscanf` silently ignores parse failures for OKX prices
**File:** `internal/infrastructure/okx/client.go`, lines 63-64
```go
fmt.Sscanf(d.BidPx, "%f", &bid)
fmt.Sscanf(d.AskPx, "%f", &ask)
```
If `Sscanf` fails, `bid`/`ask` remain `0`, producing a bad mid-price. Use `strconv.ParseFloat` and check errors, or at minimum log a warning on failure.

### W4. Same issue in Binance client
**File:** `internal/infrastructure/binance/client.go`, lines 59-60
```go
fmt.Sscanf(t.Bid, "%f", &bid)
fmt.Sscanf(t.Ask, "%f", &ask)
```
Same problem as W3.

### W5. Simulated Polymarket client uses non-deterministic `math/rand` without seed
**File:** `internal/infrastructure/polymarket/client.go`, line 36  
`rand.Float64()` is called without seeding. Since Go 1.20 the default seed is random, but if reproducibility is needed for testing, this is an issue. Also note that `math/rand` is not concurrency-safe in older Go versions (though safe since Go 1.20+).

### W6. `screener.seen` map is not thread-safe
**File:** `internal/domain/service/screener.go`, line 15  
The `seen` map is read/written in `Screen()` which is called from the main goroutine, so it's currently safe. But if the design evolves to call `Screen` from multiple goroutines (e.g., multiple price streams), this will race. Consider `sync.Map` or a mutex.

### W7. `risk.Manager.currentUSD` is never updated
**File:** `internal/infrastructure/risk/manager.go`, line 13  
`currentUSD` starts at 0 and is never incremented after a successful trade evaluation. This means the position limit check (`currentUSD + notional > maxPositionUSD`) will never grow, so risk management is effectively disabled — 10000 USD max position will never be approached since current stays at 0.

### W8. LLM goroutine fires continuously but results are never used for trading decisions
**File:** `cmd/speedgap/main.go`, lines 81-91  
The LLM signal goroutine calls `ollama.InterpretSignal()` and prints the result but never feeds it back into the screener or execution logic. The README says "Trades on BOTH speed-gap + reasoning-gap simultaneously" but the code only logs the signal. This is a functional gap between documentation and implementation.

### W9. CLOB client `apiKey` is accepted but never validated
**File:** `internal/infrastructure/polymarket/clob_client.go`, line 25  
The `NewClobClient(apiKey)` accepts an API key and sets it as a header, but:
- It's never actually used (main.go uses `SimulatedClient`)
- There's no validation the key is non-empty
- The Polymarket CLOB likely requires EIP-712 signed orders, not just an API key header

### W10. `time.Sleep(50ms)` in `PaperOnly` blocks the main loop
**File:** `internal/engine/net_router.go`, line 62
```go
time.Sleep(50 * time.Millisecond)
```
This simulates execution latency but blocks the main event loop for 50ms, during which no price updates from OKX or Polymarket are processed. In a real system, this should be async.

### W11. Polymarket price scaling uses hardcoded magic numbers
**File:** `internal/infrastructure/polymarket/clob_client.go`, line 119  
**File:** `internal/infrastructure/polymarket/client.go`, line 39
```go
scaled := (baseBid + baseAsk) / 2 / 0.52 * 78000.0
```
The `0.52` and `78000.0` magic numbers appear in multiple places (clob_client.go:119, clob_types.go:74, client.go:39, clob_client.go:134). These should be named constants.

---

## SUGGESTIONS (13 findings)

### S1. Zero test coverage
No `_test.go` files exist. The domain logic (`CalculateSpread`, `Screen`, `Evaluate`, `PaperOnly`, `extractJSON`, `parsePolymarketPriceStr`) is all testable in isolation. At minimum, add unit tests for:
- `valueobject.CalculateSpread` — spread math correctness
- `service.OpportunityScreener.Screen` — dedup and threshold logic
- `risk.Manager.Evaluate` — position limit boundary cases
- `llm.extractJSON` — various LLM output formats
- `polymarket.parsePolymarketPriceStr` — edge cases

### S2. The `contains` helper is both wrong and unused
**File:** `internal/infrastructure/polymarket/client.go`, lines 50-52
```go
func contains(s, substr string) bool {
    return len(s) >= len(substr) && s == substr
}
```
This is not a substring search — `s == substr` means it only returns true for exact equality. It's also never called anywhere. Delete it.

### S3. Inconsistent error handling patterns
- `Screen()` returns `(*Opportunity, error)` but only ever returns `(nil, nil)` or `(opp, nil)`. It never returns an actual error. If there's no error condition, consider a simpler signature.
- `json.Marshal(reqBody)` on line 75 of `llm/client.go` ignores the error with `_`. While unlikely to fail, it's better to handle it.
- `http.NewRequestWithContext` errors are silently ignored in multiple places (`llm/client.go:78`, `okx/client.go:44`, `clob_client.go:77`, `clob_client.go:97`).

### S4. Use `math/rand/v2` or seed explicitly
**File:** `internal/infrastructure/polymarket/client.go`  
Go 1.23 supports `math/rand/v2` which has better APIs and automatic seeding. Consider upgrading.

### S5. No graceful shutdown for goroutines
**File:** `cmd/speedgap/main.go`, lines 41-42  
The `okxClient.StreamBTCUSDT` and `polyClient.StreamBTCDaily` goroutines are started but there's no `WaitGroup` to ensure they complete before the program exits. The context cancellation will signal them, but the final stats print block doesn't wait for goroutine cleanup.

### S6. Stats struct is a local anonymous struct in main
**File:** `cmd/speedgap/main.go`, lines 50-57  
The `stats` struct is an anonymous struct defined inline in `main()`. This should be a named type for clarity and to allow passing to other functions. Also, `totalGross` and `totalNet` are `float64` but are never updated with `netSpreadBps` from the `PaperOnly` result — only `totalGross` gets `opp.Spread.SpreadBps`.

### S7. Channel buffer size of 1 may cause stale prices
**File:** `cmd/speedgap/main.go`, lines 38-39
```go
okxPrice := make(chan valueobject.Price, 1)
polyPrice := make(chan valueobject.Price, 1)
```
With buffer size 1, if the sender produces a new price before the receiver processes the old one, the old price is overwritten. This is intentional (keeps latest price) but means `case p := <-okxPrice` could miss intermediate prices. Consider documenting this design choice or using a `LatestValue` wrapper.

### S8. No logging library — everything goes to stdout
All logging uses `fmt.Printf` / `log.Println`. Consider using `slog` (Go 1.21+) for structured logging with levels, which would make debugging in production much easier.

### S9. Binance client is dead code
**File:** `internal/infrastructure/binance/client.go`  
The README explicitly states "(unused -- Binance blocked)" but the file still exists and imports `github.com/gorilla/websocket`. It also has the JSON struct bug (C1). Either fix it or remove it entirely. The `gorilla/websocket` dependency in `go.mod` exists only for this dead code.

### S10. Dedup map in screener grows unboundedly
**File:** `internal/domain/service/screener.go`, line 15  
The `seen` map grows over time. While entries expire after 30s, old keys are never cleaned up — they just expire. Since the TTL-based check uses `time.Now().Before(exp)`, expired entries accumulate forever. Add periodic cleanup or use a bounded cache.

### S11. `Spread.TTL` is hardcoded
**File:** `internal/domain/valueobject/spread.go`, line 24
```go
TTL: 2500 * time.Millisecond,
```
This should be configurable or computed from the spread magnitude (larger spreads could have longer TTLs).

### S12. Opportunity ID is a truncated SHA256 hash with collision risk
**File:** `internal/domain/service/screener.go`, line 35
```go
hash := fmt.Sprintf("%x", sha256.Sum256([]byte(dedup)))[:12]
```
12 hex characters = 48 bits of hash. For a deduplication key this is fine, but the `ID` field on `Opportunity` is used as if it's unique. Document that collisions are possible.

### S13. NetRouter.PaperOnly returns a string instead of a structured result
**File:** `internal/engine/net_router.go`, line 64  
The return type is `string` — a formatted message. This makes it impossible to programmatically inspect results. Return a struct with `Direction`, `GrossBps`, `NetBps` fields and format the string in the caller.

---

## LOOKS GOOD (7 findings)

### G1. Clean domain-driven design structure
The project follows a clean DDD layout with `aggregate/`, `service/`, `valueobject/`, `engine/`, `infrastructure/` packages. Domain types are properly separated from infrastructure concerns.

### G2. Proper context propagation
All streaming functions accept `context.Context` and respect `ctx.Done()` for graceful shutdown. The main function uses `signal.NotifyContext` correctly.

### G3. Fee-aware execution logic
`NetRouter` correctly accounts for taker fees on both legs before computing net spread. The `DefaultFees` configuration is clear and adjustable.

### G4. Defensive LLM response parsing
The `parseSignal` function in `llm/client.go` gracefully falls back to a "neutral/HOLD" signal with 0.5 confidence when JSON parsing fails, rather than returning an error. This is reasonable for a non-critical signal source.

### G5. Price value object is well-structured
`valueobject.Price` includes `Source`, `Value`, `Timestamp`, `RawBid`, `RawAsk`, and `Latency` — captures all necessary information for downstream consumers.

### G6. Spread calculation is sound
`CalculateSpread` uses the correct midpoint-relative formula: `(poly - bin) / mid * 10000`. This avoids the division-by-zero issue that would arise from dividing by a single venue's price.

### G7. Graceful shutdown path
The main loop uses `break loop` with a labeled `for` loop, which properly exits the select loop on SIGINT/SIGTERM and prints session statistics.

---

## Summary

| Category | Count |
|----------|-------|
| Critical | 4 |
| Warning  | 11 |
| Suggestion | 13 |
| Looks Good | 7 |

**Top priorities for action:**
1. **Fix the Binance JSON struct** (C1) — delete the unexported fields `b` and `c` that duplicate tags.
2. **Add HTTP status code checks** (W1) — essential for production correctness.
3. **Fix `currentUSD` never incrementing** (W7) — risk management is completely inactive.
4. **Remove or fix the `contains` function** (S2) — it's wrong and unused.
5. **Add tests** (S1) — zero test coverage is the single biggest gap.