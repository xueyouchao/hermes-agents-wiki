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

## [2026-04-22] ingest | InteriorGS Dataset
- Analyzed HuggingFace dataset: spatialverse/InteriorGS
- Created entity page: entities/3dgs/interiorgs.md
- Created raw source: raw/articles/spatialverse-interiorgs.md
- Key content: 1,000 indoor 3DGS scenes, 5M+ images, 554K+ object instances, 755 categories
- Updated 3dgs-research.md to include InteriorGS in implementations
- Updated index.md with new entity entry

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

## [2026-04-20] ingest | Agent Platform Landscape (YouTube)
- Extracted YouTube video content via Firecrawl: https://www.youtube.com/watch?v=YJCe8hvZrxs
- Created raw source: raw/transcripts/agent-platform-landscape-2026.md
- Created entity pages:
  - entities/ai-platforms/claude-managed-agents.md
  - entities/ai-platforms/deep-agents-deploy.md
  - entities/ai-platforms/openai-agents-sdk.md
- Created concept pages:
  - concepts/ai-agents/agent-platform-landscape.md
  - concepts/ai-agents/brain-vs-hands-architecture.md
- Key content: 5-tier build-to-buy spectrum for agent platforms, Claude Managed Agents vs LangChain Deep Agents vs OpenAI Agents SDK
- Updated index.md with new sections: Managed Agent Platforms (2026) and Agent Concepts
- Related: [[langchain]], [[aws-bedrock]], [[auto-gpt]], [[open-hands]]

## [2026-04-20] reorganize | 3DGS sub-wiki
- Created research/3dgs/3dgs-research.md as topic hub
- Created concepts/3dgs/ folder and moved: 3d-gaussian-splatting.md, nerf.md, point-cloud.md, view-synthesis.md
- Created entities/3dgs/ folder and moved: awesome-3dgs.md, gaussian-impl.md, splat-webgl.md
- Added [[3dgs-research]] to Topic Hubs in index.md
- Updated 3D Graphics section with sub-sections for Concepts and Implementations


## [2026-04-22] reorganize | Knowledge graph tools and autoresearch
- Created entities/knowledge-graph-tools/ folder
- Moved code2vec.md, graphify.md, neo4j.md, sourcegraph-public-snapshot.md into entities/knowledge-graph-tools/
- Moved autoresearch.md into entities/karpathy/ (properly placing it in the karpathy sub-wiki)
- Updated index.md with new section and correct wikilinks for all moved files
- Updated comparisons/knowledge-graph-tools-llm-retrieval.md with correct wikilinks
- Updated log.md Last updated date

## [2026-05-10] ingest | X AI/tech daily digest
- Scraped X.com successfully with valid stored session (0 likes, 0 bookmarks, 6 timeline posts)
- Retained 3 AI/tech timeline posts after 24-hour filtering and relevance screening
- Created xdailyupdates/2026-05-10/raw/001_Dilum-Sanjaya.md
- Created xdailyupdates/2026-05-10/raw/002_Movez.md
- Created xdailyupdates/2026-05-10/raw/003_leopardracer.md
- Created xdailyupdates/2026-05-10/index.md
- Created queries/2026-05-10-x-daily.md
- Updated index.md with the new query entry
- No GitHub repos extracted; GitNexus not run and Graphify unavailable

## [2026-05-10] update | GitNexus manageable batch
- Sequential GitNexus pass over a manageable 10-repo batch chosen to avoid huge CPU spikes while replacing stale failure markers
- Updated raw/repomix.md and entities/repos/repomix.md (791 files, 11724 symbols, 13520 edges, 111 clusters, 179 flows)
- Updated raw/python-telegram-bot.md and entities/repos/python-telegram-bot.md (1201 files, 15915 symbols, 28186 edges, 428 clusters, 138 flows)
- Updated raw/minGPT.md and entities/repos/minGPT.md (15 files, 274 symbols, 380 edges, 17 clusters, 3 flows)
- Updated raw/agentscope.md and entities/repos/agentscope.md (564 files, 9417 symbols, 16292 edges, 500 clusters, 227 flows)
- Updated raw/peft.md and entities/repos/peft.md (727 files, 16377 symbols, 24327 edges, 421 clusters, 128 flows)
- Updated raw/sentence-transformers.md and entities/repos/sentence-transformers.md (616 files, 12713 symbols, 18274 edges, 281 clusters, 101 flows)
- Updated raw/trl.md and entities/repos/trl.md (484 files, 12708 symbols, 17579 edges, 205 clusters, 135 flows)
- Updated raw/CodeFormer.md and entities/repos/CodeFormer.md (111 files, 2795 symbols, 4541 edges, 140 clusters, 122 flows)
- Updated raw/vit-pytorch.md and entities/repos/vit-pytorch.md (79 files, 3193 symbols, 5060 edges, 254 clusters, 50 flows)
- Updated raw/transformers.js.md and entities/repos/transformers.js.md (669 files, 7292 symbols, 15611 edges, 199 clusters, 300 flows)

