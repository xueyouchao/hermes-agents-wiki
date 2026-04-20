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

## [2026-04-18] ingest | Polymarket AI Arbitrage Video Analysis
- Analyzed youtube-transcript-api GitHub repository (https://github.com/jdepoix/youtube-transcript-api)
- Tested transcript fetch on video BiqG3it0gY0 (YouTube API blocked from IP - used web extraction fallback)
- Created raw source: raw/youtube-polymarket-ai-arbitrage.md
- Created wiki summary page: polymarket-ai-arbitrage.md
- Key content: AI arbitrage in prediction markets - $313 to $414K case study, five AI arbitrage gaps, CNC lathe parallel, rolling disruption model
- Added to index.md under "FinTech & AI" section
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

## [2026-04-17] update | Restore whole-wiki index and fold in NVIDIA research
- Restored the root index.md as the top-level catalog for the full Hermes Agents wiki
- Moved NVIDIA-specific research notes into research/nvidia/
- Moved NVIDIA concept and entity pages into concepts/nvidia/ and entities/nvidia/
- Added [[nvidia-research]] as the renamed hub for NVIDIA material
- Updated SCHEMA.md so NVIDIA applied AI research is part of the vault domain

## [2026-04-17] update | Create AWS and Temporal sub-wikis
- Moved AWS entity pages into entities/aws/
- Moved Temporal entity pages into entities/temporal/
- Moved Temporal concept pages into concepts/temporal/
- Added [[aws-research]] and [[temporal-research]] as sub-wiki hub pages
- Kept the root index.md as the single top-level catalog for the whole vault

## [2026-04-17] update | Create Karpathy repository sub-wiki
- Moved Karpathy repository pages into entities/karpathy/
- Moved the Karpathy overview page into concepts/karpathy/
- Added [[karpathy-research]] as the Karpathy sub-wiki hub
- Recorded the sub-wiki layout in SCHEMA.md

## [2026-04-17] compile | Normalize links, sources, and topic structure
- Added missing concept pages for Temporal recovery terms, NVIDIA RTX deployment topics, and 3D graphics foundations
- Rewrote malformed or duplicate pages including the stray Karpathy duplicate and the broken fVDB overview
- Replaced placeholder source paths with real URLs where the vault already depended on external source material
- Rebuilt index.md as a topic-first catalog that lists the current pages once under domain groupings
- Reduced unresolved wikilinks to schema examples only, then updated SCHEMA.md wording to remove those false positives

## [2026-04-20] reorganize | AI/LLM Repositories sub-wiki
- Created research/ai-repos/ai-repos-research.md as topic hub
- Created entities/repos/ folder
- Moved 56 AI/LLM repository files from wiki root to entities/repos/
- Organized repos into categories: LLM Inference, Frameworks, Agents, Vision, Training, RAG, Research, Other Tools
- Added [[ai-repos-research]] to Topic Hubs in index.md
- Added full "AI/LLM Repositories" section to index.md with categorized entries

## [2026-04-20] reorganize | 3DGS sub-wiki
- Created research/3dgs/3dgs-research.md as topic hub
- Created concepts/3dgs/ folder and moved: 3d-gaussian-splatting.md, nerf.md, point-cloud.md, view-synthesis.md
- Created entities/3dgs/ folder and moved: awesome-3dgs.md, gaussian-impl.md, splat-webgl.md
- Added [[3dgs-research]] to Topic Hubs in index.md
- Updated 3D Graphics section with sub-sections for Concepts and Implementations
