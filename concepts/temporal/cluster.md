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

## Responsibilities

- Persist workflow histories and metadata
- Schedule work onto task queues
- Serve the Temporal API for workers and clients

## Related

- [[self-hosted-temporal]] - Running a cluster yourself
- [[persistence]] - Storage layer behind workflow durability
- [[temporal]] - Product that exposes the cluster model
