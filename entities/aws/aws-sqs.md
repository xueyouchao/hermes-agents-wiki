---
title: Amazon SQS
created: 2026-04-16
updated: 2026-04-16
type: entity
tags: [aws, cloud, messaging, queue, sqs]
sources: [https://aws.amazon.com/sqs/]
---

# Amazon Simple Queue Service (SQS)

Amazon SQS is a fully managed message queuing service for microservices, distributed systems, and serverless applications. It decouples and scales components by sending, storing, and receiving messages at any volume.

## Core Benefits

- **No Overhead:** No upfront costs; AWS manages infrastructure
- **Reliability:** Delivers large volumes without message loss
- **Security:** Secure transmission, KMS integration
- **Cost-Effective:** Elastic scaling without capacity planning

## Queue Types

| Type | Description |
|------|-------------|
| Standard | Maximum throughput, best-effort ordering |
| FIFO | Exact order, message deduplication |

## Primary Use Cases

- **Application Reliability:** Decouple microservices, hold messages if component fails
- **Event-Driven Processing:** Separate frontend/backend (e.g., banking: immediate response, background payment processing)
- **Workload Management:** Buffer for Auto Scaling groups
- **Message Ordering:** Tasks requiring sequence preservation

## Customer Implementations

- **Change Healthcare:** Millions of daily confidential transactions
- **NASA:** Decouple image pipeline jobs
- **Capital One:** Modernize retail message queuing
- **BMW:** Sensor data for dynamic map updates

## Related Services

- [[aws-sns|SNS]] — Often paired for pub/sub patterns
- [[aws-lambda|Lambda]] — Event source for SQS queues
- [[aws-ec2|EC2]] — Worker instances processing queue messages
- [[aws-sqs|SQS]] -> [[aws-sqs|FIFO]] — Ordered processing requirements

## References

- [SQS Product Page](https://aws.amazon.com/sqs/)
- [SQS Features](https://aws.amazon.com/sqs/features/)
