---
title: React Doctor
created: 2026-05-27
updated: 2026-05-27
type: entity
tags: [devtools, agent-skill, react, linting, open-source]
sources: [xdailyupdates/2026-05-27/raw/001_Aiden_Bai.md, "https://github.com/millionco/react-doctor"]
---

# React Doctor

Deterministic React codebase scanner and agent skill that catches issues across state & effects, performance, architecture, security, and accessibility. Works for all React frameworks (Next.js, Vite, TanStack, React Native, Expo).

## Key Facts

- **Repo:** [millionco/react-doctor](https://github.com/millionco/react-doctor)
- **Author:** Aiden Bai (also creator of Million.js)
- **Language:** TypeScript
- **License:** MIT
- **Install:** `npx react-doctor@latest`
- **Agent integration:** Installable as agent skill (`npx react-doctor@latest install`) for Claude Code, Cursor, Codex, and OpenCode
- **CI:** Available as reusable GitHub Action for PR scanning with inline annotations

## Architecture

- **@react-doctor/core** — private diagnostic engine built on Effect v4
- **@react-doctor/api** — programmatic `diagnose()` API
- **react-doctor** (CLI) — published CLI, `bin`, and public `inspect()`
- **oxlint-plugin-react-doctor** — 100+ rules as an oxlint plugin
- **eslint-plugin-react-doctor** — ESLint mirror of the oxlint plugin

## Why Notable

Bridges the gap between static linting and agentic coding: React Doctor detects issues deterministically and then teaches the coding agent to avoid them. Fits the wider pattern of agent-oriented devtools (see [[agent-platform-landscape]], [[everything-claude-code]]).

## Related

- [[agent-platform-landscape]] — 5-tier build-to-buy spectrum for agents
- [[everything-claude-code]] — Claude Code resources and agent skills