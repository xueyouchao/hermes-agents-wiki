# SpeedGap-Prototype Code Review — Merged Report

**Date:** 2026-04-25  
**Reviewers:** deepseek-v4-flash + glm-5.1 (consolidated)  
**Project:** speedgap-prototype (14 Go source files, ~1074 lines, 0 test files)

---

## CRITICAL (fix before any production use)

| # | Issue | Consensus | Details |
|---|-------|-----------|---------|
| C1 | **Binance struct: unexported fields with JSON tags** | Both | `internal/infrastructure/binance/client.go:48-49` — fields `b` and `c` are lowercase (unexported) but have json tags. `encoding/json` silently ignores them. They also shadow exported fields with the same tags (`"b"`, `"a"`). **Delete the unexported fields.** |
| C2 | **Missing HTTP status code checks** | Both | `okx/client.go:45-59`, `polymarket/clob_client.go:81-107` — neither checks `resp.StatusCode`. A 429/403/500 response silently decodes into a zero struct → garbage prices. |
| C3 | **`contains()` is broken AND unused** | Both | `polymarket/client.go:50-52` — `s == substr` checks exact equality, not substring. It's also never called. **Delete it.** |
| C4 | **`AssetID[:8]` slice can panic** | deepseek only | `polymarket/clob_client.go:121` — if `AssetID` is shorter than 8 chars, this panics at runtime. |
| C5 | **Polymarket price scaling = hardcoded magic numbers** | Both | `0.52` and `78000.0` appear in 3+ files (`client.go:39`, `clob_client.go:119`, `clob_types.go:73-74`). These are fragile and wrong when BTC moves. Extract to named constants or derive from live data. |
| C6 | **`extractJSON` is fragile** | Both | `llm/client.go:134-141` — first `{` to last `}` breaks on LLM prose containing curly braces. Try `json.Unmarshal` first, then look for ```json fences. |

---

## WARNINGS (should fix, not immediately dangerous)

| # | Issue | Source | Details |
|---|-------|--------|---------|
| W1 | **`currentUSD` never updated → risk manager is disabled** | Both | `risk/manager.go:13` — starts at 0, never increments. Position limit check always passes. |
| W2 | **LLM goroutine is fire-and-forget** | Both | `main.go:82-91` — LLM signal is logged but never feeds back into screener/execution. README says "trades on BOTH speed-gap + reasoning-gap" — impl doesn't match. |
| W3 | **`seen` map in screener grows unboundedly** | Both | `screener.go:15` — expired entries are never cleaned up. Use periodic eviction or `sync.Map`. |
| W4 | **`Screen()` signature has unused error return** | Both | `screener.go:25,102` — always returns `nil` error. Simplify or implement error paths. |
| W5 | **Silent zero on parse failures** | Both | `clob_types.go:59` (`ParseFloat`), `okx/client.go:63-64` (`Sscanf`), `binance/client.go:59-60` — all swallow errors and default to 0. Zero prices cause division-by-near-zero in spread calc. |
| W6 | **`time.Sleep(50ms)` blocks main loop** | Both | `net_router.go:62` — simulates latency but stops price processing for 50ms. Should be async or removed. |
| W7 | **Ignored errors** | Both | `json.Marshal` in `llm/client.go:75`, `http.NewRequestWithContext` in `llm/client.go:78`, `okx/client.go:44`, `clob_client.go:77,97` — errors silently discarded. |
| W8 | **`Opportunity.State` mutated externally** | Both | `net_router.go:37,63` — directly mutates `opp.State` instead of calling domain methods. Violates DDD aggregate pattern. |

---

## SUGGESTIONS (improvements)

| # | Issue | Consensus | Details |
|---|-------|-----------|---------|
| S1 | **Zero unit tests** | Both | No `*_test.go` files at all. `CalculateSpread`, `Screen`, `PaperOnly`, `Evaluate`, `extractJSON`, `parsePolymarketPriceStr` are all easily testable. |
| S2 | **Binance client is dead code** | Both | Unreferenced, imports `gorilla/websocket` (only external dep). Remove or gate behind build tag. |
| S3 | **DRY violation: scaling formula duplicated 3x** | Both | Extract `ScalePolymarketPrice(price float64) float64` with named constants. |
| S4 | **No structured logging** | Both | All `fmt.Printf` / `log.Println`. Use `slog` for levels + structured fields. |
| S5 | **Hardcoded config values** | deepseek | LLM prompt, 20s tick, 500ms loop ticker, 3s poll interval — should be config-driven. |
| S6 | **`Stats` is anonymous local struct** | glm | Move to a named type for clarity. Also `totalNet` is never updated from net spreads. |
| S7 | **`PaperOnly` returns string, not struct** | deepseek | Return a structured result for programmatic use; format strings in the caller. |
| S8 | **Use `strconv.ParseFloat` instead of `fmt.Sscanf`** | deepseek | More idiomatic, better error messages. |
| S9 | **No graceful goroutine cleanup** | deepseek | No `WaitGroup` to ensure streaming goroutines finish before program exits. |

---

## LOOKS GOOD (both reviewers agree)

- **Clean DDD architecture** — `domain/valueobject`, `domain/service`, `domain/aggregate`, `infrastructure` layers with inward-pointing deps
- **Proper context cancellation** — all streaming goroutines respect `ctx.Done()`; main uses `signal.NotifyContext`
- **Fee-aware execution logic** — net spread correctly accounts for taker fees on both legs
- **Solid dedup pattern** — SHA256 hash + 30s TTL prevents duplicate opportunity emission
- **Correct spread formula** — `(poly - bin) / mid * 10000` is standard convention
- **Defensive LLM fallback** — parse failures produce neutral/HOLD signal rather than crashing

---

## Top 5 Action Items

1. **Add HTTP status checks** (C2) — essential for a trading system; silent zero-values are dangerous
2. **Fix Binance struct** (C1) — delete unexported `b`/`c` fields that shadow valid ones
3. **Fix `currentUSD` accumulation** (W1) — risk manager is completely inert without it
4. **Delete broken `contains()`** (C3) — dead code + logic bug
5. **Add unit tests** (S1) — zero test coverage is the biggest structural gap