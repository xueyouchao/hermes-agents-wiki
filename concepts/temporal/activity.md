---
title: Activity
created: 2026-04-16
updated: 2026-04-16
type: concept
tags: [activity, concept, temporal]
sources: [raw/articles/temporal-io-homepage.md]
---

# Activity

An Activity is a function in Temporal designed to handle failure-prone logic, such as calling third-party APIs, with built-in automatic retries.

## Purpose

Activities handle the unreliable parts of distributed systems:
- External API calls
- Database operations
- File I/O
- Network requests

## Key Features

### Automatic Retries
Activities automatically retry on failure with configurable:
- Retry policies (backoff, max attempts)
- Timeouts (start-to-close, schedule-to-start)
- Heartbeats for long-running operations

### Timeout Handling
- **Schedule-to-Start**: Max time before activity starts
- **Start-to-Close**: Max time for activity to complete
- **Heartbeat**: Timeout for activity progress reporting

### Idempotency
Activities should be idempotent since they may execute multiple times due to retries.

## Relationship to Workflows

Workflows orchestrate activities:

```mermaid
flowchart LR
    subgraph Workflow["Workflow Execution"]
        W1[Start] --> W2[Schedule Activity]
        W2 --> W3[Wait for Result]
        W3 --> W4[Continue]
        W4 --> W5[Complete]
    end

    subgraph Activity["Activity Execution"]
        A1[Dispatch to Worker] --> A2[Execute]
        A2 --> A3{Success?}
        A3 -->|Yes| A4[Return Result]
        A3 -->|No| A5[Wait Backoff]
        A5 --> A1
    end
    
    W2 -.-> |1. Schedule| A1
    A4 -.-> |2. Complete| W3
```

### Retry Flow

```mermaid
stateDiagram-v2
    [*] --> Start
    Start --> Execute: Start Activity
    Execute --> Success: Complete
    Execute --> Fail: Error
    Fail --> Wait: Retry Policy
    Wait --> Execute: Backoff Complete
    Fail --> [*]: Max Retries Exceeded
    Success --> [*]
```

If activity fails, it's retried automatically. If workflow fails, it replays from last checkpoint and re-calls activities (which may have already succeeded).

## Related

- [[workflow]] - Calls activities to execute business logic
- [[durable-execution]] - Overall execution model
- [[temporal]] - Platform providing activity infrastructure
- [[compensation]] - Handling partial failures with Saga pattern