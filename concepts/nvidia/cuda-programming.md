---
title: CUDA Programming
created: 2026-04-17
updated: 2026-04-17
type: concept
tags: [nvidia, cuda, gpu, programming]
sources: [https://developer.nvidia.com/ai-apps-for-rtx-pcs/sdks-models]
---

# CUDA Programming

CUDA programming is NVIDIA's model for writing GPU-accelerated software. In this wiki it appears as the lower-level foundation beneath TensorRT, `llama.cpp` acceleration, and other RTX AI application tooling.

## In Practice

- GPU kernels provide the compute layer for model inference and supporting operations
- Frameworks such as TensorRT package CUDA optimization so applications do not manage every kernel directly
- Local AI tooling depends on CUDA compatibility across drivers, toolkit versions, and hardware generation

## Related

- [[tensorrt-optimization]]
- [[llm-deployment-on-rtx-pcs]]
- [[nvidia-ai-apps-for-rtx-pcs-technical-details]]
