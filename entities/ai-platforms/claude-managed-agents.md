---
title: Claude Managed Agents
created: 2026-04-20
updated: 2026-04-20
type: entity
tags: [ai-agents, managed-platform, anthropic, cloud-hosted]
sources: [raw/transcripts/agent-platform-landscape-2026.md, https://claude.com/blog/claude-managed-agents]
---

# Claude Managed Agents

Anthropic's fully cloud-hosted agent platform launched in April 2026. Positioned as a "meta-harness" that handles both the "brain" (model + agent loop) and "hands" (sandbox execution, tool calling, MCPs) in a blackbox system.

## Key Facts

| Attribute | Details |
|-----------|---------|
| Provider | Anthropic |
| Launch | April 2026 |
| Pricing | $0.08 per session hour (active runtime) |
| Model Support | Anthropic models only |
| Architecture | Brain vs Hands (decoupled) |

## What Actually Shipped vs What's Locked Away

The announcement promised more than it delivered:

**Available Now:**
- Cloud-hosted agent infrastructure
- Session management and orchestration
- MCP (Model Context Protocol) integration
- Credential vaults (secrets separate from sandboxes)
- Environment management (different libraries per sandbox)
- Basic agent creation in Claude Console

**Locked in Research Preview:**
- Outcome-based tasks
- Multi-agent orchestration
- Stateful memory
- Evaluator agent (Claude self-evaluates and iterates)

## The "Brain vs Hands" Architecture

Anthropic describes Claude Managed Agents as decoupling:
- **Brain**: Model + harness (agent loop) — decision making
- **Hands**: Sandboxes for code execution, tool calling, MCPs — execution

This architecture allows Anthropic to manage infrastructure and scaling while abstracting away complexity.

## Criticism

- Less open than LangChain's alternative
- Locks you into Anthropic models
- Memory built up within a closed harness creates vendor lock-in
- Many advanced features still in research preview
- Completely seeds control of agents to Anthropic

## Related

- [[deep-agents-deploy]] - LangChain's open alternative
- [[openai-agents-sdk]] - OpenAI's agent SDK
- [[agent-platform-landscape]] - 5-tier build-to-buy spectrum
- [[brain-vs-hands-architecture]] - Agent architecture concept
- [[langchain]] - LangChain framework
- [[aws-bedrock]] - AWS managed agent offering (AgentCore)