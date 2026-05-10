---
title: kalshi-market-maker
created: 2026-05-03
updated: 2026-05-03
type: entity
tags: [prediction-markets, kalshi, market-making, risk-management, fintech]
sources: [https://github.com/rodlaf/kalshimarketmaker]
---

# kalshi-market-maker

## Overview

Dynamic Kalshi market-making bot with explicit safety controls. It selects markets, launches one Avellaneda-Stoikov worker per market, and enforces both portfolio-level and per-market limits.

## Key patterns

- Dynamic market selector before worker launch
- One worker per market instead of one giant loop
- Inventory-aware quoting via reservation price and skew
- Cleanup invariant when a worker is removed: stop, wait, cancel, verify cleanup
- Operational tooling for cancel-all and liquidation

## Why it matters

The important lesson is architectural, not mathematical: **worker lifecycle management** is part of strategy safety. This is directly relevant for `speedgap-prototype` if weather strategies expand across cities, dates, or venues and need independent execution units.

## Reusable lesson

A future `speedgap-prototype` could treat each event or market family as an isolated worker with its own state, while a portfolio risk layer governs aggregate exposure.

## Related
- [[prediction-markets-research]]
- [[prediction-market-trading-architectures]]
- [[poly-market-maker]]
