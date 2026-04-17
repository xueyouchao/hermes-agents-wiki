---
title: Amazon SNS
created: 2026-04-16
updated: 2026-04-16
type: entity
tags: [aws, cloud, messaging, pub-sub, sns]
sources: [https://aws.amazon.com/sns/]
---

Amazon Simple Notification Service (SNS) is a fully managed Pub/Sub service for both system-to-system (A2A) and system-to-person (A2P) messaging.

## Core Messaging Models

### Application-to-Application (A2A)

- Integrates and decouples distributed applications
- Captures events from **60+ AWS services** (analytics, compute, containers, databases, IoT, ML, security, storage)
- Supports serverless architectures with messaging fanout patterns

### Application-to-Person (A2P)

- Direct customer communication
- **SMS:** Worldwide delivery to 240+ countries
- **Mobile Push:** Application notifications
- **Email:** Direct email delivery
- **SMS Identities:** Sender ID, long/short codes, Toll-Free Numbers, 10DLC

## Key Features

| Feature | Description |
|---------|-------------|
| FIFO Messaging | Strictly ordered message delivery |
| Durability | Message archiving, replay, retries, DLQs |
| Optimization | Filtering, batching, deduplication |
| Security | KMS encryption, PrivateLink, resource policies |

## Customer Use Cases

- **PlayOn! Sports:** Serverless fanout architectures
- **Change Healthcare:** Millions of daily confidential transactions
- **FC Barcelona:** All web platform notifications
- **NASA:** Image and Video Library content management

## Related Services

- [[aws-sqs|SQS]] — Often used with SNS for pub/sub
- [[aws-lambda|Lambda]] — Event-driven triggers
- [[aws-sns|SNS]] -> [[aws-sqs|SQS]] — Fanout patterns

## References

- [SNS Product Page](https://aws.amazon.com/sns/)
- [SNS Documentation](https://docs.aws.amazon.com/sns/)
