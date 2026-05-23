---
title: CodeGraph
created: 2026-05-23
updated: 2026-05-23
type: entity
tags: [reference, ai-agents]
sources:
  - https://github.com/colbymchenry/codegraph
  - xdailyupdates/2026-05-23/raw/002_Sharbel.md
---

# CodeGraph

CodeGraph is a local-first code-intelligence library, CLI, and MCP server for AI coding agents. It is positioned as a way to pre-index codebases into a semantic graph so tools such as Claude Code, Codex, Cursor, OpenCode, and [[hermes-agent]] can retrieve structured code context with fewer token-heavy search passes. It fits the same broad tooling space as [[knowledge-graph-tools-llm-retrieval]] and adjacent agent workflows in [[agent-platform-landscape]].

## Key Facts
- **Repository:** `colbymchenry/codegraph`
- **URL:** https://github.com/colbymchenry/codegraph
- **Primary language:** TypeScript
- **License:** MIT
- **GitHub snapshot:** 19,169 stars and 1,056 forks during the 2026-05-23 ingest.
- **Packaging:** distributed as `@colbymchenry/codegraph` on npm, with install scripts for macOS/Linux and Windows.

## Architecture Notes
The README and repository guidance describe a layered pipeline: files are parsed through tree-sitter extraction, symbols and relationships are stored in SQLite/FTS5, references are resolved across imports/framework patterns, and graph/context APIs expose callers, callees, impact radius, search, and MCP-serving workflows.

A shallow clone inspected on 2026-05-23 showed modules for database access, extraction, reference resolution, graph traversal/querying, context building, search, sync/watch behavior, MCP serving, CLI wiring, and multi-agent installer targets. GitNexus analysis completed successfully and indexed 4,107 nodes, 9,071 edges, 115 clusters, and 300 flows.

## Why It Matters
The X post that surfaced CodeGraph framed it as one of the fastest-growing GitHub repositories of the week and specifically connected it to Claude Code, Codex, Cursor, OpenCode, and Hermes Agent. For this wiki, the durable value is less the star-growth claim itself and more the tooling pattern: local semantic code graphs as a substrate for agentic coding, retrieval, and context compression.

## Related
- [[knowledge-graph-tools-llm-retrieval]]
- [[ai-repos-research]]
- [[hermes-agent]]
- [[agent-platform-landscape]]
