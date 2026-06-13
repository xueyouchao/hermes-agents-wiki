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

## [2026-05-22] ingest | X AI/tech daily digest
- Scraped X.com successfully with valid stored session (0 likes, 0 bookmarks, 7 timeline posts)
- Retained 4 AI/tech timeline posts after relevance screening and 24-hour timestamp filtering
- Created xdailyupdates/2026-05-22/raw/001_Ridark.md
- Created xdailyupdates/2026-05-22/raw/002_Valentin-Ignatev.md
- Created xdailyupdates/2026-05-22/raw/003_leopardracer.md
- Created xdailyupdates/2026-05-22/raw/004_Google-Gemma.md
- Created xdailyupdates/2026-05-22/index.md
- Created queries/2026-05-22-x-daily.md
- Updated index.md with the new query entry
- No GitHub repos extracted; GitNexus not run and Graphify not run

## [2026-05-23] ingest | X AI/tech daily digest
- Scraped X.com successfully with valid stored session (0 likes, 0 bookmarks, 7 timeline posts)
- Retained 3 AI/tech timeline posts after relevance screening, duplicate suppression, and 24-hour timestamp filtering
- Normalized 1 broken-line GitHub URL from text: colbymchenry/codegraph
- Ran GitNexus on colbymchenry/codegraph successfully (4,107 nodes, 9,071 edges, 115 clusters, 300 flows); Graphify not run because it was not installed
- Created xdailyupdates/2026-05-23/raw/001_Rahul.md
- Created xdailyupdates/2026-05-23/raw/002_Sharbel.md
- Created xdailyupdates/2026-05-23/raw/003_Movez.md
- Created xdailyupdates/2026-05-23/index.md
- Created queries/2026-05-23-x-daily.md
- Created entities/knowledge-graph-tools/codegraph.md
- Updated index.md with the new query and entity entries

## [2026-05-24] ingest | X AI/tech daily digest
- Scraped X.com successfully with valid stored session (0 likes, 0 bookmarks, 8 timeline posts)
- Retained 3 AI/tech timeline posts after relevance screening, duplicate suppression, and 24-hour timestamp filtering
- Created xdailyupdates/2026-05-24/raw/001_Ricardo.md
- Created xdailyupdates/2026-05-24/raw/002_Lunar.md
- Created xdailyupdates/2026-05-24/raw/003_MobileVibe.md
- Created xdailyupdates/2026-05-24/index.md
- Created queries/2026-05-24-x-daily.md
- Updated index.md with the new query entry
- No GitHub repos extracted; GitNexus not run and Graphify not run

## [2026-05-25] ingest | X AI/tech daily digest
- Scraped X.com successfully with valid stored session (0 likes, 0 bookmarks, 5 timeline posts)
- Retained 2 AI/tech timeline posts after relevance screening, duplicate suppression, and prior-bundle search
- Created xdailyupdates/2026-05-25/raw/001_Sprytix.md
- Created xdailyupdates/2026-05-25/raw/002_Hyperagent.md
- Created xdailyupdates/2026-05-25/index.md
- Created queries/2026-05-25-x-daily.md
- Updated index.md with the new query entry
- No GitHub repos extracted; GitNexus not run and Graphify not run

## [2026-05-26] ingest | X AI/tech daily digest
- Scraped X.com successfully with valid stored session (0 likes, 0 bookmarks, 7 timeline posts)
- Retained 2 AI/tech timeline posts after relevance screening, duplicate suppression, and 24-hour timestamp filtering
- Created xdailyupdates/2026-05-26/raw/001_Argona.md
- Created xdailyupdates/2026-05-26/raw/002_Larus-Canus.md
- Created xdailyupdates/2026-05-26/index.md
- Created queries/2026-05-26-x-daily.md
- Updated index.md with the new query entry
- No GitHub repos extracted; GitNexus not run and Graphify not run

## [2026-05-27] ingest | X AI/tech daily digest
- Scraped X.com successfully with valid stored session (0 likes, 0 bookmarks, 7 timeline posts)
- Retained 1 AI/tech timeline post after relevance screening and duplicate suppression; 6 posts skipped as recirculated discourse
- Created xdailyupdates/2026-05-27/raw/001_Aiden_Bai.md
- Created entities/react-doctor.md (new entity for millionco/react-doctor deterministic React scanner + agent skill)
- Created xdailyupdates/2026-05-27/index.md
- Created queries/2026-05-27-x-daily.md
- Updated index.md with react-doctor entity and 2026-05-27 query entry
- 1 repo extracted: millionco/react-doctor (normalized from post text — no structured github_links); GitNexus not run, Graphify not run

