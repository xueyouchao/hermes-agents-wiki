---
title: llm.c
created: 2026-04-16
updated: 2026-05-11
type: entity
tags: [repository, c, cuda, gpt, karpathy]
sources: [raw/gitnexus/karpathy/llm-c/overview.md]
---

# llm.c

llm.c (LLM in C) is a lightweight implementation for training Large Language Models (GPT-2/GPT-3) in pure C and CUDA, eliminating heavy dependencies like PyTorch.

## Key Stats
- **Stars:** 29.5k
- **Languages:** C, CUDA
- **CPU Reference:** ~1,000 lines of code

## GitNexus Analysis
- **Files:** 97
- **Symbols:** 734
- **Relationships:** 1,456 edges
- **Clusters:** 66 functional areas
- **Processes:** 58 execution flows

## Features
- Pure C/CUDA - no PyTorch dependency
- ~7% faster than PyTorch Nightly
- Uses cuBLAS, cuBLASLt, CUTLASS, cuDNN
- CPU reference implementation for learning
- Multi-GPU and multi-node support via MPI

## Performance
> "Currently, llm.c is a bit faster than PyTorch Nightly (by about 7%)." — Andrej Karpathy

## Quick Start (GPU)
```bash
./dev/download_starter_pack.sh
make train_gpt2fp32cu
./train_gpt2fp32cu
```

## Quick Start (CPU)
```bash
make train_gpt2
OMP_NUM_THREADS=8 ./train_gpt2
```

## Notable Forks
- **Hardware:** AMD (ROCm), Metal (Apple), Habana Gaudi2
- **Languages:** Rust, C#, Java, Go, Swift, Zig, Nim, Mojo

## GitNexus Wiki Pages

- [[raw/gitnexus/karpathy/llm-c/overview]] - GitNexus-generated repository overview
- [[raw/gitnexus/karpathy/llm-c/gpt-2-training]] - Main GPT-2 training loop across C and CUDA entrypoints
- [[raw/gitnexus/karpathy/llm-c/neural-network-operations]] - Transformer layer math and fused operator implementations
- [[raw/gitnexus/karpathy/llm-c/cuda-forward-kernels]] - CUDA forward-pass kernels and optimization variants
- [[raw/gitnexus/karpathy/llm-c/cuda-backward-kernels]] - CUDA backward-pass kernels and gradient propagation details
- [[raw/gitnexus/karpathy/llm-c/cuda-optimizer-communication]] - AdamW updates, gradient norms, and multi-GPU comms
- [[raw/gitnexus/karpathy/llm-c/data-processing-datasets]] - Dataset download, tokenization, and binary shard preparation
- [[raw/gitnexus/karpathy/llm-c/model-evaluation-export]] - Checkpoint export and lm-eval workflow
- [[raw/gitnexus/karpathy/llm-c/llama-training]] - LLaMA 3.x training and export path inside the repo

## Related
- [[andrej-karpathy]] - Author
- [[nanoGPT]] - PyTorch-based alternative