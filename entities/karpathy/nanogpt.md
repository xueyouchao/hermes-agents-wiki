--- 
title: nanoGPT
created: 2026-04-16
updated: 2026-05-11
type: entity
tags: [repository, python, gpt, transformer, karpathy]
sources: [raw/gitnexus/karpathy/nanogpt/overview.md]
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

## GitNexus Wiki Pages
- [[raw/gitnexus/karpathy/nanogpt/overview]] - GitNexus-generated repository overview
- [[raw/gitnexus/karpathy/nanogpt/model-architecture]] - Single-file GPT-2 model implementation details
- [[raw/gitnexus/karpathy/nanogpt/training]] - Distributed training loop, schedules, and checkpoint flow
- [[raw/gitnexus/karpathy/nanogpt/inference]] - Autoregressive sampling and checkpoint loading path
- [[raw/gitnexus/karpathy/nanogpt/benchmarking]] - MFU and throughput benchmarking workflow
- [[raw/gitnexus/karpathy/nanogpt/data-preparation]] - Dataset-to-binary preprocessing pipeline
- [[raw/gitnexus/karpathy/nanogpt/configuration-utility]] - CLI/config-file override mechanism used by scripts
- [[raw/gitnexus/karpathy/nanogpt/other]] - Config presets, datasets, and supporting project files

## Related
- [[andrej-karpathy]] - Author
- [[mingpt]] - Predecessor
- [[llm-c]] - Pure C/CUDA alternative