## [2026-05-28] ingest | X AI/tech daily — Opus 4.8 release, Claude Code security plugin, Devin CLI Opus 4.8

- Scrape: storage_state_valid=true, 0 likes, 0 bookmarks, 10 timeline posts
- Retained 3 AI/tech posts:
  1. @Claude — Claude Opus 4.8 model release (sharper judgment, longer independent work, same price)
  2. @ClaudeDevs — Claude Code security-guidance plugin (identify/fix vulnerabilities during coding, via /plugins)
  3. @nader dabit — Devin CLI now supports Claude Opus 4.8
- Skipped 7 posts: repeated Hyperagent promo, trading-bot promo, deepfake scare, AI-founder listicle, education resource listicle, OSINT tutorial, Elon Musk self-driving car
- No GitHub repos extracted; GitNexus not run, Graphify not run
- Created: xdailyupdates/2026-05-28/raw/001_Claude.md, 002_ClaudeDevs.md, 003_nader_dabit.md
- Created: xdailyupdates/2026-05-28/index.md, queries/2026-05-28-x-daily.md
- Updated: index.md (new query entry), log.md (this entry)

## [2026-05-29] ingest | X AI/tech daily digest for 2026-05-29

- Scrape: 8 timeline, 0 likes, 0 bookmarks; 3 retained after AI/tech filter and recirculation dedup
- Retained: Codex + Ollama local deployment (WorldofAI), Claude Code /ultracode Dynamic Workflows agent swarms (Dan McAteer), Claude for Finance lecture (Rony)
- Skipped: Rohit (workshop recirculation since 05-07/05-11), Quickcast AI (CX marketing), Elon Musk (empty), eternal classic (vague), Bitdefender (security PSA)
- No GitHub repos extracted; GitNexus not run, Graphify not run
- Created: xdailyupdates/2026-05-29/raw/001_WorldofAI.md, 002_Dan_McAteer.md, 003_Rony.md, xdailyupdates/2026-05-29/index.md, queries/2026-05-29-x-daily.md
- Updated: index.md, log.md

## [2026-05-30] ingest | X AI/tech daily digest for 2026-05-30

- Scrape: 8 timeline, 0 likes, 0 bookmarks; 3 retained after AI/tech filter and recirculation dedup
- Retained: Claude Code autonomous workflow (@darkzodchi), DGX Spark local supercomputer (@starmex), reconurge/flow infra mapping (@Tom Dörr)
- Skipped: @Clerk (auth-marketing, no depth), @MobileVibe (recirculated since 05-24), @ₕₐₘₚₜₒₙ (not AI/tech), @Melvyn + @Machina (empty)
- 1 GitHub repo referenced (reconurge/flow) but not found (private/deleted); no valid repos extracted
- GitNexus not run, Graphify not run (no repos extracted)
- Created: xdailyupdates/2026-05-30/raw/001_darkzodchi.md, 002_starmex.md, 003_Tom_Dorr.md, xdailyupdates/2026-05-30/index.md, queries/2026-05-30-x-daily.md
- Updated: index.md (new query entry), log.md (this entry)

## [2026-05-31] ingest | X AI/tech daily — Karpathy Wiki Layer, 5 focused agents

- Scrape: storage_state_valid=true, 0 likes, 0 bookmarks, 6 timeline posts; 2 retained after AI/tech filter and recirculation dedup
- Retained: @Asteri (Karpathy Wiki Layer token-reduction), @darkzodchi (5 focused agents in one afternoon)
- Skipped: @AI_Explorer (follow-listicle), @MobileVibe (recirculated since 05-24), @Harman (recirculated listicle), @Vikas Singh (recirculated Claude course since 05-18)
- No GitHub repos extracted; GitNexus not run, Graphify not run
- Created: xdailyupdates/2026-05-31/raw/001_Asteri.md, 002_darkzodchi.md, xdailyupdates/2026-05-31/index.md, queries/2026-05-31-x-daily.md
- Updated: index.md (new query entry), log.md (this entry)

## [2026-06-01] ingest | X AI/tech daily digest

