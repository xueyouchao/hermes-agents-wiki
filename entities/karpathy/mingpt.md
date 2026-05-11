---
title: minGPT
created: 2026-04-16
updated: 2026-05-11
type: entity
tags: [repository, python, gpt, transformer, karpathy]
sources: [raw/gitnexus/karpathy/mingpt/overview.md]
---

# minGPT

minGPT is a clean, educational re-implementation of GPT (Generative Pretrained Transformer) in PyTorch. Created by Andrej Karpathy to simplify often sprawling GPT implementations.

## Key Stats

- **Stars:** 24.1k
- **Language:** Python (PyTorch)
- **Status:** Semi-archived (superseded by nanoGPT)

## GitNexus Analysis

- **Files:** 15
- **Symbols:** 122
- **Relationships:** 286 edges
- **Clusters:** 21 functional areas
- **Processes:** 8 execution flows

## Architecture

Three core files (~300 lines total):
1. `mingpt/model.py` - Transformer model definition
2. `mingpt/bpe.py` - Byte Pair Encoder
3. `mingpt/trainer.py` - Training boilerplate

## Project Examples

- `projects/adder` - Train GPT to perform addition
- `projects/chargpt` - Character-level language modeling
- `demo.ipynb` - Minimal sorting task demo
- `generate.ipynb` - Loading GPT-2 weights

## GPT Evolution Reference

| Model | Params | Layers | Heads | d_model | Context |
|-------|--------|--------|-------|---------|---------|
| GPT-1 | 117M | 12 | 12 | 768 | 512 |
| GPT-2 | 1.5B | 48 | 16 | 1600 | 1024 |
| GPT-3 | 175B | 96 | 96 | 12288 | 2048 |

## GitNexus Wiki Pages
- [[raw/gitnexus/karpathy/mingpt/overview]] - GitNexus-generated repository overview
- [[raw/gitnexus/karpathy/mingpt/model-architecture]] - Core GPT model definition and transformer block structure
- [[raw/gitnexus/karpathy/mingpt/training]] - Generic trainer loop, callbacks, and optimizer contract
- [[raw/gitnexus/karpathy/mingpt/tokenization]] - GPT-2 BPE encoder and token preparation flow
- [[raw/gitnexus/karpathy/mingpt/utilities-configuration]] - CfgNode configuration helpers and shared utilities
- [[raw/gitnexus/karpathy/mingpt/addition-project]] - Worked arithmetic-sequence training example
- [[raw/gitnexus/karpathy/mingpt/character-level-gpt-project]] - Character-level language-model project walkthrough
- [[raw/gitnexus/karpathy/mingpt/other]] - Supporting notebooks, tests, and package extras

## Related

- [[andrej-karpathy]] - Author
- [[nanoGPT]] - Successor (faster, more performant)
