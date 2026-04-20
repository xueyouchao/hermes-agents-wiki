# Wiki Index


> Master catalog for the Hermes Agents wiki.
> The root index tracks topic hubs first, then supporting pages grouped by domain.
> Last updated: 2026-04-17

## Topic Hubs

- [[aws-research]] - AWS infrastructure and AI platform sub-wiki
- [[karpathy-research]] - Andrej Karpathy and repository sub-wiki
- [[temporal-research]] - Temporal platform and durable execution sub-wiki
- [[nvidia-research]] - NVIDIA RTX AI, ACE, and fVDB sub-wiki
- [[ai-repos-research]] - AI/LLM repositories (56 repos with 15k+ stars)
- [[3dgs-research]] - 3D Gaussian Splatting sub-wiki

## Karpathy

- [[andrej-karpathy]] - Researcher and educator behind the Karpathy repository set
- [[karpathy-repos]] - Overview and learning path across the repository collection
- [[nanogpt]] - GPT pretraining and fine-tuning reference repo
- [[llm-c]] - Minimal C/CUDA LLM training stack
- [[mingpt]] - Minimal PyTorch GPT implementation
- [[minbpe]] - Minimal byte-pair encoding implementation
- [[micrograd]] - Tiny autograd engine
- [[char-rnn]] - Character-level recurrent model
- [[nanochat]] - Local low-cost chat assistant project

## Temporal

- [[temporal]] - Open-source durable execution platform
- [[temporal-cloud]] - Managed Temporal offering
- [[durable-execution]] - State persistence and recovery model
- [[workflow]] - Deterministic orchestration code
- [[activity]] - Retryable side-effecting work
- [[replay]] - Workflow state reconstruction from persisted history
- [[compensation]] - Recovery pattern for partially completed work
- [[cluster]] - Operational unit behind self-hosted Temporal
- [[persistence]] - Storage layer for workflow histories
- [[self-hosted-temporal]] - Self-managed deployment model

## AWS

- [[aws-ec2]] - Elastic compute instances
- [[aws-lambda]] - Serverless compute
- [[aws-s3]] - Object storage platform
- [[aws-dynamodb]] - Managed NoSQL database
- [[aws-rds]] - Managed relational databases
- [[aws-vpc]] - Private networking foundation
- [[aws-cloudfront]] - CDN and edge delivery service
- [[aws-iam]] - Identity and access management
- [[aws-route53]] - DNS and traffic routing
- [[aws-sns]] - Pub/sub messaging
- [[aws-sqs]] - Queueing service
- [[aws-ecs]] - Managed container orchestration
- [[aws-eks]] - Managed Kubernetes
- [[amazon-sagemaker]] - Managed ML platform
- [[aws-bedrock]] - Managed generative AI and AgentCore platform

## NVIDIA

- [[nvidia-ai-apps-rtx-pcs-overview]] - Research overview of the RTX AI app ecosystem
- [[nvidia-ai-apps-rtx-pcs-technical-details]] - Detailed implementation and optimization notes
- [[nvidia-ai-apps-for-rtx-pcs-sdk-and-models]] - Entity page for the RTX AI apps ecosystem
- [[nvidia-ai-apps-for-rtx-pcs-technical-details]] - Entity page for implementation details
- [[nvidia-ace-for-games]] - ACE for Games platform page
- [[audio2face-3d-sdk]] - Audio-driven facial animation for game characters
- [[neomo-nano-for-game-ai]] - Small NVIDIA models for game AI
- [[npc-dynamic-behavior-ace]] - Dynamic NPC behavior patterns enabled by ACE
- [[qwen3-on-device-ai]] - On-device multilingual game AI model notes
- [[rendering-pipeline-integration-ace]] - ACE integration inside rendering/gameplay pipelines
- [[cuda-programming]] - GPU programming foundation beneath local RTX AI tooling
- [[tensorrt-optimization]] - Inference optimization workflow for RTX deployment
- [[windows-ml-integration]] - Windows-native model deployment path
- [[llm-deployment-on-rtx-pcs]] - Practical local LLM deployment on RTX hardware
- [[fvdb-overview]] - fVDB overview and positioning
- [[fvdb-architecture]] - fVDB architecture and components
- [[fvdb-fundamentals]] - Core fVDB principles
- [[fvdb-openvdb-integration]] - fVDB relationship to OpenVDB and NanoVDB
- [[fvdb-pytorch-integration]] - PyTorch integration patterns for fVDB
- [[fvdb-microservices]] - fVDB NIM and microservice packaging notes
- [[fvdb-performance]] - fVDB performance and scaling notes
- [[documentation-resources]] - NVIDIA source and reference roundup

## 3D Graphics

> Topic Hub: [[3dgs-research]] - 3D Gaussian Splatting sub-wiki

### Concepts

- [[3d-gaussian-splatting]] - Real-time neural rendering technique using optimized Gaussians
- [[nerf]] - Precursor neural radiance field representation
- [[view-synthesis]] - Task of generating novel viewpoints
- [[point-cloud]] - Basic 3D geometric representation

### Implementations

- [[gaussian-impl]] - Reference implementation of the original 3DGS method
- [[splat-webgl]] - Browser viewer for splat scenes
- [[awesome-3dgs]] - Curated ecosystem and paper list

## Tools And Comparisons

