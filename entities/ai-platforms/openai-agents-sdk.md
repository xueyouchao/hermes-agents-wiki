---
title: OpenAI Agents SDK
created: 2026-04-20
updated: 2026-04-20
type: entity
tags: [ai-agents, agent-framework, openai, sdk]
sources: [raw/transcripts/agent-platform-landscape-2026.md, https://openai.com/index/the-next-evolution-of-the-agents-sdk/]
---

# OpenAI Agents SDK

OpenAI's agent development library that evolved from earlier versions to include harness-like features. Positioned in Tier 2 of the agent platform spectrum (agent frameworks).

## Key Facts

| Attribute | Details |
|-----------|---------|
| Provider | OpenAI |
| Type | Open-source library |
| Model Support | Primarily OpenAI, but model agnostic |
| Tier | 2 (Agent Frameworks) |
| Pricing | Free (open source) + sandbox provider fees |

## Evolution

The Agents SDK represents OpenAI's evolution from simple API wrappers to a full-featured agent development framework. It includes:

- **Agent loop management**: Built-in state handling
- **Code execution**: Native sandbox integration with providers like E2B, Daytona, Modal
- **Tool calling**: Advanced function calling capabilities
- **Memory and workspace**: File system mounts and state management
- **Separation of concerns**: Secrets management separate from harness and sandbox

## Architecture

Like Claude Managed Agents and Deep Agents Deploy, OpenAI's Agents SDK separates:
- Agent logic (the harness)
- Sandbox execution environment
- Secrets and credentials

The SDK is open source and available on GitHub, with releases like v0.14 covering sandbox agents, clients, memory, and workspace mounts.

## Comparison

| Dimension | OpenAI Agents SDK | Claude Managed Agents | Deep Agents Deploy |
|-----------|------------------|----------------------|-------------------|
| Hosting | Self-hosted | Cloud-hosted | Cloud or BYO |
| Model | OpenAI-optimized | Anthropic only | Agnostic |
| Pricing | Free + sandbox fees | $0.08/session hr | $39/seat/mo |
| Control | High | Low | Medium |

## Use Cases

The Agents SDK is ideal for:
- Developers who want control without building from scratch
- Projects requiring OpenAI model optimization
- Applications needing sandbox code execution
- Teams wanting to avoid vendor lock-in

## Related

- [[claude-managed-agents]] - Anthropic's managed platform
- [[deep-agents-deploy]] - LangChain's managed platform
- [[agent-platform-landscape]] - 5-tier build-to-buy spectrum
- [[langchain]] - Alternative agent framework