## [2026-05-10] update | Import GitNexus repo wikis into raw knowledgebase sources
- Copied GitNexus-generated wiki page sets into raw/gitnexus/karpathy/micrograd/, raw/gitnexus/karpathy/char-rnn/, raw/gitnexus/karpathy/minbpe/, and raw/gitnexus/3dgs/splat-webgl/
- Updated entities/karpathy/micrograd.md to reference imported GitNexus wiki pages
- Updated entities/karpathy/char-rnn.md to reference imported GitNexus wiki pages
- Updated entities/karpathy/minbpe.md to reference imported GitNexus wiki pages
- Updated entities/3dgs/splat-webgl.md to reference imported GitNexus wiki pages

## [2026-05-11] ingest | X AI/tech daily digest
- Scraped X.com successfully with valid stored session (0 likes, 0 bookmarks, 6 timeline posts)
- Retained 5 AI/tech timeline posts after 24-hour filtering and relevance screening
- Created xdailyupdates/2026-05-11/raw/001_Mayank-Agarwal.md
- Created xdailyupdates/2026-05-11/raw/002_Marry-Evan.md
- Created xdailyupdates/2026-05-11/raw/003_gus.md
- Created xdailyupdates/2026-05-11/raw/004_ZoAina-AI.md
- Created xdailyupdates/2026-05-11/raw/005_AilaunchX.md
- Created xdailyupdates/2026-05-11/index.md
- Created queries/2026-05-11-x-daily.md
- Updated index.md with the new query entry
- No GitHub repos extracted; GitNexus not run and Graphify not run

## [2026-05-11] update | Import remaining GitNexus repo wikis into raw knowledgebase sources
- Generated GitNexus wiki bundles sequentially with provider=openai model=glm-5.1:cloud base_url=http://127.0.0.1:11434/v1
- Copied GitNexus-generated wiki page sets into raw/gitnexus/karpathy/mingpt/, raw/gitnexus/karpathy/nanogpt/, raw/gitnexus/karpathy/llm-c/, raw/gitnexus/3dgs/gaussian-impl/, and raw/gitnexus/3dgs/awesome-3dgs/
- Updated entities/karpathy/mingpt.md to reference imported GitNexus wiki pages
- Updated entities/karpathy/nanogpt.md to reference imported GitNexus wiki pages
- Updated entities/karpathy/llm-c.md to reference imported GitNexus wiki pages
- Updated entities/3dgs/gaussian-impl.md to reference imported GitNexus wiki pages
- Updated entities/3dgs/awesome-3dgs.md to reference imported GitNexus wiki pages
- GitNexus analyze emitted non-fatal scope-extraction warnings for awesome-3D-gaussian-splatting src/__init__.py and src/components/__init__.py, but wiki generation completed successfully

## [2026-05-12] ingest | X AI/tech daily digest
- Scraped X.com successfully with valid stored session (0 likes, 0 bookmarks, 7 timeline posts)
- Retained 4 AI/tech timeline posts after relevance screening
- Created xdailyupdates/2026-05-12/raw/001_Marry-Evan.md
- Created xdailyupdates/2026-05-12/raw/002_AilaunchX.md
- Created xdailyupdates/2026-05-12/raw/003_Matt-Pocock.md
- Created xdailyupdates/2026-05-12/raw/004_Kshitij-Mishra-AI-Tech.md
- Created xdailyupdates/2026-05-12/index.md
- Created queries/2026-05-12-x-daily.md
- Updated index.md with the new query entry
- Inferred 4 GitHub repos from broken-format post text and cloned/analyzed them with basic README triage: The-Swarm-Corporation/AutoHedge, HKUDS/Vibe-Trading, AgriciDaniel/claude-ads, nowork-studio/toprank
- GitNexus available but not run; Graphify not installed

## [2026-05-13] ingest | X AI/tech daily digest
- Scraped X.com successfully with valid stored session (0 likes, 0 bookmarks, 5 timeline posts)
- Retained 3 AI/tech timeline posts after relevance screening
- Created xdailyupdates/2026-05-13/raw/001_Anuj.md
- Created xdailyupdates/2026-05-13/raw/002_Cole-Whitman.md
- Created xdailyupdates/2026-05-13/raw/003_ZAYVEN-KNOX.md
- Created xdailyupdates/2026-05-13/index.md
- Created queries/2026-05-13-x-daily.md
- Updated index.md with the new query entry
- No GitHub repos extracted; GitNexus not run and Graphify not run

## [2026-05-14] ingest | X AI/tech daily digest
- Scraped X.com successfully with valid stored session (0 likes, 0 bookmarks, 7 timeline posts)
- Retained 4 AI/tech timeline posts after relevance screening
- Created xdailyupdates/2026-05-14/raw/001_Ram.md
- Created xdailyupdates/2026-05-14/raw/002_Hailey.md
- Created xdailyupdates/2026-05-14/raw/003_Ronin.md
- Created xdailyupdates/2026-05-14/raw/004_VALIX.md
- Created xdailyupdates/2026-05-14/index.md
- Created queries/2026-05-14-x-daily.md
- Updated index.md with the new query entry
- No canonical GitHub repos extracted; GitNexus not run and Graphify not run

