---
title: poly-market-maker
created: 2026-05-03
updated: 2026-05-03
type: entity
tags: [prediction-markets, polymarket, market-making, clob, execution, fintech]
sources: [https://github.com/Polymarket/poly-market-maker]
---

# poly-market-maker

## Overview

Official-style Polymarket market-maker keeper for CLOB markets. It runs a deterministic sync cycle that fetches midpoint, computes desired quotes, compares desired versus open orders, then cancels/replaces to converge toward the target book shape.

## Core lifecycle

Every sync interval it:
1. fetches midpoint,
2. computes expected orders,
3. diffs them against live resting orders,
4. cancels stale orders,
5. places new orders.

## Why it matters

This is the cleanest minimal reference for a **quote engine loop**. It is useful even outside literal market making because it makes the execution lifecycle explicit: compute desired state, diff actual state, then reconcile.

## Reusable lesson

`speedgap-prototype` should separate **desired position/order state** from **exchange reconciliation logic**. Strategy B already hints at this with intent recording and rollback, but the same pattern can be generalized for future strategies.

## Related
- [[prediction-markets-research]]
- [[prediction-market-trading-architectures]]
- [[kalshi-market-maker]]
