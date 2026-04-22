---
title: InteriorGS - 3DGS Indoor Dataset
created: 2026-04-22
updated: 2026-04-22
type: source
tags: [3dgs, dataset, indoor-scenes]
sources: [https://huggingface.co/datasets/spatialverse/InteriorGS]
---

# InteriorGS Dataset Source

**URL**: https://huggingface.co/datasets/spatialverse/InteriorGS
**Source**: SpatialVerse Research Team, Manycore Tech Inc.
**Total Size**: 43.8 GB

## Overview

InteriorGS is a 3D Gaussian Splatting dataset of 1,000 semantically labeled indoor scenes. Created by photorealistically rendering handcrafted 3D environments, then reconstructing splatting-based representations from over 5 million images. Supports free-form agent navigation within continuous 3D environments.

### Key Statistics
- 1,000 indoor scenes
- 5+ million rendered images
- 554,000+ object instances
- 755 semantic categories
- 80+ environment types

## Data Structure

### 3D Gaussian Models (.ply)
- Compressed using SuperSplat method
- Coordinate system: XYZ = (Right, Back, Up), meters

### Semantic Annotations (labels.json)
- 3D oriented bounding boxes (8 corner vertices)
- Per-object semantic class labels with instance IDs

### Occupancy Maps
- 1024x1024 PNG + JSON metadata
- Free space (255), occupied (0), unknown (127)

### Floorplan Data (structure.json)
- Rooms: virtual partitions with room types
- Walls: line segments with thickness/height
- Instances: object positions and sizes

## Citation

```bibtex
@misc{miao2025physicallyexecutable3dgaussian,
  title={Towards Physically Executable 3D Gaussian for Embodied Navigation}, 
  author={Bingchen Miao et al.},
  year={2025},
  eprint={2510.21307},
  archivePrefix={arXiv},
  primaryClass={cs.CV},
  url={https://arxiv.org/abs/2510.21307}, 
}
```