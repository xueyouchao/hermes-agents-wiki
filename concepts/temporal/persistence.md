---
title: Persistence
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [temporal, persistence, storage]
sources: [raw/articles/temporal-io-homepage.md]
---

# Persistence

Persistence is the storage layer that holds workflow event history, state transitions, timers, and metadata. It is what makes replay and recovery possible in a durable execution system.

## Why It Matters

- Stores the authoritative workflow history
- Enables recovery after worker and process failures
- Supports visibility into execution progress over time

## Related

- [[durable-execution]] - Persistence is the basis of durability
- [[replay]] - Replay consumes persisted history
- [[cluster]] - Clusters depend on a persistence layer
