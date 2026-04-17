--- 
title: nanoGPT
created: 2026-04-16
updated: 2026-04-16
type: entity
tags: [repository, python, gpt, transformer, karpathy]
sources: []
---

# nanoGPT

nanoGPT is Andrej Karpathy's "simplest, fastest" repository for training and finetuning medium-sized GPTs. It's a streamlined rewrite of minGPT designed for performance.

## Key Stats
- **Stars:** 56.7k
- **Language:** Python (PyTorch)
- **Lines:** ~300 lines each for train.py and model.py

## GitNexus Analysis
- **Files:** 21
- **Symbols:** 83
- **Relationships:** 142 edges
- **Clusters:** 11 functional areas

## Features
- PyTorch 2.0 `torch.compile()` support
- Reproduces GPT-2 (124M) on OpenWebText in ~4 days on 8x A100
- Supports training from scratch, finetuning, and loading GPT-2 weights
- Character-level training on Shakespeare

## Quick Start
```bash
# Prepare data
python data/shakespeare_char/prepare.py

# Train
python train.py config/train_shakespeare_char.py

# Sample
python sample.py --init_from=gpt2
```

## Architecture
- GPT model with causal self-attention
- Configurable: n_layer, n_head, n_embd, block_size
- Learning rate decay with cosine schedule

## Related
- [[andrej-karpathy]] - Author
- [[mingpt]] - Predecessor
- [[llm-c]] - Pure C/CUDA alternative
