---
title: Prediction Markets Research
type: summary
created: 2026-05-03
updated: 2026-05-03
tags: [prediction-markets, fintech, arbitrage, market-making, reference]
sources: [https://github.com/pmxt-dev/pmxt, https://github.com/Polymarket/poly-market-maker, https://github.com/rodlaf/kalshimarketmaker, https://github.com/YichengYang-Ethan/oracle3, https://github.com/RichardFeynmanEnthusiast/kalshi-polymarket-arbitrage-bot, https://github.com/haredoggy/Prediction-Markets-Trading-Bot-Toolkits]
---

# Prediction Markets Research

## Overview

This hub tracks open-source prediction-market trading infrastructure that is directly relevant to [[polymarket-ai-arbitrage]], [[pmxt]], [[poly-market-maker]], [[kalshi-market-maker]], [[oracle3]], [[kalshi-polymarket-arbitrage-bot]], and [[polymarket-toolkits]].

The most reusable patterns fall into five buckets:

1. **Unified venue adapters** for Polymarket, Kalshi, and adjacent exchanges
2. **Orderbook-first execution engines** with explicit partial-fill handling
3. **Market-making loops** that continuously cancel/replace around a reference price
4. **Event-driven arbitrage systems** that normalize venue data into a shared state model
5. **Risk layers** that treat circuit breakers, inventory, and reconciliation as first-class modules

## Key Architecture Patterns

### 1. Unified exchange abstraction
- [[pmxt]] shows the cleanest external example of a unified API over prediction venues.
- The value is not just convenience; it creates a stable boundary between strategy code and venue-specific signing, pagination, and market metadata quirks.

### 2. Thin strategies over shared services
- [[polymarket-toolkits]] organizes strategy bots as thin orchestrators over shared services like market cache, orders, positions, price feeds, and risk guards.
- This matches the direction of ADR 0004 in `speedgap-prototype`: a scheduler plus registered strategy modules instead of a god object.

### 3. Reactive state pipelines
- [[kalshi-polymarket-arbitrage-bot]] uses a domain event pipeline: ingest venue deltas → update unified market state → detect arb → execute.
- This is the strongest reference for moving from polling-oriented logic toward event-driven detection.

### 4. Safety as core engine logic
- [[poly-market-maker]], [[kalshi-market-maker]], and [[oracle3]] all treat execution safety as architecture, not as an afterthought.
- Common mechanisms: explicit cleanup invariants, position caps, partial-fill unwind, cooldowns, and operator kill switches.

### 5. Strategy families, not one-off bots
- [[oracle3]] and [[polymarket-toolkits]] frame strategies as a portfolio of reusable modules sharing a pricing, execution, and risk core.
- That framing is more extensible than embedding each new edge directly into the main trading engine.

## Comparison Shortlist

| Repo | Primary Value | Best Reusable Lesson |
|---|---|---|
| [[pmxt]] | Unified market/trading API | Separate venue adapters from strategy logic |
| [[poly-market-maker]] | Minimal market-making lifecycle | Deterministic cancel/replace sync loop |
| [[kalshi-market-maker]] | Dynamic worker + inventory control | Per-market workers with portfolio caps |
| [[kalshi-polymarket-arbitrage-bot]] | Event-driven cross-venue arb | Shared market state and domain events |
| [[oracle3]] | Pricing + execution + risk stack | Model/pricing layer separated from execution layer |
| [[polymarket-toolkits]] | Multi-strategy engine shape | Shared services under many bots |

## Direct Relevance to speedgap-prototype

The current `speedgap-prototype` code already has the beginnings of the right shape:
- ADR 0003 extracts Strategy B execution into a deep module.
- ADR 0004 defines a registered strategy abstraction.
- `strategy_b.py` already encodes a strong invariant-driven arb scanner.

The next step is to push more of the system toward:
- venue abstraction,
- strategy-local execution modules,
- shared real-time market state,
- and stronger execution/risk observability.

## Related Pages
- [[prediction-market-trading-architectures]]
- [[polymarket-ai-arbitrage]]
- [[pmxt]]
- [[poly-market-maker]]
- [[kalshi-market-maker]]
- [[oracle3]]
- [[kalshi-polymarket-arbitrage-bot]]
- [[polymarket-toolkits]]
