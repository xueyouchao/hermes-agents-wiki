---
title: LeRobot
created: 2026-04-20
updated: 2026-04-20
type: entity
tags: [tool, robotics, framework, huggingface, open-source]
sources: [raw/articles/sv101-physical-intelligence.md]
---

# LeRobot

LeRobot is Hugging Face's open-source robot training framework, led by Remi Cadene (recruited from Tesla), designed to make training robots as simple as training language models.

## Overview

- **Developer**: Hugging Face
- **Lead**: Remi Cadene (formerly Tesla Autopilot/Optimus)
- **GitHub Stars**: 20,000+
- **Philosophy**: Democratize robot training

## Key Contributions

### 1. LeRobotDataset
- **Problem**: Each lab uses different data formats
- **Solution**: Unified data format specification
- Enables data sharing across different robot platforms

### 2. Multi-Model Integration
- One-click integration with multiple mainstream policy models
- Researchers don't need to read papers and modify code
- Direct API-style access to state-of-the-art models

### 3. Full Pipeline
Previously, robot training required three different toolchains:
1. Data collection
2. Model training
3. Real robot deployment

LeRobot provides a **unified workflow** covering all three stages.

## Background: Remi Cadene's Journey

Remi Cadene brings invaluable experience:
- **Tesla Autopilot**: Worked on self-driving AI
- **Tesla Optimus**: Contributed to humanoid robot development
- **Hugging Face**: Now building robot training infrastructure

This represents the broader trend of talent flowing from major tech companies to open-source ecosystems.

## Ecosystem Role

LeRobot serves as the "TensorFlow/PyTorch of robotics":
- Abstract away complexity
- Enable rapid experimentation
- Lower barrier to entry

Combined with [[open-x-embodiment]] data and open-source models like [[open-vla]], researchers can now:
1. Use Open X-Embodiment data
2. Train OpenVLA in LeRobot framework
3. Deploy to real robots

**Entire workflow: free and reproducible**

## See Also

- [[huggingface-robotics]] - Parent organization
- [[robotics-vla-models]] - Research hub
- [[open-vla]] - Model trained with LeRobot
- [[genesis-robotics]] - Competing simulation platform