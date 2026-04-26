# DDD Domain Model — Polymarket AI Arbitrage System

## Bounded Contexts

```
+--------------------------------------------------+
|                   Arbitrage Core                   |
|  (Domain: price discovery, spread capture, PnL)   |
+--------------------------------------------------+  
         |                  |                 |
         v                  v                 v
+----------------+ +----------------+ +--------------+
| Market Data    | | Execution      | | LLM Signal   |
| Context (read) | | Context        | | Context      |
|                | | (write/orders) | | (reasoning)  |
+----------------+ +----------------+ +--------------+
         |                                 |
         v                                 v
+--------------------------------------------------+
|                 Temporal Orchestration             |
|  (workflow engine, durable execution, saga)       |
+--------------------------------------------------+
```

## Aggregates & Entities

### 1. Opportunity (Aggregate Root)
```
Opportunity {
  id: UUID
  marketId: MarketID
  type: SpeedArbitrage | ReasoningGap | FragmentationGap
  state: OPEN | EXECUTING | FILLED | EXPIRED | FAILED
  spread: Spread (value object)
  confidence: ConfidenceScore
  createdAt: UTC
  expiresAt: UTC  // 2.7s TTL per article
}
```

### 2. Trade (Aggregate Root)
```
Trade {
  id: UUID
  opportunityId: UUID
  legs: [Leg]
  state: PENDING | EXECUTED | SETTLED | FAILED
  PnL: Money
  commission: Money
  createdAt: UTC
  settledAt: UTC
}
```

### 3. Signal (Aggregate Root)
```
Signal {
  id: UUID
  source: LLM_MODEL | NEWS_FEED | FED_STATEMENT
  event: Event
  interpretation: LLMInterpretation
  confidence: [0.0, 1.0]
  actionableMarkets: [MarketID]
  validUntil: UTC
}
```

## Value Objects

| VO | Fields | Invariants |
|----|--------|------------|
| Spread | bid, ask, midpoint, percentage | spread > 0; percentage >= 0 |
| Money | amount, currency | currency ∈ [USDC, ETH, BTC] |
| MarketID | source, pair, contract | source ∈ [POLYMARKET, BINANCE, OKX] |
| ConfidenceScore | score, model, version | score ∈ [0, 1] |

## Domain Events

```
OpportunityDetected(opportunityId, spread, source)
SignalReceived(signalId, event, confidence)
TradeLegExecuted(tradeId, leg, fillPrice)
TradeSettled(tradeId, PnL, duration)
ArbitrageWindowClosed(opportunityId, reason)
```

## Domain Services

| Service | Responsibility |
|---------|---------------|
| OpportunityScreener | Continuously rank opportunities by EV (expected value) per Sharpe ratio |
| SpreadCalculator | Cross-market fair-value computation, accounting for fees |
| ExecutionRouter | Best-execution logic across venues (latency-weighted routing) |
| RiskManager | Position sizing, max drawdown, correlation limits |
| SignalInterpreter | Hydrate raw LLM output into structured Signal aggregate |

## Anti-Corruption Layers

```
Polymarket API  --ACL-->  Domain Events (normalized)
Binance API     --ACL-->  Domain Events
OpenRouter LLM  --ACL-->  Signal Interpreter
```

## Ubiquitous Language

| Term | Definition |
|------|------------|
| Arbitrage Window | The time delta between inefficiency emergence and closure. Target < 2.7s. |
| Speed Gap | Pricing lag between Polymarket contract and spot CEX. |
| Reasoning Gap | LLM-based interpretation of public info faster than market pricing. |
| Leg | One side of a multi-sided trade (buy on A, sell on B = 2 legs). |
| EV (Expected Value) | Spread % minus transaction costs, adjusted by probability of fill. |
| Alpha Decay | Rate at which arbitrage signal becomes useless. Article: 12.3s → 2.7s in 18 months. |
