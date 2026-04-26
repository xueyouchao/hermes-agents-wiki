# SpeedGap Prototype — Architecture Review

**Reviewer:** minimax-m2.7:cloud (custom provider)
**Project:** speedgap-prototype (14 Go source files, ~1074 lines, 0 test files)
**Date:** 2026-04-25

---

## Does It Fit the Use Case?

**No — not in its current form.** The architecture has the right *shape* (DDD layering, fee awareness, channel-based streaming) but suffers from fundamental semantic errors and missing infrastructure that make it ineffective at actually detecting or executing real arbitrage.

---

## What Works

- **DDD layering**: `domain` has zero external imports, infrastructure points inward — correct
- **Fee modeling is correct**: NetRouter properly applies taker fees on both legs before computing net spread
- **Cancellation safety**: All goroutines respect `ctx.Done()`
- **Dedup pattern**: SHA256 + 30s TTL is reasonable for avoiding duplicate opportunity emissions
- **Go idioms**: Channels, interfaces, value objects — idiomatic Go 1.23

---

## Critical Issues

### 1. Apples-to-Oranges Price Comparison (P0 — semantically wrong)

The screener computes:

```
spreadBps = (polyPrice - binPrice) / midpoint * 10000
```

But `polyPrice` is a **binary probability token** (YES token worth $0–1, e.g. 0.52) that represents the market's implied probability of "BTC closes above $X today." `binPrice` is the actual BTC spot price (~$78,000).

The current code "fixes" this with:
```go
scaled := val / 0.52 * 78000.0  // clob_client.go line 119
```

This is a linear heuristic that only works if BTC is exactly ~$78K. It breaks completely as BTC moves. The two prices are **different financial instruments** that cannot be directly compared as a scalar spread.

**What the spread should actually be:**

```
implied_prob  = Polymarket YES token price  (e.g. 0.65)
actual_prob   = N(d2) from Black-Scholes given spot + vol + time-to-expiry
spread_bps    = (implied_prob - actual_prob) * notional * 10000
```

You are arbitrageing **implied vs actual probability**, not BTC price across venues. The 274 bps the system reports is likely phantom — an artifact of the scaling heuristic, not a real spread.

### 2. Latency: 2–3s REST Polling (P0 — kills the strategy)

Speedgap arbitrage requires sub-second price tracking. In 2 seconds of BTC volatility at $78K:
- Normal: $50–200 move
- Volatile: $500+ move

A 274 bps spread can flip sign in 100ms. Sub-second websocket streaming is non-negotiable. OKX REST polling every 2s and Polymarket every 3s are fundamentally incompatible with the strategy.

OKX has a public WebSocket endpoint (`wss://ws.okx.com:8443/ws/v5/public`). Polymarket CLOB also supports WebSocket. You have `gorilla/websocket` in go.mod but only use it in the dead Binance client.

### 3. LLM Signal Never Connects to Execution (P1)

The LLM fires every 20s and logs a signal, but:
- `InterpretSignal` result is printed and discarded
- `LLMSignal` is never passed to `OpportunityScreener.Screen()` or `NetRouter.PaperOnly()`
- No direction/confidence filtering of opportunities
- The "reasoning gap" strategy is essentially non-functional

For the reasoning-gap to work, the LLM signal should gate or weight execution:
- **Gate**: only trade when LLM direction agrees with spread direction
- **Weight**: boost effective spread when LLM confidence is high
- **Filter**: reject opportunities when LLM says "HOLD"

### 4. Risk Manager Is Inert (P1)

```go
// risk/manager.go line 26
notional := absBps * 10.0  // heuristic: 1 bps → $10 notional
```

`currentUSD` is never incremented after a trade, so the manager will never trigger the "position limit" rejection. The risk manager has no memory between calls.

### 5. No Execution Abstraction (P1)

`NetRouter.PaperOnly` directly does `fmt.Printf`. To go live you would need to rewrite it. There is no `Executor` interface to swap between paper/OKX live/Polymarket live.

### 6. No Tests (P2)

Zero test files in the repo. The domain layer (spread calculation, screening logic, risk evaluation) is pure functions with zero dependencies — trivially testable with table-driven tests.

### 7. Dead Code (P2)

- `internal/infrastructure/binance/client.go` — never called (main.go uses `okx.NewClient()` and `polymarket.NewSimulatedClient()`)
- `polymarket/client.go` `contains()` helper — defined but never used
- go.mod has `gorilla/websocket` but it's only used by the dead Binance client

---

## Specific Code Bugs

