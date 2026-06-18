---
title: Agent-Reach
created: 2026-06-18
updated: 2026-06-18
type: entity
tags: [open-source, devtools, ai-agents, python, scraping, social-media]
sources: [xdailyupdates/2026-06-18/raw/003_self-dll.md, https://github.com/Panniantong/Agent-Reach]
confidence: medium
---

# Agent-Reach

Open-source Python toolkit that gives AI agents "eyes on the internet" across social and content platforms without paid APIs.

## Overview

Agent-Reach (GitHub: Panniantong/Agent-Reach) is a Python-based infrastructure project that provides AI coding agents — such as [[claude-managed-agents]], [[cursor]], [[open-hands]], and [[browser-use]] — with the ability to read, search, and summarize content from major online platforms. It replaces commercial scraping APIs (Apify, ScrapingBee, Bright Data, SerpAPI) with local, cookie-based, open-source alternatives.

The project is released under the MIT license and has accumulated 34K+ GitHub stars with rapid daily growth (+2,025 in one day as of 2026-06-18).

## Supported Platforms

| Platform | Capability | Configuration |
|----------|-----------|---------------|
| Web | Read arbitrary pages | None |
| YouTube | Subtitle extraction + search | None |
| RSS | Read RSS/Atom feeds | None |
| Semantic Search | Web-wide semantic search | Automatic (MCP-based, free, no key) |
| GitHub | Read public repos + search | None; private repos require login |
| Twitter/X | Read single tweets; search/timeline with config | Cookie-based login |
| Bilibili | Search + video details (bili-cli, no login) | None; subtitles via OpenCLI |
| Reddit | Search + read posts/comments | Desktop OpenCLI or rdt-cli + cookie |
| Xiaohongshu | Search, read, comment | Desktop OpenCLI or xiaohongshu-mCP QR |
| LinkedIn | Read public pages; profile/company/job search with config | Cookie-based login |
| V2EX | Hot posts, node posts, user info | None |
| Xueqiu | Stock quotes, search, hot posts | Cookie-based login |
| Xiaoyuzhou Podcast | Audio transcription (Whisper, free key) | Cookie-based login |

## Key Design Principles

- **Zero API fees** — all tools open-source, all APIs free. Optional proxy for server deployments (~$1/month).
- **Privacy-local cookies** — cookies stored locally, never uploaded. Open-source code auditable.
- **Continuous backend rollover** — each platform has a preferred + fallback backend. When one breaks, the toolkit switches transparently.
- **Universal agent compatibility** — works with any agent that can execute shell commands.
- **Built-in diagnostics** — `agent-reach doctor` reports connectivity status per platform.

## Architecture Notes

Agent-Reach is implemented primarily in Python (~284KB) with Shell scripts (~15KB). It uses a multi-backend router pattern: each platform has a default scraper and one or more fallback scrapers. When a platform changes its anti-bot measures, the project updates the backend list and users receive the fix via the standard update mechanism.

## GitNexus Analysis

- Nodes: 1,453
- Edges: 2,279
- Clusters: 21
- Flows: 54

## Relationships

- Replaces: commercial scraping stacks (Apify, ScrapingBee, Bright Data, SerpAPI)
- Complements: [[claude-managed-agents]], [[open-hands]], [[browser-use]]
- Related concepts: [[ai-agents]], [[firecrawl]]

## Source

- [GitHub Repository](https://github.com/Panniantong/Agent-Reach)
