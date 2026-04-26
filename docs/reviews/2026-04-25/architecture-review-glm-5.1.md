# SpeedGap-Prototype Architecture Review

**Date:** 2026-04-25
**Reviewer:** glm-5.1 (cloud)
**Project:** speedgap-prototype (14 Go source files, ~1074 lines, 0 test files)

---

## Current Architecture Summary

```
main.go (orchestrator)
  ├── okx.Client (REST poll 2s)        ─┐
  ├── polymarket.SimulatedClient (3s)   ─┤ Price channels
  ├── llm.OllamaClient (20s tick)      ─┘
  │
  ├── service.OpportunityScreener (1 bps threshold, SHA256 dedup)
  ├── risk.Manager (position limits)
  └── engine.NetRouter (fee-adjusted paper execution)

Domain layer: Price VO, Spread VO, LLMSignal VO, Opportunity aggregate
Infrastructure: okx, polymarket (sim+clob), binance (dead), llm, risk
```

---

## Does It Fit the Use Case?

**Partially.** The use case is **cross-venue arbitrage between OKX (BTC-USDT) and Polymarket (BTC-daily prediction market)**. The architecture captures the *structure* of this correctly, but has fundamental gaps that prevent it from actually doing the job effectively.

### What Works Well

1. **DDD layering** — domain has zero external imports, infrastructure depends inward
2. **Fee-aware execution** — NetRouter correctly subtracts taker fees on both legs
3. **Context cancellation** — all goroutines respect ctx.Done()
4. **Dedup pattern** — SHA256 + TTL prevents re-emitting the same opportunity

---

## Architecture Issues (Beyond Code Review)

The existing review (review-combined.md) covered code-level bugs. These are *architectural* problems:

### A1. The Price Comparison Is Semantically Wrong (CRITICAL)

You're comparing:
- **OKX BTC-USDT**: spot BTC price in USD (~$78,000)
- **Polymarket BTC-daily**: a *probability token* priced 0-1 representing "will BTC close above $X today?"

The current code scales the Polymarket probability by `probability / 0.52 * 78000` — a linear heuristic that breaks as soon as BTC moves away from $78K. More fundamentally, **these are different financial instruments being compared as if they're the same asset**.

The arbitrage opportunity here isn't "BTC costs more on Polymarket." It's:
- Polymarket implies a BTC price distribution (via probability of "above $X")
- OKX shows the spot price
- The gap is between Polymarket's *implied probability* vs the *actual probability* given spot + time to expiry

**Recommendation:** Replace the scalar price comparison with a proper *implied probability vs actual probability* model:

```
Implied prob from Poly = token_price_YES
Actual prob from spot  = N(d2) from Black-Scholes using OKX spot + vol + time-to-expiry
Spread = (implied - actual) * notional
```

### A2. Polymarket Has Markets For More Than Just "BTC Above $78K"

Polymarket runs many BTC-related markets with different strike prices. The architecture should support **watching multiple condition_ids** simultaneously and computing spread for each.

### A3. The "Speed" in SpeedGap Needs WebSocket, Not REST Polling

OKX is polled every 2 seconds. In 2 seconds, BTC can move $50-200 during volatile periods. A 274 bps spread can flip to negative in 100ms. The existing `gorilla/websocket` dependency in the Binance client (dead code) should be repurposed for OKX WebSocket streaming.

Polymarket CLOB also supports WebSocket subscriptions. For a system named "speed-gap", sub-second latency is the whole point.

### A4. LLM Signal Is Disconnected from Execution

The LLM fires every 20s and logs a signal, but **the signal never influences screener or execution**. The `LLMSignal` VO isn't used anywhere in the main loop. To make the "reasoning gap" strategy work, the signal needs to either:
- Weight the spread (increase/decrease confidence)
- Gate execution (only trade when LLM agrees on direction)
- Filter opportunities by sentiment

### A5. No Order Execution Path

Everything is paper-only, which is fine for a prototype. But the architecture has no abstraction for execution at all — `PaperOnly()` directly `fmt.Printf`s. There should be an `Executor` interface:

```go
type Executor interface {
    ExecuteLeg(ctx context.Context, leg Leg) (Fill, error)
    CancelLeg(ctx context.Context, legID string) error
}
```

This lets you swap between `PaperExecutor`, `OKXExecutor`, and `PolymarketExecutor` without touching the engine.

### A6. Single-Instrument, Single-Direction Design

The system only trades one direction: buy OKX, sell Polymarket (or vice versa). It can't:
- Trade both directions simultaneously
- Monitor multiple markets
- Track position P&L across time

---

## Proposed Improvements

### 1. Fix the Core Pricing Model (Highest Priority)

Replace the scalar comparison with a probability comparison:

```go
// internal/domain/valueobject/probability.go
type ImpliedProbability struct {
    Source      string    // "polymarket:BTC-above-78K"
    Probability float64   // 0.0 - 1.0
    Strike      float64   // $78,000
    Expiry      time.Time // market resolution time
    RawPrice    float64   // the YES token price
}

type SpotPrice struct {
    Source    string
    Price    float64  // current BTC spot
    Timestamp int64
}
```

Then compute actual probability from Black-Scholes or a simpler heuristic:

```go
func ActualProbFromSpot(spot float64, strike float64, vol float64, tte time.Duration) float64 {
    d1 := (math.Log(spot/strike) + (riskFree+vol*vol/2)*tte.Seconds()/secsPerYear) / (vol * math.Sqrt(tte.Seconds()/secsPerYear))
    d2 := d1 - vol*math.Sqrt(tte.Seconds()/secsPerYear)
    return ndf(d2) // cumulative normal
}
```

