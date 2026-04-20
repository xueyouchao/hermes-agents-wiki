---
title: Temporal Cluster
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [temporal, cluster, infrastructure]
sources: [raw/articles/temporal-io-homepage.md]
---

# Temporal Cluster

A Temporal cluster is the backend service deployment that stores workflow histories, manages task queues, and coordinates workers. It is the operational foundation behind self-hosted Temporal.

## Architecture

```mermaid
flowchart TB
    subgraph Cluster["Temporal Cluster"]
        LB[Load Balancer]
        
        subgraph Services["Core Services"]
            FE[Frontend<br/>Service]
            HS[History<br/>Service]
            MS[Matching<br/>Service]
            WS[Worker<br/>Service]
        end
        
        subgraph Storage["Persistence Layer"]
            DB[(Database)]
            ES[(Elasticsearch<br/>Optional)]
        end
    end
    
    subgraph External["External Components"]
        Worker1[Workflow<br/>Worker]
        Worker2[Activity<br/>Worker]
        Client[SDK Client]
    end
    
    Client --> LB
    LB --> FE
    FE --> HS
    FE --> MS
    
    HS <--> DB
    MS <--> DB
    HS <--> ES
    
    HS --> WS
    WS --> Worker1
    WS --> Worker2
```

## Responsibilities

- Persist workflow histories and metadata
- Schedule work onto task queues
- Serve the Temporal API for workers and clients

## Services

| Service | Responsibility |
|---------|---------------|
| Frontend | Handle API requests, authentication, rate limiting |
| History | Manage workflow execution state and event history |
| Matching | Match tasks to workers, poll management |
| Worker | Register workers, manage task queues |

## Related

- [[self-hosted-temporal]] - Running a cluster yourself
- [[persistence]] - Storage layer behind workflow durability
- [[temporal]] - Product that exposes the cluster model
