---
title: Physical Intelligence
created: 2026-04-20
updated: 2026-04-20
type: entity
tags: [company, robotics, embodied-ai, vla, pi, physical-intelligence]
sources: [raw/articles/sv101-physical-intelligence.md]
---

# Physical Intelligence (PI)

Physical Intelligence (PI) is a robotics AI company developing the π₀ family of VLA models, known for pushing the boundaries of continuous control and high-frequency action generation.

## Company Overview

- **Founded**: 2024
- **Headquarters**: San Francisco Bay Area
- **Funding**: $1B+ (multiple rounds)
  - Initial funding: $10B+ valuation
  - November 2024: $400M
  - November 2025: $600M
  - **Total Valuation**: $5.6B

**Investors**: Jeff Bezos, OpenAI, Sequoia Capital, Khosla Ventures, Lachy Groom, Anduril

## Key Models

### π₀ (pi-zero)
- **Parameters**: Billions of level
- **Control Frequency**: ~50Hz (50 updates per second)
- **Architecture**: Flow Matching for continuous joint trajectory generation
- **Innovation**: Outputs smooth control signals instead of discrete tokens
- **Capabilities**: Paper folding, playing poker cards - tasks requiring extreme precision
- **Data**: More training data than all previous Google Research efforts combined

### π₀.5
- **Capability**: Zero-shot adaptation to unseen environments
- **Test**: Deployed on mobile robots in unfamiliar homes
- **Observation**: Shows human-like ability to interact with unknown environments

## Technical Approach

π₀ uses **Flow Matching** instead of traditional language token prediction:
- Generates continuous joint trajectories directly
- Outputs ~1 second of planned actions (50 steps at 50Hz)
- Enables smoother motion with reduced jitter and latency
- Better suited for folding laundry, grasping柔性 objects, manipulating small parts

## Open Source: OpenPI Project

PI released model weights and inference code through the **OpenPI** project, allowing:
- Research community reproduction and extension
- Deployment on various robot platforms
- Community contributions and improvements

**Note**: Training pipeline and proprietary data (tens of thousands of hours) remain closed.

## Founding Team - "Avengers League"

The PI founding team comprises key figures from Google's robot foundation model efforts:

| Member | Background |
|--------|------------|
| [[chelsea-finn]] | Stanford professor, co-founder; key RT series researcher |
| [[sergey-levine]] | Berkeley professor, co-founder, chief scientist; reinforcement learning pioneer |
| Karol Hausman | Google DeepMind senior research scientist; core author of RT-1, RT-2, SayCan |
| Brian Ichter | Google Brain; deep contributor to RT series development |

## Strategy Analysis

PI's open-source approach is characterized as "most calculating":

1. **Standard Setting**: By open-sourcing, PI becomes the de facto standard; every use consolidates its ecosystem position
2. **Talent Attraction**: OpenPI GitHub becomes the hottest robotics project - more effective than recruitment ads
3. **Data Flywheel**: Community usage generates improvements and data that flow back to PI, strengthening next-generation models

This represents a "open-source funnel, closed-source monetization" strategy:
- Open model attracts developers into ecosystem
- Closed training data and capabilities maintain competitive advantage
- Best versions available exclusively through PI

## See Also

- [[vla-model]] - Vision-Language-Action fundamentals
- [[physical-intelligence]] - This entity
- [[chelsea-finn]] - Co-founder profile
- [[sergey-levine]] - Co-founder profile
- [[open-x-embodiment]] - Training data resource