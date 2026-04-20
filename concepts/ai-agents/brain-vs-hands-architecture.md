---
title: Brain vs Hands Architecture
created: 2026-04-20
updated: 2026-04-20
type: concept
tags: [ai-agents, architecture, design-pattern, anthropic]
sources: [raw/transcripts/agent-platform-landscape-2026.md]
---

# Brain vs Hands Architecture

An agent architecture pattern introduced by Anthropic in their engineering blog post for Claude Managed Agents. The concept decouples the cognitive components from the execution components.

## Core Concept

The architecture divides an AI agent into two distinct parts:

### The Brain

The cognitive processing center that:
- Runs the LLM model
- Contains the agent loop (harness)
- Makes decisions about what tools to call
- Handles reasoning and planning
- Manages context and memory

### The Hands

The execution environment that:
- Actually performs code execution
- Executes tool calls
- Handles MCP (Model Context Protocol) connections
- Manages sandbox environments
- Performs I/O operations

## Why Decouple?

This separation allows:

1. **Scaling independence**: Brain and hands can scale separately
2. **Security isolation**: Execution happens in isolated sandboxes
3. **Infrastructure management**: Anthropic handles the infrastructure
4. **Model evolution**: Harness can evolve with model capabilities

## Implementation in Claude Managed Agents

Anthropic's managed platform implements this by:

1. **Session management**: Orchestrating sessions across brain and hands
2. **Credential vaults**: Secrets separate from sandboxes (not available to LLM)
3. **Environments**: Different libraries can be installed in different environments
4. **MCP integration**: Model Context Protocol for tool connections

## Comparison with Other Approaches

| Architecture | Brain | Hands | Example |
|--------------|-------|-------|---------|
| Coupled | Same process | Same process | Custom agent code |
| Decoupled (Brain/Hands) | Cloud-hosted | Sandboxes | Claude Managed Agents |
| Framework-based | SDK | Your infrastructure | OpenAI Agents SDK |

## Criticism

- Completely seeds control to the provider
- Blackbox system — limited visibility
- Harder to customize behavior
- Memory lock-in within closed harness

## Related Concepts

- [[agent-harness]] - The agent loop that drives decision making
- [[claude-managed-agents]] - Implements brain vs hands
- [[agent-platform-landscape]] - Where this fits in the 5-tier spectrum

## Related Entities

- [[claude-managed-agents]] - Primary implementation
- [[deep-agents-deploy]] - Alternative approach
- [[openai-agents-sdk]] - Similar separation of concerns