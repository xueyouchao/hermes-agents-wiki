---
title: Temporal
created: 2026-04-16
updated: 2026-04-16
type: entity
tags: [temporal, platform, durable-execution, open-source]
sources: [raw/articles/temporal-io-homepage.md]
---

# Temporal

Temporal is an open-source platform that enables **Durable Execution**, allowing developers to build applications that maintain state and recover automatically from failures in distributed systems.

## Overview

Temporal solves the problem of building reliable distributed applications by capturing the state of code at every step, making infrastructure failures (network flakes, service crashes, API timeouts) irrelevant.

## Key Facts

| Property | Value |
|----------|-------|
| License | MIT (open source) |
| GitHub Stars | 19,600+ |
| Founded by | Creators of AWS SQS, AWS SWF, Uber's Cadence |

## Products

- **Temporal Cloud**: Managed service offering
- **Self-Hosted**: 100% open source deployment

## SDK Support

Temporal provides native SDKs for: Python, Go, TypeScript, Ruby, C#, Java, and PHP.

## Use Cases

- AI agents - Reliable orchestration for multi-step LLM systems
- Fintech - Durable ledgers and multi-step transaction handling
- Infrastructure - CI/CD, cloud deployment, and fleet management
- E-commerce - Order fulfillment and customer onboarding

## Notable Users

Companies using Temporal include OpenAI, NVIDIA, Salesforce, Netflix, Snap, Cloudflare, and DoorDash.

## Architecture Overview

```mermaid
flowchart TB
    subgraph Client["Client Applications"]
        API[Temporal SDK Client]
    end

    subgraph Cluster["Temporal Cluster"]
        FE[Frontend Service]
        History[History Service]
        Matching[Matching Service]
        Worker[Worker Service]
        DB[(Persistence<br/>Database)]
    end

    subgraph Workers["Worker Processes"]
        WW[Workflow Worker]
        AW[Activity Worker]
    end

    subgraph TaskQueues["Task Queues"]
        TQ1[Workflow Task Queue]
        TQ2[Activity Task Queue]
    end

    API --> |gRPC| FE
    FE --> |Route| History
    FE --> |Route| Matching
    
    History <--> |Read/Write| DB
    Matching <--> |Read/Write| DB
    
    History --> |Schedule| TQ1
    Matching --> |Dispatch| TQ2
    
    WW -.-> |Poll| TQ1
    AW -.-> |Poll| TQ2
    
    WW --> |Execute| Workflow
    AW --> |Execute| Activity
    
    Workflow -.-> |1. Call| Activity
    Activity -.-> |2. Complete| Workflow
```

## Concepts Map

```mermaid
flowchart LR
    subgraph Core["Core Concepts"]
        DE[Durable<br/>Execution]
        WF[Workflow]
        AC[Activity]
        RP[Replay]
    end

    subgraph Infrastructure["Infrastructure"]
        CL[Cluster]
        PS[Persistence]
        WH[Workflow<br/>History]
    end

    subgraph Deployment["Deployment Options"]
        TC[Temporal<br/>Cloud]
        SH[Self-Hosted]
    end

    DE --> WF
    DE --> AC
    WF -.-> |calls| AC
    RP -.-> |restores| WF
    WF --> |persisted to| WH
    WH --> PS
    PS --> CL
    TC <--> CL
    SH --> CL
```

## Related

- [[durable-execution]] - The core concept behind Temporal
- [[temporal-cloud]] - Managed deployment option
- [[self-hosted-temporal]] - Self-hosted deployment option
