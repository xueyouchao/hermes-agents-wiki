---
title: Xiaomi Robotics
created: 2026-04-20
updated: 2026-04-20
type: entity
tags: [company, robotics, china, vla, xiaomi]
sources: [raw/articles/sv101-physical-intelligence.md]
---

# Xiaomi Robotics

Xiaomi's robotics division has emerged as a significant Chinese player in open-source VLA models, releasing the Xiaomi-Robotics-0.47 model in February 2026.

## Recent Release

### Xiaomi-Robotics-0.47

- **Parameters**: 4.7B
- **Release Date**: February 12, 2026
- **Architecture**: MoT (Mixture of Thoughts) hybrid architecture

### Key Innovation

The MoT architecture separates the "brain" and "little brain":
- **Brain**: High-level reasoning, task planning
- **Little brain**: Low-level motor control, real-time反应

This addresses a critical issue in VLA models: **inference latency**. By separating these functions, Xiaomi achieves faster response times while maintaining high-level understanding.

### Consumer GPU Compatibility

A significant advantage: the model can run on consumer-grade GPUs, making it accessible for:
- Research labs with limited compute
- Hobbyists and developers
- Small companies without enterprise hardware

This democratizes access to robot AI capabilities.

## Company Context

Xiaomi brings consumer electronics expertise to robotics:
- Experience with hardware-software integration
- Manufacturing capabilities
- Large user base for potential home robot deployment

## Strategic Position

Xiaomi's approach represents the Chinese "practical deployment" philosophy:
- Not just research - focus on making it runnable
- Consumer-friendly (runs on consumer GPU)
- Bridges research and real-world application

## See Also

- [[robotics-vla-models]] - Research hub
- [[four-factions]] - Analysis of Chinese players
- [[ant-group-lingbot]] - Another Chinese VLA model
- [[vla-model]] - Technical foundation