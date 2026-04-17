---
title: Amazon S3
created: 2026-04-16
updated: 2026-04-17
type: entity
tags: [aws, cloud, storage, s3]
sources: [https://aws.amazon.com/s3/]
---

# Amazon S3

Amazon S3 is AWS's managed object storage service. Within this wiki it functions as the storage foundation behind analytics, data lakes, ML datasets, and application content delivery.

## Core Strengths

- Durable, elastic object storage
- Broad integration with analytics and AI workflows
- Multiple storage classes for cost and latency tradeoffs
- Event hooks that connect storage to application logic

## Typical Uses

- Data lake storage for analytics and ML
- Model artifacts, datasets, and training inputs
- Static application assets and backups
- Event-driven pipelines with downstream compute triggers

## Related Services

- [[aws-ec2]] - Compute accessing S3-hosted data
- [[aws-eks]] - Kubernetes workloads using S3-backed data
- [[aws-ecs]] - Container workloads integrated with S3
- Glacier storage classes - Long-term archival tiering

## References

- [S3 Product Page](https://aws.amazon.com/s3/)
- [S3 Documentation](https://docs.aws.amazon.com/s3/)
