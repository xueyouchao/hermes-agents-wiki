---
title: Workflow
created: 2026-04-16
updated: 2026-04-16
type: concept
tags: [workflow, concept, temporal]
sources: [raw/articles/temporal-io-homepage.md]
---

# Workflow

A Workflow in Temporal is durable, fault-tolerant code that defines business logic. Workflows are the core execution unit that maintains state across failures.

## Characteristics

- **Durable**: Survives process crashes, restarts, and failures
- **Idempotent**: Can safely replay from checkpoints
- **Deterministic**: Same inputs produce same outputs (required for replay)

## Workflow Types

### Long-Running Workflows
Continuous processes that may run for days or weeks, such as:
- Order processing pipelines
- AI model training orchestration
- Human-in-the-loop approvals

### Periodic Workflows
Scheduled tasks that run on intervals:
- Data synchronization jobs
- Report generation
- Cleanup tasks

## Key Features

### Execution Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant W as Workflow
    participant A as Activity
    participant T as Temporal Cluster
    
    C->>T: Start Workflow
    T->>W: Create Workflow Execution
    W->>A: Schedule Activity
    A->>T: Activity Task
    T->>A: Dispatch to Worker
    A-->>T: Activity Result
    T-->>W: Activity Completion
    W->>T: Continue Execution
    T-->>C: Workflow Result
```

### Signals, Timers, and Child Workflows

```mermaid
flowchart TB
    subgraph Workflow["Workflow"]
        Start((Start))
        Signal1[Signal: User Input]
        Timer[Timer: Delay/Wait]
        Child[Child Workflow]
        Query[Query: Read State]
        End((Complete))
    end
    
    Start --> Signal1
    Signal1 --> Timer
    Timer --> Child
    Child --> Query
    Query --> End
    
    Signal1 -.-> |External Event| Signal1
    Timer -.-> |Fires After Delay| Timer
    Query -.-> |Read-Only| Query
```

### Workflow Types

### Long-Running Workflows

## Related

- [[durable-execution]] - The execution model
- [[activity]] - Failure-prone operations called by workflows
- [[temporal]] - Platform hosting workflows
- [[replay]] - Recovery mechanism