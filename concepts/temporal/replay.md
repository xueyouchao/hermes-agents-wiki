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

## How Replay Works

```mermaid
flowchart TB
    subgraph EventHistory["Event History (Persisted)"]
        E1[Event 1<br/>WorkflowStarted]
        E2[Event 2<br/>ActivityScheduled]
        E3[Event 3<br/>ActivityCompleted]
        E4[Event 4<br/>ActivityScheduled]
        E5[Event 5<br/>...]
    end

    subgraph Replay["Replay Process"]
        R1[Load Event History]
        R2[Re-execute from Event 1]
        R3[Skip Already<br/>Completed Steps]
        R4[Resume from<br/>Checkpoint]
    end
    
    E1 --> R1
    R1 --> R2
    R2 --> R3
    R3 --> R4
```

### Key Points

1. **Deterministic Code**: Workflow code must be deterministic for replay to work correctly
2. **Event Sourcing**: All state changes are stored as events, not just final state
3. **Idempotent Activities**: Activities should be idempotent since they may be re-executed

## Why It Matters

- Preserves workflow progress without manual checkpoint logic
- Lets workers recover from crashes and redeployments
- Enforces deterministic workflow code as part of the programming model

## Related

- [[durable-execution]] - The higher-level model that depends on replay
- [[workflow]] - Workflow code must be replay-safe
- [[activity]] - Side effects are kept outside workflow replay
