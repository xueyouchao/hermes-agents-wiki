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

- **Signals**: Async events that can modify workflow state
- **Timers**: Delayed execution and timeouts
- **Child Workflows**: Compose complex processes
- **Queries**: Read-only state inspection

## Related

- [[durable-execution]] - The execution model
- [[activity]] - Failure-prone operations called by workflows
- [[temporal]] - Platform hosting workflows
- [[replay]] - Recovery mechanism