- Scrape: storage_state_valid=true, 0 likes, 0 bookmarks, 8 timeline posts
- Retained 1 AI/tech timeline post after relevance screening and recirculation dedup (7 skipped: 4 recirculated, 1 not AI/tech, 2 trading/promo)
- Retained: @Stevie3D (archviz Gaussian splat testing from Blender with lichtfeldstudio)
- Skipped: @BuBBliK (RTX Spark, recirculated since 05-30), @MobileVibe (Claude Code on phone, recirculated since 05-24), @shirish (RTX Spark, recirculated since 05-30), @Elon Musk (not AI/tech), @lucacadalora (meta follow-count tweet), @Quant Pilot (trading promo, recirculated), @Himanshu Kumar (unverified income claims)
- No GitHub repos extracted; GitNexus not run and Graphify not run
- Created: xdailyupdates/2026-06-01/raw/001_Stevie3D.md, xdailyupdates/2026-06-01/index.md, queries/2026-06-01-x-daily.md
- Updated: index.md (new query entry), log.md (this entry)

## [2026-06-02] ingest | X AI/tech daily digest

- Scrape: storage_state_valid=true, 0 likes, 0 bookmarks, 7 timeline posts
- Retained 4 AI/tech timeline posts after relevance screening and recirculation dedup (3 skipped: 1 recirculated follow listicle, 1 not AI/tech, 1 not substantive)
- Retained: ElevenLabs Developers (YouTube channel for AI engineers), Sac (vibe-coding live-stream monetization), Peter Dedene (GitHub Copilot post-June 2026 discourse), Gipp (Mac Mini M4 AI cost claim — repeated discourse signal)
- Skipped: AI_Explorer (recirculated follow listicle), Burger King (ad), Black Squad (not substantive AI/tech)
- No GitHub repos extracted; GitNexus not run and Graphify not run
- Created: xdailyupdates/2026-06-02/raw/001_ElevenLabs-Developers.md, 002_Sac.md, 003_Peter-Dedene.md, 004_Gipp.md, xdailyupdates/2026-06-02/index.md, queries/2026-06-02-x-daily.md
- Updated: index.md (new query entry), log.md (this entry)

## [2026-06-03] ingest | X AI/tech daily digest for 2026-06-03

- Scrape: storage_state_valid=true, 0 likes, 0 bookmarks, 6 timeline posts
- Retained 1 AI/tech timeline post after relevance screening and recirculation dedup (5 skipped: 1 recirculated Copilot discourse from 2026-06-02, 1 AI sales promo, 1 AI shopping marketing, 1 Jensen Huang meme, 1 NVDA photonics speculation)
- Retained: @PlayCanvas (SuperSplat WebGPU + LOD upgrade for 24M Gaussians)
- 1 GitHub repo extracted: playcanvas/supersplat; GitNexus run (4,720 nodes, 9,520 edges, 141 clusters, 300 flows)
- Graphify: not installed
- Created: xdailyupdates/2026-06-03/raw/001_PlayCanvas.md, xdailyupdates/2026-06-03/index.md, queries/2026-06-03-x-daily.md, entities/3dgs/supersplat.md
- Updated: index.md (new query + supersplat entity), research/3dgs/3dgs-research.md (added supersplat), log.md (this entry)

## [2026-06-05] ingest | X AI/tech daily digest

- Scrape: storage_state_valid=true, 0 likes, 0 bookmarks, 8 timeline posts
- Retained 1 AI/tech timeline post after relevance screening and recirculation dedup (7 skipped: 2 recirculated follow listicles, 1 recirculated Grok Imagine demo, 1 not AI/tech, 1 promotional hardware call, 1 minor dev showcase, 1 stock promo)
- Retained: @Arun Kurian (AirVis Studio — local Gaussian Splat 3D digital twins from video)
- Skipped: @Soar (travel app), @AI_Explorer (recirculated follow listicle), @Nalin (recirculated follow listicle), @Just a Dude Who Invests (not AI/tech), @Elon Musk (recirculated Grok Imagine demo), @lumos robotics (promotional hardware call), @Craig Taylor (minor dev showcase), @Jealousy 尼卡 (stock promo)
- No GitHub repos extracted; GitNexus not run and Graphify not run
- Created: xdailyupdates/2026-06-05/raw/001_Arun-Kurian.md, xdailyupdates/2026-06-05/index.md, queries/2026-06-05-x-daily.md
- Updated: index.md (new query entry), log.md (this entry)

