---
title: Durable Execution
created: 2026-04-16
updated: 2026-04-16
type: concept
tags: [durable-execution, concept, patterns]
sources: [raw/articles/temporal-io-homepage.md]
---

# Durable Execution

Durable Execution is a programming model where the platform automatically captures the state of application code at every step, enabling automatic recovery from failures without manual intervention.

## Core Benefits

1. **Automatic Recovery**: Workflows pick up exactly where they left off after any failure
2. **No Manual Recovery**: Eliminates complex reconciliation logic
3. **Full Visibility**: Complete insight into the exact state of every execution

## How It Works

The platform persists:
- Progress of each workflow execution
- All variables and local state
- Timer states and signals
- Activity results and retry history

When a failure occurs (process crash, network partition, timeout), the system replays the workflow from the last checkpoint, restoring exact state.

## How Replay Works

```mermaid
flowchart LR
    subgraph Normal["Normal Execution"]
        E1[Execute Step 1] --> E2
        E2[Execute Step 2] --> E3
        E3[Execute Step 3] --> E4[Complete]
        E1 -.-> |Persist Event| H1[(History<br/>Event 1)]
        E2 -.-> |Persist Event| H2[(History<br/>Event 2)]
        E3 -.-> |Persist Event| H3[(History<br/>Event 3)]
    end

    subgraph Recovery["Failure & Recovery"]
        Fail{{Worker Crash}} ==> Replay
        Replay["Replay from<br/>History"] ==> E2R
        E2R[Re-execute<br/>Step 2] -.->|Same Results| E2
    end
    
    E2 --> Fail
```

## Comparison to Traditional Approaches

| Approach | Recovery | State Management | Visibility |
|----------|----------|------------------|------------|
| Durable Execution | Automatic | Platform-managed | Built-in |
| Manual Checkpointing | Developer-coded | Developer-coded | Logs |
| Event Sourcing | Replay events | Custom | Custom |

## Related Concepts

- [[workflow]] - Durable code that defines business logic
- [[activity]] - Failure-prone functions with retries
- [[replay]] - Re-executing workflow from last checkpoint
- [[temporal]] - Platform implementing durable execution