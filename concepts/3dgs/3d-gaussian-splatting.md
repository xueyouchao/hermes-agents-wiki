---
title: 3D Gaussian Splatting
created: 2026-04-16
updated: 2026-04-17
type: concept
tags: [3dgs, gaussian-splatting, radiance-field, nerf, view-synthesis, 3d-reconstruction]
sources: [https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/, https://github.com/graphdeco-inria/gaussian-splatting]
---

# 3D Gaussian Splatting

3D Gaussian Splatting is a real-time radiance field rendering technique that represents scenes as optimized 3D Gaussians. It is notable because it closes much of the quality gap with NeRF-style methods while supporting interactive rendering speeds.

## Core Idea

Instead of storing a scene only as dense voxels or a neural field, 3D Gaussian Splatting uses anisotropic Gaussians with position, covariance, color, and opacity. This makes rendering more direct and avoids spending compute on large empty regions.

## Why It Matters

- Delivers high-quality novel view synthesis
- Supports real-time or near-real-time rendering
- Works well as a bridge between reconstruction and deployable rendering systems

## Performance Profile

| Method | Training Time | Rendering Speed | Quality |
|--------|---------------|-----------------|---------|
| NeRF | 2-4 days | Slow per-frame rendering | Excellent |
| Instant-NGP | Minutes | Very fast | Good |
| 3D Gaussian Splatting | 15-30 min | 30+ fps class rendering | Excellent |

## Related Repositories

### [[gaussian-impl]]

Reference implementation for the original approach, centered on Python, PyTorch, and CUDA extensions.

### [[splat-webgl]]

Browser-based WebGL viewer for Gaussian splat scenes.

### [[awesome-3dgs]]

Curated index of papers, implementations, and research directions built on top of 3DGS.

## Use Cases

- Real-time scene capture and rendering
- Photorealistic environment reconstruction
- Virtual production and digital sets
- Robotics and navigation scene understanding
- 3D cultural heritage preservation

## Related Concepts

- [[nerf]] - The main predecessor in neural radiance field rendering
- [[view-synthesis]] - The task 3DGS is often evaluated against
- [[point-cloud]] - A simpler geometric representation used in adjacent pipelines

## References

- [Original Paper](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/)
- [Reference Repository](https://github.com/graphdeco-inria/gaussian-splatting)
- [Project Video](https://youtu.be/T_kXY43VZnk)
