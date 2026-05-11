---
title: Gaussian Splatting Reference Implementation
created: 2026-04-16
updated: 2026-05-11
type: entity
tags: [3dgs, gaussian-splatting, repository, python, pytorch, radiance-field]
sources: [https://github.com/graphdeco-inria/gaussian-splatting, raw/gitnexus/3dgs/gaussian-impl/overview.md]
---

# Gaussian Splatting Reference Implementation

This is the reference repository for the original 3D Gaussian Splatting method from Inria/GraphDeco. It is the implementation baseline for much of the later 3DGS ecosystem.

## Technical Shape

- Python and PyTorch training stack
- CUDA/OpenGL rendering components
- Scripts for optimization, rendering, and scene conversion

## Why It Matters

- Defines the baseline implementation of the original method
- Acts as the source project many later forks and extensions build on
- Connects the 3DGS paper to a practical training and rendering workflow

## GitNexus Wiki Pages

- [[raw/gitnexus/3dgs/gaussian-impl/overview]] - GitNexus-generated repository overview
- [[raw/gitnexus/3dgs/gaussian-impl/training-pipeline]] - Optimization loop, densification, and checkpointing flow
- [[raw/gitnexus/3dgs/gaussian-impl/rendering]] - Differentiable rasterization path and per-view rendering logic
- [[raw/gitnexus/3dgs/gaussian-impl/rendering-pipeline]] - Offline rendering workflow for saved checkpoints
- [[raw/gitnexus/3dgs/gaussian-impl/gaussian-model]] - Core Gaussian parameterization, serialization, and densification state
- [[raw/gitnexus/3dgs/gaussian-impl/scene-management]] - Scene assembly from cameras, point clouds, and datasets
- [[raw/gitnexus/3dgs/gaussian-impl/camera-system]] - Camera representation and view parameter handling
- [[raw/gitnexus/3dgs/gaussian-impl/conversion]] - COLMAP preprocessing and dataset conversion entrypoint
- [[raw/gitnexus/3dgs/gaussian-impl/evaluation-metrics]] - PSNR/SSIM/LPIPS evaluation workflow

## Related Projects

- [[3d-gaussian-splatting]] - Concept page for the rendering method
- [[splat-webgl]] - Browser-oriented viewer
- [[awesome-3dgs]] - Curated ecosystem and paper list

## References

- [GitHub Repository](https://github.com/graphdeco-inria/gaussian-splatting)
- [Project Page](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/)
