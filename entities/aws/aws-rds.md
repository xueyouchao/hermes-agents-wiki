---  
title: Amazon RDS
created: 2026-04-16
updated: 2026-04-16
type: entity
tags: [aws, cloud, database, relational, rds]
sources: [https://aws.amazon.com/rds/]
---  
# Amazon Relational Database Service (RDS)

Amazon RDS is a fully managed relational database service that simplifies setup, operation, and scaling of databases in the cloud. It optimizes total cost of ownership (TCO) by automating administrative tasks.

## Core Value Proposition

- **Automated Management:** Provisioning, configuration, patching, and backups handled by AWS
- **Scalability:** Rapid scaling to meet demand
- **Performance:** Graviton3-based instances, optimized reads/writes
- **High Availability:** Multi-AZ deployments

## Supported Database Engines

| Category | Engines |
|----------|---------|
| Open Source | MySQL, PostgreSQL, MariaDB |
| Commercial | Oracle, SQL Server, Db2 |
| Cloud-Native | Amazon Aurora (MySQL/PostgreSQL compatible) |

## Key Innovations

### Amazon Aurora
> "Unparalleled high performance and availability at global scale with full MySQL and PostgreSQL compatibility at 1/10th the cost of commercial databases."

- **Aurora Serverless:** Scales to hundreds of thousands of transactions in seconds
- **Aurora I/O-Optimized:** Price predictability for I/O-intensive applications
- **Zero-ETL Integration:** Near real-time analytics to Amazon Redshift

### Generative AI Support
Using Aurora Optimized Reads with `pgvector_hnsw` achieves **20x improved queries per second** compared to `pgvector_IVFFLAT`.

## Use Cases

1. **Web and Mobile Apps:** High throughput with pay-per-use pricing
2. **Managed Migration:** Moving from self-managed databases
3. **Legacy Modernization:** Migrating from commercial engines (up to 90% cost reduction)

## Customer Impact

- **Intuit Mint:** 25% database cost reduction
- **Cathay Pacific:** 20% performance boost from Oracle to RDS
- **Samsung:** Migrated 1.1 billion users from Oracle to Aurora

## Related Services

- [[aws-dynamodb|DynamoDB]] — NoSQL alternative
- [[aws-ec2|EC2]] — Self-managed database option
- [[aws-s3|S3]] — Data lake integration for Aurora

## References

- [RDS Product Page](https://aws.amazon.com/rds/)
- [RDS Documentation](https://docs.aws.amazon.com/AmazonRDS/)
