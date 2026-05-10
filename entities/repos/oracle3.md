---
title: oracle3
created: 2026-05-03
updated: 2026-05-03
type: entity
tags: [prediction-markets, pricing, arbitrage, risk-management, fintech, event-driven]
sources: [https://github.com/YichengYang-Ethan/oracle3]
---

# oracle3

## Overview

`oracle3` is an autonomous prediction-market trading agent spanning Kalshi, Polymarket, and Solana. Its most interesting property is that it separates a **pricing engine** from the **strategy layer** and from the **execution/risk layer**.

## Architecture

The README describes a stack of:
- Wang Transform pricing engine
- fair-value estimator and Kelly sizing
- strategy layer (constraint-based, statistical, and model-driven)
- trading engine with spread executor, risk manager, and position tracker

## Why it matters

This is the strongest external reference for keeping **pricing logic independent from trade execution**. `speedgap-prototype` currently has simple heuristics for BTC and weather probabilities; `oracle3` shows how to evolve toward a richer pricing layer without entangling execution code.

## Reusable lesson

Introduce a dedicated pricing/model layer for strategies that need it, but keep invariant-based arbitrage strategies like Strategy B independent from model risk.

## Related
- [[prediction-markets-research]]
- [[prediction-market-trading-architectures]]
- [[pmxt]]
