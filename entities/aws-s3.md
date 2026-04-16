---
title: Amazon S3
created: 2026-04-16
updated: 2026-04-16
type: entity
tags: [aws, cloud, storage, s3]
sources: [raw/articles/aws-s3-2026.md]
---

# Amazon S3 (Simple Storage Service)

Amazon S3 is an industry-leading object storage service designed for scalability, data availability, security, and performance. Launched on March 14, 2006, it has evolved from "storage for the internet" to a foundational data layer for AI and analytics.

## Key Performance Statistics

| Metric | Value |
|--------|-------|
| Objects Stored | 500 trillion+ |
| Requests/Second | 200 million+ |
| Daily Event Notifications | 300 billion+ |
| Customer Savings (Intelligent-Tiering) | $6 billion+ |

## Core Benefits

- **Durability & Availability:** 99.999999999% (11 nines) durability, 99.99% availability
- **Scalability:** Fully elastic — grows and shrinks automatically
- **Security:** Encrypted by default with robust auditing and access controls
- **Cost-Efficiency:** Multiple storage classes with automated lifecycle management

## Specialized Storage Classes

| Class | Use Case |
|-------|----------|
| S3 Express One Zone | Single-digit millisecond latency, 10x faster than Standard |
| S3 Tables | Native Apache Iceberg support with automatic compaction |
| S3 Vectors | Vector storage for AI, up to 90% cost reduction |
| S3 Glacier | Low-cost archival storage |

## Primary Use Cases

### 1. Data Lakes & Analytics
S3 serves as the foundation for over 1,000,000 data lakes. Supports open table formats (Apache Iceberg) for queries directly against a single data copy.

### 2. Artificial Intelligence & Machine Learning
- Foundation for [[durable-execution|Foundation Model]] training
- RAG (Retrieval-Augmented Generation) enhancement
- High-performance training with S3 Express One Zone

### 3. Semantic Search
Using S3 Vectors for vector embeddings storage and query in a serverless architecture.

### 4. Backup and Compliance
Integration with [[aws-backup|AWS Backup]] and replication for RTO/RPO requirements.

## Notable Customers

- **The BBC:** Preserving 100 years of historical archives
- **Adobe:** Generative AI leadership
- **GE HealthCare:** "Health Cloud" for patient outcomes
- **Indeed:** S3 Tables for data governance

## Related Services

- [[aws-ec2|EC2]] — Compute that accesses S3 data
- [[aws-eks|EKS]] — Kubernetes with S3 file integration
- [[aws-ecs|ECS]] — Containers with S3 connectivity
- [[aws-glacier|AWS Glacier]] — Archival storage companion

## References

- [S3 Product Page](https://aws.amazon.com/s3/)
- [S3 Documentation](https://docs.aws.amazon.com/s3/)