Spread becomes: `(impliedProb - actualProb) * notional`, and you only trade when this exceeds fees.

### 2. Upgrade to WebSocket Streaming

Replace OKX REST polling with OKX WebSocket:

```
WSS endpoint: wss://ws.okx.com:8443/ws/v5/public
Subscribe: {"op":"subscribe","args":[{"channel":"tickers","instId":"BTC-USDT"}]}
```

Same for Polymarket CLOB WebSocket. This gets you from 2s latency to ~50ms.

### 3. Connect the LLM Signal to Execution

Add a signal channel that feeds into the screener:

```go
type SignalFilter struct {
    latestSignal *valueobject.LLMSignal
    mu           sync.RWMutex
}

func (f *SignalFilter) Enrich(opp *aggregate.Opportunity) *aggregate.Opportunity {
    f.mu.RLock()
    defer f.mu.RUnlock()
    if f.latestSignal == nil {
        return opp
    }
    opp.LLMSignal = f.latestSignal
    // Boost confidence if signal agrees with spread direction
    if opp.Spread.SpreadBps > 0 && f.latestSignal.Direction == "bullish" {
        opp.Spread.SpreadBps *= (1 + f.latestSignal.Confidence)
    }
    return opp
}
```

### 4. Add Execution Interface + SAGA Orchestration

```go
// internal/domain/service/executor.go
type LegExecutor interface {
    PlaceOrder(ctx context.Context, order Order) (Fill, error)
    CancelOrder(ctx context.Context, orderID string) error
}

// Two implementations:
// - PaperExecutor: logs to stdout (current behavior)
// - LiveExecutor: real API calls with HMAC signing
```

For the SAGA pattern (already scaffolded in `temporal/`), execute leg 1 first, then leg 2. If leg 2 fails, compensate leg 1.

### 5. Add Multi-Market Watchlist

```go
// Watch multiple Polymarket conditions simultaneously
type MarketWatchlist struct {
    Conditions map[string]MarketConfig // condition_id -> config
}
type MarketConfig struct {
    ConditionID string
    Strike      float64
    Expiry      time.Time
    Side        string // "yes" or "no"
}
```

This lets you scan all BTC-related Polymarket markets at once, not just a single hardcoded one.

### 6. Add Structured Logging + Metrics

Replace all `fmt.Printf` with `slog` + structured fields. Add Prometheus metrics:

```go
var (
    spreadGauge      = promauto.NewGaugeVec(...)  // current spread in bps
    opportunities    = promauto.NewCounterVec(...) // detected, executed, rejected
    executionLatency = promauto.NewHistogram(...) // time from detection to paper fill
)
```

### 7. Add Unit Tests (Trivially Testable)

The domain layer (`CalculateSpread`, `Screen`, `Evaluate`) has zero dependencies and is perfect for table-driven tests:

```go
func TestCalculateSpread(t *testing.T) {
    tests := []struct{
        name string; bin, poly float64; wantBps float64
    }{
        {"poly above", 78000, 78200, 256.4},
        {"bin above", 78200, 78000, -256.4},
    }
    ...
}
```

---

## New Ideas for the Use Case

### Idea 1: Funding Rate Arbitrage (Near-Zero Risk)

While waiting for the Polymarket BTC-daily market to develop edge, add **OKX funding rate arbitrage** as a second strategy. OKX perpetual swaps have 8h funding payments. When the funding rate is >100bps, you can:
- Short the perp, long spot, collect funding
- This is delta-neutral, not dependent on price direction

This needs: OKX perp ticker + funding rate API, position tracking.

### Idea 2: Order Book Depth (Not Just BBO)

Currently only Best Bid/Offer is used. For real arbitrage, you need **depth at size** — e.g., "there's $50K at the BBO but $500K at 5bps away." This determines your actual fillable size and slippage.

### Idea 3: Cross-Venue Latency Measurement

Add per-venue latency tracking in `Price.Latency`. You already have the field but it's always 0. Measure `time.Now().UnixMilli() - exchange_timestamp` for each price update. If OKX latency is 50ms but Polymarket is 500ms, your "274 bps spread" may have already closed on Polymarket before you can act.

### Idea 4: Polymarket Order Flow Imbalance

Instead of just BBO, compute **order flow imbalance** from the full book:

```
imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
```

This is a leading indicator of probability moves, giving you early signal before the price shifts.

### Idea 5: Hedging with Options

Polymarket binary options have a natural hedge: if you're long "BTC above $78K YES" tokens, delta-hedge by shorting BTC on OKX. The LLM signal can drive the hedge ratio. This turns a directional bet into a volatility bet.

---

## Priority Roadmap

| Priority | Item | Impact |
|----------|------|--------|
| P0 | Fix pricing model (probability vs probability) | Without this, the system detects phantom spreads |
| P0 | Add HTTP status checks + zero-price guards | Prevents garbage data in spread calc |
| P1 | WebSocket for OKX (replace REST poll) | 20x latency improvement |
| P1 | Connect LLM signal to execution loop | Makes reasoning-gap strategy functional |
| P1 | Executor interface abstraction | Enables switching from paper to live |
| P2 | Fix risk manager (`currentUSD` never updates) | Currently inert |
| P2 | Add unit tests for domain layer | Foundation for any future changes |
| P2 | Delete dead code (Binance client, `contains()`) | Reduce confusion |
| P3 | Multi-market watchlist | Scale from 1 to N markets |
| P3 | Structured logging + metrics | Observability for real trading |