## [2026-06-06] ingest | X AI/tech daily digest

- Scrape: storage_state_valid=true, 0 likes, 0 bookmarks, 8 timeline posts
- Retained 1 AI/tech timeline post after relevance screening and recirculation dedup (7 skipped: 1 recirculated Clerk marketing from 05-30, 1 empty, 1 not AI/tech, 2 stock/crypto promo, 1 engineering demo, 1 unsubstantiated hype)
- Retained: @Trinity by Ability (open-source production runtime for Claude Code agents - scheduler, audit trail, auto-recovery, multi-user)
- Skipped: @Clerk (recirculated marketing), @Elon Musk (empty), @Serenity (stock promo), @Muhendislik Harikasi (not AI/tech), @Evan Luthra (unsubstantiated hype), @Jealousy (stock promo)
- No GitHub repos extracted (Trinity repo could not be resolved); GitNexus not run and Graphify not run
- Created: xdailyupdates/2026-06-06/raw/001_Trinity-by-Ability.md, xdailyupdates/2026-06-06/index.md, queries/2026-06-06-x-daily.md
- Updated: index.md (new query entry), log.md (this entry)

## [2026-06-07] ingest | X AI/tech daily digest

- Scrape: storage_state_valid=true, 0 likes, 0 bookmarks, 10 timeline posts
- Retained 1 AI/tech timeline post after relevance screening and recirculation dedup (9 skipped: 2 trading/marketing, 1 personal metrics, 1 follow-bait, 2 Claude education recirculation, 1 stock hype, 1 product marketing, 1 recirculated agentic discourse)
- Retained: @Peter Steinberger (agentic loop design: "design loops that prompt your agents")
- Skipped: Mulight 沐光 (Serenity Skills trading marketing), Quant Pilot (recirculated trading promo), Kaichao You (vLLM personal metrics), David Ondrej (follow-bait), Codez (Boris Cherny / Claude Code education, recirculated since 05-18), Wimar.X (NVIDIA/SpaceX stock hype), Oxylabs (product marketing), Anuj (Claude education, recirculated), Rahul (7 Claude agents, recirculated agentic discourse)
- No GitHub repos extracted; GitNexus not run and Graphify not run
- Created: xdailyupdates/2026-06-07/raw/001_Peter-Steinberger.md, xdailyupdates/2026-06-07/index.md, queries/2026-06-07-x-daily.md
- Updated: index.md (new query entry), log.md (this entry)

## [2026-06-08] ingest | X AI/tech daily digest

