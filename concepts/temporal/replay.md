---
title: Replay
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [temporal, replay, durable-execution]
sources: [raw/articles/temporal-io-homepage.md]
---

# Replay

Replay is the mechanism Temporal uses to rebuild workflow state after a worker restarts or fails. The runtime re-executes deterministic workflow code against the persisted event history so the workflow resumes with the same logical state.

## Why It Matters

- Preserves workflow progress without manual checkpoint logic
- Lets workers recover from crashes and redeployments
- Enforces deterministic workflow code as part of the programming model

## Related

- [[durable-execution]] - The higher-level model that depends on replay
- [[workflow]] - Workflow code must be replay-safe
- [[activity]] - Side effects are kept outside workflow replay
