---
title: NVIDIA GR00T N1
created: 2026-04-20
updated: 2026-04-20
type: entity
tags: [model, robotics, nvidia, gr00t, foundation-model]
sources: [raw/articles/sv101-physical-intelligence.md]
---

# NVIDIA GR00T N1

GR00T N1 is NVIDIA's open humanoid robot foundation model, introduced at GTC 2025 and updated to N1.6 at CES 2026. It represents NVIDIA's full-stack approach to robotics.

## Release Timeline

| Version | Event | Time |
|---------|-------|------|
| GR00T N1 | GTC 2025 (March) | First release |
| GR00T N1.6 | CES 2026 (January) | Latest iteration |

## Technical Architecture

GR00T N1 uses a **dual-system architecture**:

### System 2: Slow Thinking
- Based on Vision-Language Model (VLM)
- Responsible for: understanding environment, interpreting instructions, making plans
- Operates at lower frequency

### System 1: Fast Thinking  
- Based on Diffusion Transformer
- Converts plans into precise joint motions at high frequency
- Operates at high frequency

### End-to-End Training
- Both systems trained jointly
- Tightly coupled for seamless coordination
- **Parameters**: 2.2B

## Open Source Status

- Model weights: Released
- Code: Released
- Early access: Granted to leading humanoid robot companies

## The "Semi-Open" Controversy

Some consider GR00T N1 "pseudo-open-source" because the entire training pipeline is tightly bound to NVIDIA's hardware ecosystem:

### Hardware Lock-in Chain
1. **Training**: Requires H100 GPU clusters
2. **Simulation**: Uses Omniverse platform
3. **Synthetic Data**: Uses Isaac Sim for generation
4. **Deployment**: Targets Jetson Thor chips

### Comparison with Pure Open Source

| Aspect | GR00T N1 | OpenVLA/Octo |
|--------|----------|--------------|
| Hardware | NVIDIA only | Any GPU |
| Platform | Omniverse only | Platform agnostic |
| Ecosystem | Locked | Open |

This represents the difference between "open" and "open-source":
- **Open**: Access to deliverables
- **Open-source**: Full freedom to use, modify, and deploy

## NVIDIA's Full Stack Ecosystem

NVIDIA doesn't just provide models - they provide an entire stack:

| Layer | Tool | Purpose |
|-------|------|---------|
| Model | GR00T N1 | Robot "brain" |
| Simulation | Isaac Sim | Synthetic training data |
| Digital Twin | Omniverse | Environment simulation |
| Data Generation | Cosmos | Video data generation |
| Physics Engine | Newton | Physics simulation |

This "one-stop service" helps NVIDIA:
1. Establish robot AI standards
2. Drive hardware sales (H100, Jetson Thor)
3. Build an ecosystem lock-in effect

## Strategic Analysis

NVIDIA's approach differs from pure academic open-source:
- Academic open-source: Pursues knowledge sharing and scientific reproducibility
- Commercial open-source: Pursues ecosystem control and market standards
- Strategic open-source: Pursues platform lock-in and hardware sales

The robotics industry is still very early - no option may be definitively "correct" or "wrong."

## Market Impact

GR00T N1 positions NVIDIA as a "total solution provider" in robotics:
- Competes with Google's "robotics Android" vision
- Creates alternative ecosystem to purely academic open-source
- Leverages hardware advantage to build software stack

## See Also

- [[nvidia]] - Parent company
- [[vla-model]] - VLA fundamentals
- [[robotics-vla-models]] - Research hub
- [[genesis-robotics]] - Competing simulation platform
- [[google-deepmind-robotics]] - Competing ecosystem