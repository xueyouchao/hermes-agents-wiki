---
title: OpenVLA
created: 2026-04-20
updated: 2026-04-20
type: entity
tags: [model, robotics, vla, open-source, stanford, berkeley]
sources: [raw/articles/sv101-physical-intelligence.md]
---

# OpenVLA

OpenVLA is an open-source Vision-Language-Action (VLA) model developed by Stanford and Berkeley researchers, known for achieving superior performance with significantly fewer parameters than proprietary alternatives.

## Key Achievement

**June 2024**: OpenVLA (7B parameters) achieved a 16.5% higher success rate than Google's RT-2-X (55B parameters) across 29 robotic manipulation tasks.

## Architecture

OpenVLA employs a **dual visual encoder** design:

### Two Visual Encoders
1. **DINOv2**: Spatial relationship understanding
2. **SigLIP**: Semantic and common-sense understanding

This "two eyes" approach allows:
- Physical isolation of spatial and semantic information
- Independent optimization of each information type
- Unified decision-making through the language model

### Language Model Integration
- Uses open-source **Llama2** as the "brain"
- Fuses spatial and semantic information for instruction following and reasoning

### Design Philosophy
Unlike Google's RT-2-X which uses a single visual encoder (one "smart person doing everything"), OpenVLA functions as a three-person team:
- Each visual encoder specializes in its domain
- Team coordination produces better results than solo effort

This validates that in embodied intelligence, "bigger" doesn't always mean "smarter."

## Training Optimizations

OpenVLA achieved its results through:
1. **Data Advantage**: Leveraged [[open-x-embodiment]] dataset
2. **Architecture Design**: Dual encoder approach
3. **Training Strategy**: Optimized action representation and training procedures

## Open Source Contribution

OpenVLA fully公开 (publicly released):
- Model weights
- Training scripts
- Complete code

This openness enabled:
- Subsequent optimization by the community
- Inference acceleration research
- Fine-tuning adaptations

## Research Team

Development team spans multiple institutions:
- Stanford University
- UC Berkeley
- Toyota Research Institute
- Google DeepMind
- [[physical-intelligence]]
- MIT

This collaboration demonstrates that open-source models can outperform well-resourced closed systems through innovative design.

## Significance

OpenVLA's victory represents a classic open-source success story:
- Innovative approach achieving "small to win big"
- Subsequent technical community work builds on this foundation
- Proves in embodied AI that data + architecture + training strategy combined matter more than pure scale

## See Also

- [[vla-model]] - VLA fundamentals
- [[octo]] - Related open-source model
- [[open-x-embodiment]] - Training data
- [[chelsea-finn]] - Key researcher
- [[robotics-vla-models]] - Research hub