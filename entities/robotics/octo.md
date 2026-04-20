---
title: Octo
created: 2026-04-20
updated: 2026-04-20
type: entity
tags: [model, robotics, vla, open-source, universal-policy]
sources: [raw/articles/sv101-physical-intelligence.md]
---

# Octo

Octo is an open-source universal robot policy model developed by Berkeley and Stanford researchers, designed for broad generalization across robot platforms and scenarios.

## Position

If OpenVLA represents "scale-oriented open-source," Octo represents "popularization-oriented open-source."

## Technical Design

- **Parameters**: Tens of millions (much smaller than OpenVLA's 7B)
- **Architecture**: Transformer-based diffusion policy model
- **Core Philosophy**: Flexibility and extensibility

### Key Features

1. **Multi-robot Support**: Works with various robot platforms
2. **Multiple Sensor Configurations**: Accepts diverse sensor inputs
3. **Rapid Adaptation**: Through fine-tuning, quickly adapts to new observation and action spaces
4. **Zero-Shot Generalization**: Can diffuse models to broad robots and scenarios

## Universal Robot Policy

The core challenge in robotics is **generalization**:
- Previous standard: train specific strategies for specific robots using specific datasets
- Problem: switching robots or environments requires complete retraining

Octo addresses this through a "universal robot policy" approach:
- Pre-trained on diverse robot data
- Can generalize to new robots and environments without full retraining
- Achieves zero-shot deployment across different platforms

## Comparison with OpenVLA

| Aspect | OpenVLA | Octo |
|--------|---------|------|
| Parameters | 7B | Tens of millions |
| Target | Best performance | Universal accessibility |
| Philosophy | Scale and optimization | Flexibility and adaptation |
| Use Case | Research, high performance | Rapid deployment, experimentation |

## Research Lineage

- **Institution**: UC Berkeley, Stanford
- **Supervision**: [[chelsea-finn]], [[sergey-levine]]
- **Relation**: "Same teacher, different path" - both from the same research group but with different design priorities

## Positioning in Ecosystem

Octo's value proposition is "everyone can use it":
- Provides a lightweight, rapidly adaptable base policy for the open-source community
- Lower computational requirements than OpenVLA
- Enables faster experimentation and iteration

This represents a different open-source philosophy: not pursuing maximum performance, but enabling universal access.

## See Also

- [[open-vla]] - Related model
- [[vla-model]] - VLA fundamentals
- [[robotics-vla-models]] - Research hub
- [[chelsea-finn]] - Key researcher
- [[lerobot]] - Training framework