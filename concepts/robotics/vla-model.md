---
title: VLA Model (Vision-Language-Action)
created: 2026-04-20
updated: 2026-04-20
type: concept
tags: [robotics, vla, concept, architecture]
sources: [raw/articles/sv101-physical-intelligence.md]
---

# VLA Model (Vision-Language-Action)

VLA (Vision-Language-Action) models represent the dominant paradigm in modern embodied AI, enabling robots to "see" their environment, "understand" instructions, and "execute" appropriate actions.

## Core Function

VLA models integrate three capabilities:

1. **Vision**: Perceive surrounding environment through cameras/sensors
2. **Language**: Understand user instructions and contextual reasoning
3. **Action**: Generate correct motor commands to execute tasks

This mirrors human cognitive processing: perception → understanding → action.

## Architecture Comparison

### Single Visual Encoder (e.g., RT-2-X)
- One encoder handles all visual processing
- "One brilliant person doing everything"
- High capability but potentially lower information processing efficiency

### Dual Visual Encoder (e.g., OpenVLA)
- **DINOv2**: Spatial relationship understanding
- **SigLIP**: Semantic and common-sense understanding
- "Three-person team" with specialized roles
- Physically isolates two information types, optimizes each, then unifies for decision-making

### Flow Matching (e.g., π₀)
- Instead of predicting language tokens for actions
- Generates continuous joint trajectories directly
- Outputs smooth control signals at ~50Hz
- More like traditional control systems, just with AI generating control signals

## Action Representation Approaches

### Discrete Token Prediction
- Treats actions as language tokens
- Predicts discrete action tokens step-by-step
- Used by: RT-2-X, OpenVLA

### Flow Matching
- Generates continuous trajectory directly
- Outputs smooth motion control signals
- Used by: π₀

### Diffusion Policy
- Uses diffusion models for action generation
- Supports various robot platforms flexibly
- Used by: Octo

## Control Frequency Considerations

| Model | Frequency | Use Case |
|-------|-----------|----------|
| π₀ | ~50Hz | High-precision tasks (paper folding, poker) |
| GR00T N1 | Dual-system | Balanced slow/fast thinking |
| Octo | Configurable | Universal adaptation |

Higher frequency enables:
- Smoother motion (less jitter)
- Better handling of dynamic environments
- Precision tasks requiring fine motor control

## Parameter Efficiency

Key insight from OpenVLA's victory: **scale isn't everything**

- OpenVLA: 7B parameters → beats 55B RT-2-X
- Lesson: Data diversity + architecture + training strategy > raw parameter count

## Current Research Questions

1. **Data Strategy**: Internet video vs. real robot data - which is more important?
2. **Scaling**: Does the "scaling law" apply to robotics as it does to LLMs?
3. **Sim-to-Real**: How to effectively transfer simulation training to real robots?
4. **Generalization**: How to achieve true zero-shot generalization across tasks?

## Open Source vs. Closed Source

Unlike LLM where OpenAI/Anthropic/Google led and open-source caught up 1-2 generations later, in robotics:

- Open-source and closed-source started almost simultaneously
- OpenVLA defeated RT-2-X in June 2024
- Reason: Robotics is still in early stages - no company has overwhelming data/algorithm advantage
- This creates a rare "level playing field" window

## See Also

- [[open-vla]] - 7B parameter model with dual encoder
- [[octo]] - Universal policy model
- [[physical-intelligence]] - π₀ with flow matching
- [[nvidia-gr00t]] - Dual-system architecture
- [[robotics-vla-models]] - Research hub