- [[autoresearch]] - Autonomous agent research repository
- [[graphify]] - Knowledge graph tooling entity
- [[neo4j]] - Graph database entity
- [[code2vec]] - Code representation learning entity
- [[sourcegraph-public-snapshot]] - Sourcegraph public snapshot entity
- [[knowledge-graph-tools-llm-retrieval]] - Comparison of Graphify, Sourcegraph, Neo4j, and Code2Vec

## Robotics & Embodied AI

> Topic Hub: [[robotics-vla-models]] - Open-source VLA models and ecosystem

### Four Factions

- [[four-factions]] - Analysis of open-source robotics competition
- [[vla-model]] - Vision-Language-Action fundamentals

### Key Companies & Models

- [[physical-intelligence]] - PI (π₀, π₀.5), $5.6B valuation
- [[open-vla]] - Stanford/Berkeley 7B model, beat Google's 55B RT-2-X
- [[octo]] - Universal robot policy model
- [[nvidia-gr00t]] - NVIDIA's full-stack robot foundation model
- [[open-x-embodiment]] - The 1M+ trajectory robot data commons
- [[xiaomi-robotics]] - Xiaomi-Robotics-0.47 with MoT architecture
- [[ant-group-lingbot]] - Ant Group's cross-form VLA

### Key Researchers

- [[chelsea-finn]] - Stanford professor, PI co-founder
- [[sergey-levine]] - Berkeley professor, PI co-founder, RL pioneer

### Tools & Infrastructure

- [[lerobot]] - Hugging Face robot training framework
- [[genesis-robotics]] - CMU-led simulation platform

## AI/LLM Repositories

> 56 AI/LLM repositories with 15k+ stars, organized by category

### LLM Inference & Deployment

- [[llama.cpp]] - C++ GPT implementation for efficient CPU inference
- [[ollama]] - Run Llama, Mistral, and other models locally
- [[vllm]] - High-throughput LLM serving engine
- [[gpt4all]] - Local LLM inference ecosystem
- [[gpt4free]] - Free GPT-4 API alternatives
- [[transformers.js]] - Run Hugging Face transformers in browser/Node
- [[open-webui]] - Web UI for self-hosted LLMs
- [[chatbot-ui]] - ChatGPT-style UI for LLMs
- [[chatbox]] - AI desktop client

### LLM Frameworks & Libraries

- [[langchain]] - Framework for building LLM applications
- [[langchain-chatchat]] - LangChain-based chat interface
- [[haystack]] - Open-source NLP framework
- [[dify]] - LLMOps platform for building AI apps
- [[flowise]] - Low-code LLM flow builder
- [[llamafactory]] - Unified framework for LLM fine-tuning
- [[peft]] - Parameter-efficient fine-tuning methods
- [[trl]] - Transformer Reinforcement Learning
- [[transformers]] - Hugging Face transformers library
- [[agentscope]] - Multi-agent simulation framework
- [[kotaemon]] - RAG-based chat UI for documents

### AI Agents

- [[auto-gpt]] - Autonomous GPT-4 agent
- [[open-hands]] - AI coding agent platform
- [[browser-use]] - Browser automation with AI agents

### Vision & Multi-modal

- [[llava]] - Large Language and Vision Assistant
- [[codeformer]] - Face restoration tool
- [[paddleocr]] - OCR toolkit
- [[swin-transformer]] - Swin Transformer vision backbone
- [[vit-pytorch]] - Vision Transformer in PyTorch
- [[pytorch-image-models]] - Image models collection
- [[sentence-transformers]] - Sentence embedding models

### Training & Education

- [[megatron-lm]] - Large-scale transformer training
- [[min-gpt]] - Minimal GPT implementation
- [[llms-from-scratch]] - Build LLM from scratch book
- [[annotated-deep-learning-paper-implementations]] - Paper implementations
- [[ml-engineering]] - ML engineering resources
- [[llm-course]] - LLM learning course

### RAG & Knowledge Bases

- [[quivr]] - RAG-as-a-service
- [[ragflow]] - RAG engine with flow control
- [[docsgpt]] - AI-powered documentation assistant

### Web Scraping & Data

- [[firecrawl]] - AI web scraping
- [[repomix]] - Repository to LLM-friendly format

### Research & Papers

- [[cvpr2026-papers-with-code]] - CVPR papers with code
- [[funnlp]] - NLP resources collection

### Other Tools

- [[aionui]] - AI assistant UI
- [[astrbot]] - Bot framework
- [[fastchat]] - ChatArena platform
- [[prompts-chat]] - Prompt collection
- [[python-telegram-bot]] - Telegram bot library
- [[wechaty]] - WeChat bot SDK
- [[sim]] - Simple integration for models
- [[awesome-llm-apps]] - Curated LLM apps list
- [[everything-claude-code]] - Claude Code resources
- [[hermes-agent]] - Hermes Agent documentation
- [[llm-app]] - LLM application collection
- [[xiaozhi-esp32]] - ESP32 voice assistant

## Meta

- [[OBSIDIAN-SETUP]] - Vault usage notes for Obsidian
- [[SCHEMA]] - Domain conventions and page rules
- [[SKILL]] - Legacy local research-generation skill notes
- [[log]] - Append-only change log for compile and ingest work

## FinTech & AI

- [[polymarket-ai-arbitrage]] - Analysis of AI arbitrage in prediction markets by Nate B. Jones
