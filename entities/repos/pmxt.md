---
title: pmxt
created: 2026-05-03
updated: 2026-05-03
type: entity
tags: [prediction-markets, polymarket, kalshi, unified-api, fintech, reference]
sources: [https://github.com/pmxt-dev/pmxt]
---

# pmxt

## Overview

`pmxt` describes itself as the **CCXT for prediction markets**. It exposes a unified API for market discovery and trading across Polymarket, Kalshi, Limitless, Probable, Myriad, Opinion, Metaculus, and Smarkets.

## Why it matters

For `speedgap-prototype`, `pmxt` is the clearest proof that **venue-specific details should be isolated behind adapters**. The strategy layer should not need to know how Polymarket signs orders versus how Kalshi authenticates requests.

## Key patterns

- Unified `Exchange()` abstraction for multi-venue reads
- Venue-specific authenticated clients for trading
- Shared hierarchy: event -> market -> outcome
- Python, TypeScript, and MCP surfaces for the same conceptual API
- Migration tooling for replacing narrower APIs with the unified layer

## Reusable lesson

If `speedgap-prototype` continues beyond a Kalshi-first weather bot, a venue adapter boundary like `pmxt` is more scalable than letting strategy code depend directly on each exchange client's raw response shape.

## Related
- [[prediction-markets-research]]
- [[prediction-market-trading-architectures]]
- [[kalshi-polymarket-arbitrage-bot]]
