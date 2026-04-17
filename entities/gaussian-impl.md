---
title: Gaussian Splatting Reference Implementation
created: 2026-04-16
updated: 2026-04-17
type: entity
tags: [3dgs, gaussian-splatting, repository, python, pytorch, radiance-field]
sources: [https://github.com/graphdeco-inria/gaussian-splatting]
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

## Related Projects

- [[3d-gaussian-splatting]] - Concept page for the rendering method
- [[splat-webgl]] - Browser-oriented viewer
- [[awesome-3dgs]] - Curated ecosystem and paper list

## References

- [GitHub Repository](https://github.com/graphdeco-inria/gaussian-splatting)
- [Project Page](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/)
