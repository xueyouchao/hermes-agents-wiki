---                      
title: 3D Gaussian Splatting
created: 2026-04-16
updated: 2026-04-16
type: concept
tags: [3dgs, gaussian-splatting, radiance-field, nerf, view-synthesis, 3d-reconstruction]                      
sources: [raw/papers/3d-gaussian-splatting-2023.md]                      
---                  
# 3D Gaussian Splatting

3D Gaussian Splatting is a real-time radiance field rendering technique that represents scenes as 3D Gaussians, enabling high-quality novel view synthesis at 30+ fps in 1080p resolution. Published at SIGGRAPH 2023, it represents a breakthrough in neural rendering by combining the quality of NeRF with real-time performance.

## Core Concept

Instead of using neural networks to represent the scene (like NeRF), 3D Gaussian Splatting uses **3D Gaussians** — ellipsoidal probability distributions — to represent the scene geometry and appearance. Each Gaussian has:
- **Position (mean):** 3D coordinates (x, y, z)
- **Covariance (shape):** 3x3 symmetric matrix representing scale and rotation
- **Appearance (color):** Spherical harmonics coefficients for view-dependent color
- **Opacity:** Transparency value

## Key Innovations

### 1. From Points to Gaussians
Starting from sparse SfM (Structure from Motion) points, the method initializes 3D Gaussians that preserve desirable properties of continuous volumetric radiance fields while avoiding computation in empty space.

### 2. Anisotropic Covariance Optimization
Unlike previous point-based methods that used spherical representations, 3D GS optimizes anisotropic covariance to accurately represent complex scene geometry.

### 3. Visibility-Aware Rendering
A fast rendering algorithm that supports anisotropic splatting and accelerates both training and enables real-time rendering.

## Performance Comparison

| Method | Training Time | Rendering Speed | Quality |
|--------|---------------|-----------------|---------||
| NeRF | 2-4 days | ~10 sec/frame | Excellent |
| Instant-NGP | ~5 min | ~60 fps | Good |
| **3D Gaussian Splatting** | ~15-30 min | **30+ fps** | Excellent |

## GitNexus Analyzed Repositories

### [[gaussian-splatting-refimpl]]
Original reference implementation from Inria/GraphDeco
- 339 symbols | 831 edges | 26 clusters | 28 flows
- Python/PyTorch + CUDA extensions

### [[splat-webgl]]
WebGL browser-based viewer
- 40 symbols | 92 edges | 4 clusters | 2 flows
- Pure JavaScript, no dependencies

### [[awesome-3dgs]]
Curated paper list and resources
- 227 symbols | 524 edges | 16 clusters | 20 flows

## Use Cases

| Industry | Application |
|----------|-------------|
| **VR/AR** | Real-time scene capture and rendering |
| **Gaming** | Photorealistic environment scanning |
| **Film** | Virtual production, set extensions |
| **Robotics** | Scene reconstruction for navigation |
| **Cultural Heritage** | 3D preservation of artifacts |
| **E-commerce** | Product visualization |

## Related Concepts

- [[nerf|NeRF]] — Neural Radiance Fields (precursor technology)
- [[durable-execution]] — Analogous concept: state persistence in computation
- [[view-synthesis]] — Generating novel views from known viewpoints
- [[point-cloud]] — Related 3D representation

## References

- [Original Paper (SIGGRAPH 2023)](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/)
- [GitHub Repository](https://github.com/graphdeco-inria/gaussian-splatting)
- [Video](https://youtu.be/T_kXY43VZnk)
