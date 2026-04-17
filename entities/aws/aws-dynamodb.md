--- 
title: Amazon DynamoDB
created: 2026-04-16
updated: 2026-04-16
type: entity
tags: [aws, cloud, database, nosql, dynamodb]
sources: [https://aws.amazon.com/dynamodb/]
---

# Amazon DynamoDB

Amazon DynamoDB is a serverless, fully managed, distributed NoSQL database designed to provide single-digit millisecond performance at any scale. It eliminates infrastructure management, offering instant scaling and high resilience.

## Key Features

- **Serverless Architecture:** Zero infrastructure management, no downtime, no version upgrades
- **Performance:** Single-digit millisecond latency at any scale
- **High Availability:** Up to 99.999% availability with Global Tables
- **Cost Optimization:** Pay-per-request billing, 25% lower cost than equivalent databases

## Scale Metrics

| Metric | Value |
|--------|-------|
| Customers | 1 million+ |
| Requests/Second (sustained) | 500,000+ |
| Table Sizes | 200TB+ for hundreds of customers |

## Core Capabilities

### Serverless
- Zero maintenance windows
- Automatic scaling
- Instant availability

### Global Tables
- Multi-Region, multi-active database
- Zero RPO (Recovery Point Objective)
- Strong consistency across regions

### Security
- Built-in controls for global banks and government agencies
- SOC 1/2/3, PCI, FINMA, and ISO compliance
- Encryption at rest by default

## Industry Use Cases

| Industry | Use Cases |
|----------|-----------|
| Financial Services | Fraud detection, payment processing, user onboarding |
| Media & Entertainment | Real-time video streaming, content metadata |
| Advertising & Marketing | User profiles, real-time bidding, attribution |
| Retail | Shopping carts, inventory tracking |
| Gaming | Player data, session history, leaderboards |

## Customer Success

- **Disney+:** Ingests billions of daily actions for viewer experience
- **Genesys:** 99.999% availability for AI orchestration
- **Snap Inc.:** 20% reduction in median latency
- **Zoom:** Scaled from 10M to 300M daily participants

## Related Services

- [[aws-rds|RDS]] — Relational database counterpart
- [[aws-vpc|VPC]] — Network isolation for DynamoDB tables
- [[aws-lambda|Lambda]] — Serverless triggers for DynamoDB streams

## References

- [DynamoDB Product Page](https://aws.amazon.com/dynamodb/)
- [DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
