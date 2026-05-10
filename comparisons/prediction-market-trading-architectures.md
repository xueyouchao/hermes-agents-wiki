---
title: Prediction Market Trading Architectures
type: comparison
created: 2026-05-03
updated: 2026-05-03
tags: [comparison, prediction-markets, arbitrage, market-making, execution, fintech]
sources: [https://github.com/pmxt-dev/pmxt, https://github.com/Polymarket/poly-market-maker, https://github.com/rodlaf/kalshimarketmaker, https://github.com/YichengYang-Ethan/oracle3, https://github.com/RichardFeynmanEnthusiast/kalshi-polymarket-arbitrage-bot, https://github.com/haredoggy/Prediction-Markets-Trading-Bot-Toolkits]
---

# Prediction Market Trading Architectures

## Overview

This comparison focuses on architecture, not profitability. The goal is to identify reusable system patterns for `speedgap-prototype`.

## Comparison Table

| Dimension | [[pmxt]] | [[poly-market-maker]] | [[kalshi-market-maker]] | [[kalshi-polymarket-arbitrage-bot]] | [[oracle3]] | [[polymarket-toolkits]] |
|---|---|---|---|---|---|---|
| Primary role | Unified API layer | Single-venue market maker | Dynamic market maker | Cross-venue arb engine | Pricing + execution stack | Multi-strategy engine |
| Core abstraction | Exchange adapter | Sync reconciliation loop | Per-market worker | Domain events + shared market state | Pricing/strategy/execution separation | Shared services under strategy bots |
| Venue scope | Broad | Polymarket | Kalshi | Polymarket + Kalshi | Multi-venue | Multi-venue |
| Strategy shape | Strategy-agnostic | Quote engine | Inventory-aware quoting | Reactive arb monitor | Strategy portfolio | Strategy portfolio |
| Risk posture | Mostly API surface | Minimal but deterministic | Strong ops + limits | Balance/risk services | Correlation-aware, multi-layer | Circuit breakers + depth guard |
| Best lesson for us | Adapter boundary | Desired-vs-actual order reconciliation | Worker lifecycle safety | Normalized market state | Separate pricing from execution | Thin strategies over common services |

## Synthesis

### Best reference for adapter design
[[pmxt]]

### Best reference for event-driven state
[[kalshi-polymarket-arbitrage-bot]]

### Best reference for deterministic execution lifecycle
[[poly-market-maker]]

### Best reference for market-making worker safety
[[kalshi-market-maker]]

### Best reference for long-term platform direction
[[polymarket-toolkits]]

### Best reference for model/pricing separation
[[oracle3]]

## What speedgap-prototype should borrow first

1. **Adapter boundary** from [[pmxt]]
2. **Shared market-state model** from [[kalshi-polymarket-arbitrage-bot]]
3. **Desired-state reconciliation** from [[poly-market-maker]]
4. **Worker lifecycle + cleanup invariants** from [[kalshi-market-maker]]
5. **Shared engine services** from [[polymarket-toolkits]]

## What to defer

- Full multi-venue abstraction everywhere before Strategy B and current weather flows are stable
- Sophisticated pricing models like [[oracle3]] until there is enough execution and calibration infrastructure to support them

## Related
- [[prediction-markets-research]]
- [[polymarket-ai-arbitrage]]
