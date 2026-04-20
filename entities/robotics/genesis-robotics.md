---
title: Genesis Robotics
created: 2026-04-20
updated: 2026-04-20
type: entity
tags: [tool, robotics, simulation, cmu, open-source]
sources: [raw/articles/sv101-physical-intelligence.md]
---

# Genesis Robotics

Genesis is an open-source robotics simulation platform led by Carnegie Mellon University (CMU), launched December 2024, designed to dramatically accelerate robot training through ultra-fast simulation.

## Overview

- **Lead Institution**: Carnegie Mellon University (CMU)
- **Collaborators**: MIT, Stanford, NVIDIA, 20+ research labs
- **Goal**: Enable years of training in hours of simulation

## Key Innovation: Speed

Genesis achieves unprecedented simulation speeds:

| Metric | Value |
|--------|-------|
| **Simulation Speed** | 43 million frames/second |
| **Real-time Factor** | 430,000x faster than real-time |
| **Hardware** | Single RTX 4090 |

### Training Time Comparison

- **Genesis**: 1 hour of simulation = **49 years** of real-world training
- **Traditional simulation**: Orders of magnitude slower
- **Real robot training**: Impractical for large-scale learning

This democratizes simulation-based training:
- Previously: Only large companies could afford large-scale simulation
- Now: A graduate student with a consumer GPU can achieve equivalent training

## Technical Approach

- Physics-based simulation
- High-fidelity environment modeling
- Optimized for parallel computation

## Competition: NVIDIA Newton

Notably, NVIDIA developed the **Newton** physics engine in collaboration with:
- Google DeepMind
- Disney Research

This creates direct competition in the simulation tools space:
- **Genesis**: Academic/community led
- **Newton**: Corporate (NVIDIA) led

## Ecosystem Role

Genesis addresses a critical bottleneck in robot learning:
- **Sim-to-Real gap**: Transferring simulation learning to real robots
- **Training efficiency**: Making large-scale training practical
- **Cost reduction**: Enabling research without massive compute budgets

Combined with [[lerobot]] for real-world training:
- **LeRobot**: Real world learning
- **Genesis**: Virtual world learning
- **Together**: Complete training pipeline at a fraction of previous cost

## Impact

Genesis represents the "simulation" pillar of the open-source robotics ecosystem, reducing training costs from millions of dollars to hundreds of dollars.

## See Also

- [[lerobot]] - Real-world training framework
- [[nvidia-gr00t]] - Uses NVIDIA simulation tools
- [[robotics-vla-models]] - Research hub
- [[vla-model]] - Training methodology