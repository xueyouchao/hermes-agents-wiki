---
title: Graphify
description: AI coding assistant skill that transforms folders into queryable knowledge graphs
type: entity
created: 2026-04-17
updated: 2026-04-17
tags: [knowledge-base, graph, llm, tool, multimodal]
sources: [https://github.com/safishamsi/graphify, https://graphify.net/]
---

# Graphify

## Overview
Graphify is an AI coding assistant skill that transforms folders containing code, documentation, papers, images, or videos into a persistent, queryable knowledge graph. It provides a CLI-driven workflow for building, querying, and maintaining knowledge graphs without requiring a separate vector database.

## Key Features
- **Multimodal extraction**: Processes code (AST), PDFs (citation mining), images (vision-based analysis), and video/audio (local Whisper transcription)
- **Token efficiency**: Achieves ~71.5x token reduction compared to reading raw files for LLM queries
- **No embeddings required**: Uses graph structure and deterministic AST analysis rather than vector embeddings
- **Privacy-preserving**: Code and data processing happens locally; only documentation and papers are sent to LLM APIs for semantic extraction
- **Language support**: Supports 25+ languages via tree-sitter parsing
- **Built-in querying**: CLI commands for graph exploration and shortest-path queries
- **Community detection**: Uses Leiden algorithm to cluster codebases into meaningful communities
- **Transparent relationships**: Every edge labeled as EXTRACTED (direct source), INFERRED (with confidence score), or AMBIGUOUS (flagged for review)

## Installation
```bash
pip install graphifyy && graphify install
# Optional extras for video/audio or Office document support
pip install 'graphifyy[video]' 'graphifyy[office]'
```

## Platform-Specific Installation
| Platform | Command |
|----------|---------|
| Claude Code | `graphify claude install` |
| Cursor | `graphify cursor install` |
| VS Code Copilot | `graphify vscode install` |
| Aider / Trae / OpenClaw | `graphify <platform> install` |

## Usage Examples

### Build a knowledge graph from a folder
```bash
/graphify ./my-codebase          # Default mode
/graphify ./raw --mode deep       # Aggressive inferred edges
/graphify ./raw --update          # Incremental update (changed files only)
/graphify ./raw --watch           # Auto-sync graph as files change
```

### Query the graph
```bash
/graphify query "show the auth flow"
/graphify path "DigestAuth" "Response"          # Shortest path between nodes
/graphify explain "SwinTransformer"              # Plain-language explanation
```

### Add external content
```bash
/graphify add https://arxiv.org/abs/...    # Fetch and graph a paper
/graphify add <video-url>                  # Download, transcribe, and graph
```

## Output Structure
Running `graphify` generates a `graphify-out/` directory containing:
- `graph.html`: Interactive, searchable visual graph (via vis.js)
- `GRAPH_REPORT.md`: Summary of "god nodes," surprising connections, suggested questions
- `graph.json`: Persistent, queryable graph data for long-term use
- `cache/`: SHA256 cache to ensure fast re-runs

## How It Works (Three Passes)
1. **Deterministic AST Pass**: Extracts structure (classes, functions, call graphs) locally without LLM costs
2. **Local Transcription**: Video/audio files transcribed using faster-whisper with domain-aware prompts
3. **LLM Subagent Pass**: Claude/GPT agents run in parallel to extract high-level concepts, design rationale, and semantic relationships from docs and transcripts

## Key Design Decisions
- **No vector database**: Graph structure serves as the similarity signal, eliminating the need for embeddings
- **Local-first processing**: Code never leaves the machine; only metadata/documentation is sent to LLM APIs
- **Explicit confidence labeling**: Relationships tagged EXTRACTED/INFERRED/AMBIGUOUS for auditability
- **Leiden community detection**: Discovers natural clusters in the codebase without manual configuration

## Related Projects
- Complements Neo4j for production storage
- Works alongside Sourcegraph for code-specific search
- Can export embeddings to Code2Vec for ML tasks

## Notes and Caveats
- Requires Python 3.10+ and a supported AI assistant (Claude Code, OpenAI, Gemini, etc.)
- Video transcription requires `faster-whisper` and sufficient local compute
- The graph grows over time; periodic pruning/archiving may be needed for very large codebases

## References
- https://github.com/safishamsi/graphify
- https://graphify.net/
- Medium article: "Graphify: Build a Knowledge Graph From Your Entire Codebase Without Sending Your Code to Anyone"