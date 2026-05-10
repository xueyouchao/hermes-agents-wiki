---
title: kalshi-polymarket-arbitrage-bot
created: 2026-05-03
updated: 2026-05-03
type: entity
tags: [prediction-markets, kalshi, polymarket, arbitrage, event-driven, fintech]
sources: [https://github.com/RichardFeynmanEnthusiast/kalshi-polymarket-arbitrage-bot]
---

# kalshi-polymarket-arbitrage-bot

## Overview

Cross-venue arbitrage bot built with domain-driven design, event-driven architecture, and ports/adapters. It normalizes venue-specific orderbook updates into a shared market-state model before checking opportunities.

## Key patterns

- Shared domain models: `Orderbook`, `MarketState`, `ArbitrageOpportunity`
- Event bus for normalized venue deltas
- `MarketManager` updates state, `ArbitrageMonitor` detects edge, `TradeExecutor` handles execution
- Balance service owns wallet-state constraints
- Explicit cool-down/reset after execution

## Why it matters

This is the best reference for turning polling code into a **reactive trading pipeline**. The strongest idea is that strategies should consume a normalized market state rather than each strategy re-parsing raw exchange payloads.

## Reusable lesson

`speedgap-prototype` would benefit from a shared in-memory market-state layer, especially if BTC and weather strategies begin to consume multiple venues or need faster refresh loops.

## Related
- [[prediction-markets-research]]
- [[prediction-market-trading-architectures]]
- [[pmxt]]
