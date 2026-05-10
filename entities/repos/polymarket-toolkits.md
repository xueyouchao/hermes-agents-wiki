---
title: polymarket-toolkits
created: 2026-05-03
updated: 2026-05-03
type: entity
tags: [prediction-markets, polymarket, kalshi, multi-strategy, risk-management, fintech]
sources: [https://github.com/haredoggy/Prediction-Markets-Trading-Bot-Toolkits]
---

# polymarket-toolkits

## Overview

Rust-based multi-venue trading engine covering Polymarket, Kalshi, and Limitless. The current shipping bot is copy trading, but the architecture is explicitly designed for a family of strategies including cross-market arb, direction hunting, market making, orderbook imbalance, and resolution sniping.

## Key patterns

- Venue adapters separated from shared services
- Shared services for positions, orders, market cache, and price feeds
- Thin bot modules for each strategy family
- Centralized risk guard and orderbook-depth checks
- TUI and ops tooling built around the same engine core

## Why it matters

This is the closest template for what `speedgap-prototype` could become if it grows from a single bot into a **strategy platform**. The important lesson is not the exact Rust stack; it is the separation of reusable services from strategy orchestration.

## Reusable lesson

Make strategies plug into common primitives: market metadata cache, order placement, risk checks, reconciliation, and observability.

## Related
- [[prediction-markets-research]]
- [[prediction-market-trading-architectures]]
- [[oracle3]]