- Scrape: storage_state_valid=true, 0 likes, 0 bookmarks, 8 timeline posts
- Retained 1 AI/tech timeline post after relevance screening and recirculation dedup (7 skipped: 2 follow-bait, 2 recirculated product marketing, 1 vague, 1 promotional showcase, 1 stock hype)
- Retained: @Sebastian Aaltonen (WASM mini-engine with ECS + AI-generated asset pipeline)
- Skipped: David Ondrej (follow-bait, recirculated from 06-07), Hyperagent (recirculated cloud sandbox promo since 04-23), Aymeric Rabot (vague "2D and 3D in sync"), Hyper3D by Deemos (Rodin Gen-2.5 promotional showcase), Nancy Pelosi Stock Tracker (stock hype), Neo Kim (follow-bait), Oxylabs (recirculated product marketing from 06-07)
- No GitHub repos extracted (Sebastian Aaltonen's engine is proprietary/unreleased); GitNexus not run and Graphify not run
- Created: xdailyupdates/2026-06-08/raw/001_Sebastian-Aaltonen.md, xdailyupdates/2026-06-08/index.md, queries/2026-06-08-x-daily.md
- Updated: index.md (new query entry), log.md (this entry)

## [2026-06-09] ingest | X AI/tech daily digest

- Scrape: storage_state_valid=true, 0 likes, 0 bookmarks, 8 timeline posts
- Retained 2 AI/tech timeline posts after relevance screening and recirculation dedup (6 skipped: 2 follow-bait/listicle, 1 stock trading, 1 recirculated Hyperagent promo, 1 ISP ad, 1 resource listicle without repos)
- Retained: @Claude (Claude Fable 5 Mythos-class model general release), @ClaudeDevs (Claude Code workflow shift under Fable 5)
- Skipped: @AI_Explorer (follow listicle), @Starlink (ISP ad), @华尔街观察 Xtrader (stock trading), @Hyperagent (recirculated cloud sandbox promo since April), @Vaiz (product ad), @Sasha Malysheva (resource listicle without concrete repos)
- No GitHub repos extracted; GitNexus not run and Graphify not run
- Created: xdailyupdates/2026-06-09/raw/001_Claude.md, xdailyupdates/2026-06-09/raw/002_ClaudeDevs.md, xdailyupdates/2026-06-09/index.md, queries/2026-06-09-x-daily.md
- Updated: index.md (new query entry), log.md (this entry)

## [2026-06-10] ingest | X AI/tech daily digest

- Scrape: 8 timeline posts, 0 likes, 0 bookmarks; storage state valid
- Retained 3 AI/tech signals after relevance screening and recirculation dedup
- Skipped 5: 3 stock/financial (Serenity), 1 ISP ad (Starlink), 1 recirculated Hyperagent promo
- No GitHub repos extracted; GitNexus not run and Graphify not run (no repos extracted)
- Created xdailyupdates/2026-06-10/raw/001_Claude.md, 002_Pliny-the-Liberator.md, 003_AI_Explorer.md
- Created xdailyupdates/2026-06-10/index.md
- Created queries/2026-06-10-x-daily.md
- Updated index.md with the new query entry
- Key signals: @Claude highlighted Cursor AI growth (15→700 people, 60% Fortune 500), @Pliny-the-Liberator claimed Fable 5 jailbreak (unverified, continues 06-09 Fable 5 narrative), @AI_Explorer recommended Anthropic ecosystem accounts

## [2026-06-11] ingest | X AI/tech daily digest

- Scrape: 10 timeline posts, 0 likes, 0 bookmarks; storage state valid
- Retained 2 AI/tech signals after relevance screening and recirculation dedup
- Suppressed 3 Fable 5 creative-use posts as recirculated discourse (already captured 06-09/06-10); skipped 5 non-AI posts
- No GitHub repos extracted; GitNexus not run (no repos extracted) and Graphify not run (not installed)
- Created: xdailyupdates/2026-06-11/raw/001_MartinValigursky.md, 002_MrNeRF.md, xdailyupdates/2026-06-11/index.md, queries/2026-06-11-x-daily.md
- Updated: index.md (new query entry), log.md (this entry)
- Key signals: PlayCanvas relighting of captured splat scenes (proxy mesh + dynamic sky/sun/point lights), MrNeRF 1B Gaussians at 60fps/5GB VRAM milestone

## [2026-06-12] ingest | X AI/tech daily digest

- Scrape: 8 timeline posts, 0 likes, 0 bookmarks; storage state valid
- Retained 2 AI/tech signals after relevance screening and recirculation dedup
- Skipped 6: 1 stock/financial (Serenity), 1 ISP ad (Starlink), 1 SuperGrok promo (Grok), 1 unsubstantiated AI prediction (tamrat), 1 recirculated follow listicle (AI_Explorer, identical to 06-10), 1 vague meme (Know Your Computer)
- No GitHub repos extracted; GitNexus not run and Graphify not run (no repos extracted)
- Created: xdailyupdates/2026-06-12/raw/001_levelsio.md, 002_Om-Patel.md, xdailyupdates/2026-06-12/index.md, queries/2026-06-12-x-daily.md
- Updated: index.md (new query entry), log.md (this entry)

## [2026-06-13] ingest | X AI/tech daily digest

- Scrape: 8 timeline posts, 0 likes, 0 bookmarks; storage state valid
- Retained 1 AI/tech signal after relevance screening and recirculation dedup
- Skipped 7: 3 stock/trading (Serenity), 1 ISP ad (Starlink), 1 unsubstantiated clickbait (AI Evolution), 1 meme/joke (Eliot), 1 recirculated Trinity promo (already captured 2026-06-06)
- Retained: @Piotr Pomorski (Fable 5 pirate bay leak claim — continues Fable 5 narrative from 06-09/06-10/06-11)
- No GitHub repos extracted; GitNexus not run and Graphify not run (no repos extracted)
- Created: xdailyupdates/2026-06-13/raw/001_Piotr-Pomorski.md, xdailyupdates/2026-06-13/index.md, queries/2026-06-13-x-daily.md
- Updated: index.md (new query entry), log.md (this entry)
