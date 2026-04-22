---
title: InteriorGS Dataset
created: 2026-04-22
updated: 2026-04-22
type: entity
tags: [3dgs, dataset, indoor-scenes, semantic-annotation, embodied-ai, scene-understanding]
sources: [https://huggingface.co/datasets/spatialverse/InteriorGS, https://github.com/manycore-research/InteriorGS]
---

# InteriorGS Dataset

A large-scale 3D Gaussian Splatting dataset of semantically labeled indoor scenes, designed for embodied AI and scene understanding research.

## Overview

| Attribute | Value |
|-----------|-------|
| Total Size | 43.8 GB |
| Scenes | 1,000 indoor scenes |
| Rendered Images | 5+ million |
| Object Instances | 554,000+ |
| Semantic Categories | 755 |
| Environment Types | 80+ (homes, stores, museums, banquet halls, etc.) |

## Key Features

### 3D Gaussian Representation
- Scenes stored as **compressed PLY files** using SuperSplat method
- Coordinate system: **XYZ = (Right, Back, Up)**, units in meters
- Real-time rendering support at 30+ fps

### Rich Semantic Annotations
- **labels.json**: 3D oriented bounding boxes with per-object semantic class labels and instance IDs
- Bounding boxes defined by 8 corner vertices
- 755 semantic categories covering furniture, fixtures, appliances

### Occupancy Maps
- **Resolution**: 1024x1024 pixels (configurable)
- **Format**: PNG (grayscale) + JSON for coordinate mapping
- **Values**: 255=white (free), 0=black (occupied), 127=gray (unknown)
- Top-down navigable floor space visualization

### Floorplan Data (structure.json)
- **Rooms**: Virtual partitions with 2D polygon profiles, room type labels
- **Walls**: Line segments with thickness, height, and openings (doors/windows)
- **Instances**: Object positions and bounding box sizes in world frame

## Dataset Structure

```
InteriorGS/
├── 0001_839920/
│   ├── 3dgs_compressed.ply   # Gaussian point cloud
│   ├── labels.json           # Semantic annotations
│   ├── occupancy.png         # Occupancy map
│   ├── occupancy.json        # Coordinate mapping
│   └── structure.json        # Floorplan data
└── ...
```

## Supported Downstream Tasks

- **3D Scene Understanding** — Semantic segmentation, object detection
- **Controllable Scene Generation** — Modify layouts, add/remove objects
- **Embodied Agent Navigation** — Continuous 3D environment for AI agents
- **Spatial Intelligence Research** — Planning, reasoning about space

## Why It Matters

- Addresses limitations of RGB-D scans (incomplete geometry, occlusions)
- Provides consistent semantic/spatial annotations missing in artist-designed scenes
- Enables physically executable navigation for embodied AI agents
- First large-scale 3DGS dataset with comprehensive floorplan + occupancy data

## Related Concepts

- [[3d-gaussian-splatting]] — Core rendering technique
- [[awesome-3dgs]] — Curated 3DGS paper list
- [[gaussian-impl]] — Reference implementation
- [[nerf]] — Predecessor neural radiance field method

## References

- [HuggingFace Dataset](https://huggingface.co/datasets/spatialverse/InteriorGS)
- [GitHub Repository](https://github.com/manycore-research/InteriorGS)
- [Sample Viewer](https://www.kujiale.com/pub/koolab/koorender/InteriorGS)
- [Paper (arXiv:2510.21307)](https://arxiv.org/abs/2510.21307)