---
title: Self-Hosted Temporal
created: 2026-04-16
updated: 2026-04-16
type: concept
tags: [self-hosted, temporal, deployment, infrastructure]
sources: [raw/articles/temporal-io-homepage.md]
---

# Self-Hosted Temporal

Self-hosted Temporal is the 100% open-source, MIT-licensed deployment option for organizations that want to run Temporal on their own infrastructure.

## Deployment Options

### Docker Compose
Single-machine development and testing

### Kubernetes
Production-grade deployment with:
- High availability
- Auto-scaling
- Custom persistence backends

### Bare Metal
For organizations with specific infrastructure requirements

## Persistence Backends

Temporal supports multiple databases:
- PostgreSQL
- MySQL
- Cassandra
- Elasticsearch (for visibility)

## Comparison

| Aspect | Self-Hosted | Temporal Cloud |
|--------|-------------|----------------|
| Management | Self-managed | Fully managed |
| Cost | Infrastructure only | Subscription |
| Control | Full | Limited |
| Support | Community | Enterprise |

## Related

- [[temporal]] - The platform
- [[temporal-cloud]] - Managed alternative
- [[cluster]] - Temporal cluster architecture
- [[persistence]] - Database backend options