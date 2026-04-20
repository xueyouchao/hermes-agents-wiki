---
title: Agent Platform Landscape
created: 2026-04-20
updated: 2026-04-20
type: concept
tags: [ai-agents, comparison, decision-framework, architecture]
sources: [raw/transcripts/agent-platform-landscape-2026.md]
---

# Agent Platform Landscape

A framework for understanding the spectrum of options for building AI agent systems, from maximum control to maximum convenience. Distilled into 5 distinct tiers across the build-to-buy spectrum.

## The 5-Tier Spectrum

```
Maximum Control ←————————————————————————————————→ Maximum Convenience

[Tier 1]      [Tier 2]        [Tier 3]           [Tier 4]        [Tier 5]
Vanilla Code  Agent           Managed            Visual           Embedded
              Frameworks      Infrastructure     Low-Code         SaaS
```

## Tier 1: Vanilla Code (Maximum Control)

Building agents from scratch using direct API calls.

**Providers:**
- Anthropic Messages API
- Google GenAI SDK
- OpenAI API

**Characteristics:**
- Full control over agent loop
- Direct access to model capabilities
- Maximum flexibility
- Longest development time

## Tier 2: Agent Frameworks

Dedicated libraries that handle the full agentic loop.

**Providers:**
- Claude Agent SDK (formerly Claude Code SDK)
- OpenAI Agents SDK
- Google Agent Development Kit (ADK)
- LangGraph
- CrewAI
- PydanticAI

**Characteristics:**
- Built-in tool dispatch, handoffs, guardrails
- Still hosted on your infrastructure
- Model-agnostic (though tuned to provider models)
- Less boilerplate than Tier 1

## Tier 3: Managed Infrastructure (Production-Ready)

Production infrastructure that wraps around agents.

**Providers:**
- Claude Managed Agents (Anthropic)
- Deep Agents Deploy (LangChain)
- Google Vertex AI Agent Builder
- Azure Foundry Agent Service
- AWS Bedrock AgentCore
- E2B, Modal, Daytona (sandbox execution)

**Characteristics:**
- Containers for sandboxes, tool execution
- Tracing, permissions, orchestration managed
- Offload infrastructure responsibility
- Some loss of flexibility

## Tier 4: Visual Low-Code

Configuration-based agent building with visual interfaces.

**Providers:**
- n8n
- Relevance AI
- Copilot Studio
- Zapier Agents
- Make.com
- Flowise
- Dify

**Characteristics:**
- Visual flow builders
- Faster time to market
- Less flexible than code-based
- Hosted and deployed by platform

## Tier 5: Embedded SaaS

Agent capabilities embedded in existing SaaS applications.

**Providers:**
- Salesforce Agentforce
- Intercom Fin
- HubSpot Breeze
- Atlassian Rovo

**Characteristics:**
- Configure rather than code
- Fastest time to market
- Maximum convenience
- Maximum vendor lock-in

## Decision Factors

| Factor | Choose Lower Tier | Choose Higher Tier |
|--------|------------------|-------------------|
| Control needed | Tier 1-2 | Tier 4-5 |
| Time to market | Longer | Faster |
| Model flexibility | Required | Not required |
| Compliance/privacy | Strict | Standard |
| Customization | High | Low |

## Key Takeaway

There is no right or wrong agent platform. Architecting AI systems is about trade-offs. The 5-tier spectrum provides the vocabulary to make trade-offs deliberately rather than defaulting to whatever launched last week.

Picking the wrong tier locks you into memory, infrastructure, and harness for 18+ months.

## Related Entities

- [[claude-managed-agents]] - Tier 3 example
- [[deep-agents-deploy]] - Tier 3 example
- [[openai-agents-sdk]] - Tier 2 example
- [[langchain]] - Tier 2 example
- [[aws-bedrock]] - Tier 3 example