## [2026-05-18] ingest | X AI/tech daily digest
- Scraped X.com successfully with valid stored session (0 likes, 0 bookmarks, 7 timeline posts)
- Retained 7 AI/tech timeline posts after relevance screening
- Created xdailyupdates/2026-05-18/raw/001_VALIX.md
- Created xdailyupdates/2026-05-18/raw/002_Vikas-Singh.md
- Created xdailyupdates/2026-05-18/raw/003_Viktor-Oddy.md
- Created xdailyupdates/2026-05-18/raw/004_Cole-Whitman.md
- Created xdailyupdates/2026-05-18/raw/005_Suryansh-Tiwari.md
- Created xdailyupdates/2026-05-18/raw/006_Anuj.md
- Created xdailyupdates/2026-05-18/raw/007_Rohit-Ghumare.md
- Created xdailyupdates/2026-05-18/index.md
- Created queries/2026-05-18-x-daily.md
- Updated index.md with the new query entry
- No canonical GitHub repos extracted; GitNexus not run and Graphify not run
## [2026-05-18] update | X AI/tech daily digest same-day addendum
- Scraped X.com successfully with valid stored session (0 likes, 0 bookmarks, 6 timeline posts)
- Added 1 newly observed relevant Claude Code education post to the existing 2026-05-18 digest: Khairallah AL-Awady on an Anthropic/Boris Cherny Claude Code workshop
- Created xdailyupdates/2026-05-18/raw/008_Khairallah-AL-Awady.md
- Updated xdailyupdates/2026-05-18/index.md
- Updated queries/2026-05-18-x-daily.md
- No GitHub repos extracted; GitNexus not run and Graphify not run


## [2026-05-18] ingest | X daily backfill for missed 2026-05-16 and 2026-05-17 dates
- Recovered authenticated home-timeline posts for missed cron dates after the daily X ingest was blocked by a prompt-safety filter.
- Created `queries/2026-05-16-x-daily.md` and `queries/2026-05-17-x-daily.md`.
- Created `xdailyupdates/2026-05-16/` and `xdailyupdates/2026-05-17/` raw backfill bundles.
- Recovery limitation: likes/bookmarks returned zero tweet articles, and deep home-timeline scrolling did not recover 2026-05-15 posts.

## [2026-05-18] update | X AI/tech daily digest same-day addendum
- Scraped X.com successfully with valid stored session (0 likes, 0 bookmarks, 8 timeline posts)
- Added 4 newly observed relevant AI/tech posts to the existing 2026-05-18 digest: David max on a Polymarket bot anecdote, ardizor on Claude money-printer/prompt claims, Anatoli Kopadze on Claude Code prompting patterns, and Tabassum Parveen on an LLM-building lecture
- Created xdailyupdates/2026-05-18/raw/009_David-max.md
- Created xdailyupdates/2026-05-18/raw/010_ardizor.md
- Created xdailyupdates/2026-05-18/raw/011_Anatoli-Kopadze.md
- Created xdailyupdates/2026-05-18/raw/012_Tabassum-Parveen.md
- Updated xdailyupdates/2026-05-18/index.md
- Updated queries/2026-05-18-x-daily.md
- No GitHub repos extracted; GitNexus not run and Graphify not run

## [2026-05-19] ingest | X AI/tech daily digest
- Scraped X.com successfully with valid stored session (0 likes, 0 bookmarks, 7 timeline posts)
- Retained 6 AI/tech timeline posts after relevance screening
- Created xdailyupdates/2026-05-19/raw/001_AilaunchX.md
- Created xdailyupdates/2026-05-19/raw/002_Santiago.md
- Created xdailyupdates/2026-05-19/raw/003_Neo-Kim.md
- Created xdailyupdates/2026-05-19/raw/004_Open-Design.md
- Created xdailyupdates/2026-05-19/raw/005_Noisy.md
- Created xdailyupdates/2026-05-19/raw/006_Cortex.md
- Created xdailyupdates/2026-05-19/index.md
- Created queries/2026-05-19-x-daily.md
- Updated index.md with the new query entry
- No GitHub repos extracted; GitNexus not run and Graphify not run

## [2026-05-20] ingest | X AI/tech daily digest
- Scraped X.com successfully with valid stored session (0 likes, 0 bookmarks, 8 timeline posts)
- Retained 7 AI/tech timeline posts after relevance screening
- Created xdailyupdates/2026-05-20/raw/001_ZAYVEN-KNOX.md
- Created xdailyupdates/2026-05-20/raw/002_NOVA.md
- Created xdailyupdates/2026-05-20/raw/003_Anuj.md
- Created xdailyupdates/2026-05-20/raw/004_Anubhav.md
- Created xdailyupdates/2026-05-20/raw/005_Tabassum-Parveen.md
- Created xdailyupdates/2026-05-20/raw/006_Paul-Sims.md
- Created xdailyupdates/2026-05-20/raw/007_Nous-Research.md
- Created xdailyupdates/2026-05-20/index.md
- Created queries/2026-05-20-x-daily.md
- Updated index.md with the new query entry
- No GitHub repos extracted; GitNexus not run and Graphify not run
