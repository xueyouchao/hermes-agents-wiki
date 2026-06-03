---
title: SuperSplat
created: 2026-06-03
updated: 2026-06-03
type: entity
tags: [3dgs, gaussian-splatting, webgpu, editor, browser, open-source]
sources: [xdailyupdates/2026-06-03/raw/001_PlayCanvas.md, https://github.com/playcanvas/supersplat]
---

# SuperSplat — 3D Gaussian Splatting Editor

Free and open-source browser-based editor for inspecting, editing, optimizing, and publishing 3D Gaussian Splatting scenes. Built by [PlayCanvas](https://playcanvas.com).

## Overview

| Attribute | Value |
|-----------|-------|
| Repository | [playcanvas/supersplat](https://github.com/playcanvas/supersplat) |
| Language | TypeScript / JavaScript |
| License | MIT |
| Runtime | Browser (WebGPU + WebGL) |
| GitNexus | 4,720 nodes, 9,520 edges, 141 clusters, 300 flows |

## Key Capabilities

- **Inspect & edit** 3DGS scenes in the browser with no install
- **Optimize** Gaussians: trim, compress, convert formats
- **Publish** processed scenes for web viewing
- **WebGPU renderer** (2026-06): Compute-shader-based rendering for 24M+ Gaussians at 60fps
- **Automatic LOD** (2026-06): Level-of-detail system for progressive streaming

## 2026-06 WebGPU + LOD Upgrade

The June 2026 upgrade introduced a compute-based WebGPU renderer with automatic LOD, enabling near-instant streaming of scenes with 24 million Gaussians directly in the browser at a solid 60fps. This represents an order-of-magnitude capability jump for browser-based 3DGS visualization.

## Related Projects

- [[gaussian-impl]] — Reference Python/PyTorch/CUDA implementation (generates `.splat` and `.ply` files consumed by SuperSplat)
- [[splat-webgl]] — Simpler WebGL-only viewer (antimatter15/splat)
- [[awesome-3dgs]] — Curated list of 3DGS papers and implementations
- [[interiorgs]] — Large-scale indoor 3DGS dataset
- [[3d-gaussian-splatting]] — Core 3DGS technique overview

## References

- [GitHub](https://github.com/playcanvas/supersplat)
- [Live Editor](https://superspl.at/editor)
- [User Guide](https://developer.playcanvas.com/user-manual/gaussian-splatting/editing/supersplat/)