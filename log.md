# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.

## [2026-04-16] create | Wiki initialized
- Domain: Temporal and durable execution ecosystem
- Structure created with SCHEMA.md, index.md, log.md
- Raw source directories: articles/, papers/, transcripts/, assets/
- Created initial wiki pages: temporal, temporal-cloud, durable-execution, workflow, activity, self-hosted-temporal
- Added OBSIDIAN-SETUP.md for vault configuration

## [2026-04-16] ingest | AWS Services (15 new entities)
- Created entity pages for 15 popular AWS services:
  - aws-ec2.md, aws-lambda.md, aws-s3.md, aws-dynamodb.md
  - aws-rds.md, aws-vpc.md, aws-cloudfront.md, aws-iam.md
  - aws-route53.md, aws-sns.md, aws-sqs.md
  - aws-ecs.md, aws-eks.md, amazon-sagemaker.md
- Updated SCHEMA.md tag taxonomy with aws service tags
- Updated index.md with all new pages (now 31 total)
- Sources: AWS official product pages (2026)

## [2026-04-16] ingest | Amazon Bedrock (AgentCore)
- Created entity page: aws-bedrock.md
- Documented AgentCore platform: Runtime, Gateway, Memory, Identity, Specialized Tools
- Included capabilities: Model Distillation (500% faster, 75% cheaper), Prompt Routing (30% cost reduction), Guardrails (88% harmful content blocked)
- Added customer success: Robinhood (80% cost reduction), Epsilon (months to weeks)
- Related: [[amazon-sagemaker|SageMaker]], [[aws-lambda|Lambda]], [[aws-iam|IAM]]
## [2026-04-17] compare | Knowledge Graph Tools for LLM Retrieval
- Created comparison page: comparisons/knowledge-graph-tools-llm-retrieval.md
- Updated index.md with new comparison entry
- Added total page count update to index.md
