---
title: autoresearch
created: 2026-04-16
updated: 2026-04-16
type: entity
tags: [repository, python, ai-agent, autonomous, llm-training, karpathy]  
sources: []
---

# autoresearch

autoresearch is an experimental framework for autonomous AI agents to conduct LLM research. The agent modifies code, runs training experiments, evaluates results, and iterates without human intervention.

## Key Stats
- **Stars:** 73k
- **Language:** Python
- **Status:** Active
- **Updated:** Mar 26, 2026

## GitNexus Analysis
- **Files:** ~30
- **Symbols:** 96
- **Relationships:** 210 edges
- **Clusters:** 17 functional areas
- **Processes:** 6 execution flows

## The Core Idea

Instead of a human researcher manually tuning hyperparameters or architectures, you provide an AI agent with a small, real LLM training setup:
- **The Loop:** Agent modifies code → trains for 5 minutes → checks for improvement → keeps or discards → repeats
- **Human Role:** Edit `program.md` to guide research instead of editing Python files

## Three-File System

1. **`prepare.py`** (Fixed): Data preparation, tokenizer training - not modified by agent
2. **`train.py`** (Mutable): Model, optimizer, training loop - agent edits this
3. **`program.md`** (Instructions): Research instructions - human edits this

## Key Constraints

| Parameter | Value |
|-----------|-------|
| Time Budget | 5 minutes per run |
| Metric | val_bpb (validation bits per byte) - lower is better |
| Hardware | Single NVIDIA GPU (tested on H100) |

## Quick Start
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Download data and train tokenizer
uv run prepare.py

# Run single experiment
uv run train.py
```

## Notable Forks
- **MacOS:** autoresearch-macos, autoresearch-mlx
- **Windows:** autoresearch-win-rtx
- **AMD:** autoresearch

## Related
- [[andrej-karpathy]] - Author
- [[nanochat]] - Builds upon nanochat