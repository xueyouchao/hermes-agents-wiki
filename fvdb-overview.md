# NVIDIA FVDB Wiki

> NVIDIA's fVDB (Flexible Virtual Database) is a deep-learning framework for sparse, large-scale, and high-performance spatial intelligence. It bridges real-world 3D data with AI-ready virtual representations.

## Domain
GPU-accelerated 3D deep learning framework for spatial intelligence, generative AI, and digital twins.

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `fvdb-overview.md`)
- Every wiki page starts with YAML frontmatter
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be appended to `log.md`

## Frontmatter
```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [from taxonomy below]
sources: [raw/articles/source-name.md]
---
```

## Tag Taxonomy
- Frameworks: framework, pytorch, integration
- Performance: scalability, speed, memory, optimization
- Applications: autonomous-vehicles, robotics, geospatial, climate-science
- Components: architecture, operators, microservices
- Data-Structures: openvdb, nanovdb, sparse-grids
- Research: publications, benchmarks, evaluation

## Overview

### What is fVDB?
NVIDIA fVDB (Flexible Virtual Database) is a GPU-optimized deep learning framework designed for sparse, large-scale, and high-performance spatial intelligence. It serves as an extension to PyTorch that provides a complete set of differentiable primitives for 3D learning tasks.

### Core Purpose
fVDB bridges the gap between real-world 3D data (LiDAR, point clouds, NeRFs) and AI-ready virtual representations, enabling spatial intelligence for autonomous vehicles, robots, and digital twins at scale.

## Architecture

### Foundation
- Built on top of **OpenVDB** (industry standard for sparse volumetric data)
- Leverages **NanoVDB** (NVIDIA's GPU-accelerated OpenVDB implementation)
- Fully integrated with **PyTorch** for deep learning workflows

### Key Technical Components
1. **Sparse Volumetric Grids** - Efficient representation of 3D data
2. **GPU-Accelerated Operators** - Differentiable convolution, pooling, attention
3. **Ray Tracing Kernels** - Fast rendering using HDDA techniques
4. **Jagged Tensors** - Support for non-uniform batch processing

## Performance Advantages

| Metric | Improvement |
|--------|-------------|
| Spatial Scale | 4x larger |
| Processing Speed | 3.5x faster |
| Operators Available | 10x more |
| Memory Efficiency | Competitive on small inputs |

## Key Applications

### Research & Development
- Neural Kernel Surface Reconstruction (NKSR)
- XCube (3D generative AI)
- NeRF-XL (large-scale Neural Radiance Fields)
- Physics Super-Resolution

### Production Systems
- Autonomous vehicle perception
- Robot spatial understanding
- Digital twins for smart cities
- Climate science modeling

## Microservices

### NVIDIA NIM Integration
| Microservice | Function |
|-------------|----------|
| fVDB Mesh Generation NIM | Converts point clouds to OpenUSD meshes |
| fVDB NeRF-XL NIM | Generates large-scale NeRFs in OpenUSD |
| fVDB Physics Super-Res NIM | AI-enhanced physics simulation super-resolution |

## Getting Started

### Early Access
- Developers can [apply for early access](https://developer.nvidia.com/fvdb/early-access-form) to the PyTorch extension
- Open source release planned for OpenVDB GitHub repository

### Integration
- Works with NVIDIA Research projects
- Integrated into NVIDIA DRIVE
- Compatible with NVIDIA Omniverse

## References
- [NVIDIA Developer Blog](https://developer.nvidia.com/blog/building-spatial-intelligence-from-real-world-3d-data-using-deep-learning-framework-fvdb/)
- [Research Publication](https://research.nvidia.com/publication/2024-07_fvdb-deep-learning-framework-sparse-large-scale-and-high-performance-spatial)
- [Technical Blog](https://blogs.nvidia.com/blog/fvdb-bigger-digital-models/)
- [OpenVDB Foundation](https://openvdb.github.io/fvdb-core/)

## Changelog
- 2024-07-01: Initial framework release
- 2024-07: Early access program launched
- 2024-08: NIM microservices announced