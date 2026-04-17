---
title: llm.c
created: 2026-04-16
updated: 2026-04-16
type: entity
tags: [repository, c, cuda, gpt, karpathy]
sources: []
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

## Related
- [[andrej-karpathy]] - Author
- [[nanoGPT]] - PyTorch-based alternative