| File | Line | Bug |
|------|------|-----|
| `risk/manager.go` | 23 | `absBps < 0` is always false (compare to 0, not assign) — bug: should be `if absBps < 0 { absBps = -absBps }` but the if condition itself is wrong |
| `risk/manager.go` | 26 | `notional := absBps * 10.0` — with absBps already set positive by line 22-25, this is actually fine but the comment "heuristic: 1 bps → $10" is wrong for a BTC spread |
| `polymarket/clob_client.go` | 18 | `const ConditionBTCDaily = "PLACEHOLDER_REPLACE_ME"` — the README says "PLACEHOLDER" but code has `"PLACEHOLDER_REPLACE_ME"`, mismatch |
| `net_router.go` | 56 | `mid*0.001` — this seems like a notional calculation (0.1% of mid) but is hard to follow without comments |
| `main.go` | 83 | `ollama.InterpretSignal` runs on a goroutine but `signal` is never shared back to the main loop — there's no channel to deliver it |

---

## Improvements (by priority)

### P0 — Fix the pricing model first, everything else depends on it

```
internal/domain/service/probability_arbitrage.go

type ProbabilitySpread struct {
    ImpliedProb float64   // Polymarket YES token price (0.0–1.0)
    ActualProb  float64   // Black-Scholes N(d2) given spot, strike, vol, TTE
    Strike      float64   // the BTC threshold the market is betting on
    Expiry      time.Time
    SpreadBps   float64   // (implied - actual) * notional * 10000
}
```

You need to know the strike price of the Polymarket market (from the market question) and compute the actual probability using BTC vol from OKX options data or a hardcoded vol assumption.

### P1 — WebSocket streaming for both venues

- OKX public WebSocket: `wss://ws.okx.com:8443/ws/v5/public` with ticker subscription
- Polymarket CLOB WebSocket for order book delta updates

### P1 — Connect LLM to screener via a signal channel

```go
signalCh := make(chan *valueobject.LLMSignal, 1)
// LLM goroutine writes here
// Screener reads latest signal and uses it to filter opportunities
```

### P1 — Executor interface

```go
type Executor interface {
    Execute(ctx context.Context, opp *Opportunity, leg1, leg2 Price) (string, error)
}
// PaperExecutor: fmt.Printf (current)
// LiveOKXExecutor: REST + HMAC
// LivePolyExecutor: CLOB + EIP-712
```

### P2 — Fix risk manager to track cumulative P&L

```go
func (m *Manager) Evaluate(ctx context.Context, opp *Opportunity) error {
    notional := m.computeNotional(opp.Spread)
    if m.currentUSD + notional > m.maxPositionUSD {
        return errors.New("position limit exceeded")
    }
    return nil
}
// And add RecordTrade(notional, pnl) to update currentUSD after each fill
```

### P2 — Add domain unit tests

The domain layer is fully testable without any mocks.

### P2 — Delete dead code

Remove Binance client and the unused `contains()` helper.

---

## New Ideas for the Use Case

### Idea 1: Funding Rate Calendar (if you add perp markets)

OKX perpetual swap funding rates are paid every 8h. When funding > 10 bps per 8h (annualized ~13%), you can run delta-neutral basis capture. This complements the prediction market strategy.

### Idea 2: Order Book Imbalance as a Leading Indicator

Polymarket's full order book (not just BBO) can show order flow imbalance:

```
imbalance = (bidVol - askVol) / (bidVol + askVol)
```

This predicts probability drift before the price moves — useful as an early signal feeding into your LLM-enriched screener.

### Idea 3: Vol Surface from OKX Options

To compute actual probability via Black-Scholes you need BTC vol. OKX options market data gives you an implied vol surface. Even a simplified vol model (e.g., rolling 30d ATM vol) would dramatically improve the probability comparison over the current scalar approach.

### Idea 4: Multi-Leg with Polymarket NO Tokens

Most arbitrage setups look at YES token vs spot. But you could also arb YES vs NO on the same market (they should sum to ~$1). This is tighter and doesn't require external price reference.

### Idea 5: Compress the SAGA with Circuit Breakers

The Temporal SAGA is the right pattern, but for sub-second latency you need local circuit breakers: if Polymarket doesn't acknowledge a fill within 200ms, cancel the OKX leg immediately. Temporal's 10min activity timeout is too slow for this use case.

---

## Summary Verdict

| Dimension | Score | Notes |
|-----------|-------|-------|
| Architecture shape | 7/10 | DDD layering, interfaces, channels — correct structure |
| Semantic correctness | 2/10 | Probability vs price comparison is fundamentally broken |
| Latency | 2/10 | 2–3s polling incompatible with the strategy |
| Execution model | 1/10 | Paper only, no abstraction, fmt.Printf everywhere |
| Testability | 0/10 | Zero tests |
| LLM integration | 1/10 | Fires but never connects to anything |
| Production readiness | 1/10 | No error handling, no structured logging, dead code |

The codebase is a well-structured prototype that solves the wrong problem. Fix the pricing model first (P0), then upgrade to WebSockets (P1), then wire up the LLM signal (P1), then add tests (P2). The DDD scaffolding is solid — the domain logic just doesn't yet express the right financial model.