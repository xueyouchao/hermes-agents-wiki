---
title: 3DGS, Spark, fVDB & NVIDIA Spatial AI — Relations & Business Map
created: 2026-04-24
updated: 2026-04-24
type: research
tags: [3dgs, gaussian-splatting, spark, fvdb, nvidia, spatial-ai, webgl, openusd, business-opportunities, digital-twin, splat-streaming]
sources: [
  https://github.com/sparkjsdev/spark,
  https://sparkjs.dev/docs/,
  research/nvidia/fvdb-overview.md,
  research/nvidia/fvdb-architecture.md,
  research/nvidia/fvdb-microservices.md,
  research/nvidia/nvidia-ai-apps-rtx-pcs-overview.md,
  concepts/3dgs/3d-gaussian-splatting.md,
  entities/3dgs/splat-webgl.md,
  entities/3dgs/awesome-3dgs.md,
  raw/articles/nvidia-ace-for-games-overview.md,
  https://developer.nvidia.com/blog/building-spatial-intelligence-from-real-world-3d-data-using-deep-learning-framework-fvdb/,
  https://research.nvidia.com/publication/2024-07_fvdb-deep-learning-framework-sparse-large-scale-and-high-performance-spatial
]
---

# 3DGS, Spark, fVDB & NVIDIA Spatial AI — Relations & Business Map

> A deep-research synthesis mapping how four technology layers — 3D Gaussian Splatting (representation), Spark (web runtime), fVDB (spatial AI backend), and NVIDIA ACE/RTX (compute + agentic AI) — converge into a single deployable spatial media stack and what business models it unlocks.

## Technology Layer Model

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4 — Interactive & Intelligent (NVIDIA ACE + LLMs)       │
│  NPC behavior, AI docents, conversational avatars, local AI    │
│  on 100M+ RTX PCs via TensorRT / llama.cpp / Audio2Face       │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3 — Web Delivery & Consumption (Spark 2.0 / Splats)    │
│  Browser-native 3DGS renderer (WebGL2, 98%+ reach). LoD       │
│  streaming via .RAD format. Dyno shader graphs. AR/VR (WebXR).│
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2 — Spatial AI Backend (NVIDIA fVDB)                    │
│  Sparse volumetric deep learning. Large-scale NeRFs (NeRF-XL),│
│  mesh generation, physics super-resolution. OpenUSD/Omniverse. │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1 — Data & Representation (3DGS + Sparse-view / 4D)   │
│  2-5 photos → photorealistic 3D (FatesGS, LongSplat). 4D GS   │
│  (GaussianHead, dynamic scenes). SPZ/SPZ compression.         │
└─────────────────────────────────────────────────────────────────┘
```

## Layer-by-Layer Relation Map

### LAYER 1 → LAYER 2: From Captured Scene to Trainable Spatial Data

- **3DGS outputs** (point clouds, splat files) are the native input to **fVDB Mesh Generation NIM**: point clouds → OpenUSD meshes at scale.
- **Sparse-view 3DGS** (COLMAP-free methods) lowers data-collection cost to **2-5 photos**, making fVDB pipelines accessible to non-specialists.
- **4D / Dynamic 3DGS** adds temporal channels; fVDB’s sparse convolution operators can process these volumetric-plus-time structures.
- **Compression**: SPZ format reduces splat file sizes to video-like ranges, making them viable for fVDB streaming microservices.

### LAYER 2 → LAYER 3: From Industry-Scale Generation to Consumer Reach

- **fVDB NeRF-XL** generates multi-square-kilometer radiance fields. Without a web runtime these stay trapped in Omniverse. **Spark 2.0’s ExtSplats + LoD streaming** is the only known open-source runtime that can display city-scale scenes on a phone.
- **OpenUSD** is the lingua franca between fVDB and Spark: fVDB outputs OpenUSD; Spark imports via standard 3D loaders (THREE.js → SplatMesh).
- **fVDB Physics Super-Res** gives physically accurate volumetric enhancement. Combined with Spark’s real-time rendering, this enables interactive simulation previews in a browser.

### LAYER 3 → LAYER 4: From Static Content to Living Worlds

- **Spark 2.0** is a *programmable* splat engine. **Dyno shader graphs** allow real-time modifications: color, opacity, displacement, particle effects, skeletal animation.
- **NVIDIA ACE** provides the conversational + facial animation stack (Audio2Face, NeMo SLM, Riva ASR/TTS). When embedded in a Spark scene, ACE characters become first-class SplatMesh objects that sort correctly against the 3DGS background.
- **Local LLM inference** (llama.cpp on RTX, up to 3352 TOPS) means the AI “inhabitant” does not require cloud API costs or latency. A museum kiosk, a real-estate open-house tablet, or a car-dealer showroom can run the full stack offline.

### Cross-Layer Feedback Loops

| Feedback Loop | How it works | Why it matters |
|---|---|---|
| **User interaction → scene update** | Spark viewer captures click/orbit data; fVDB pipeline regenerates a sub-volume (e.g., a damaged wall section); updated .RAD chunk streams back | Real-time collaborative editing at scale |
| **AI agent → procedural splat** | ACE NPC decides to sit; Dyno graph procedurally modifies the chair-splat subset to show occupied state | Worlds that react to inhabitants |
| **Sparse capture → compressed asset → LoD stream** | Phone captures 3 photos → backend generates SPZ → LoD tree built → .RAD streams to any device | Zero-friction content pipeline |
| **City-scale NeRF → local LoD paging** | fVDB NeRF-XL outputs massive scene → Spark SplatPager fetches only visible chunks | Enterprise-scale spatial apps on consumer hardware |

## Key Interfaces & Standards

| Interface | Format / Protocol | Role in Stack |
|---|---|---|
| **SPZ** | Compressed binary splat | Lightweight interchange between capture tool and web viewer |
| **PLY (compressed)** | Point cloud with Gaussian attributes | Training input, archival format |
| **.RAD** | Spark 2.0 LoD streaming format | Progressive, HTTP Range-request delivery of huge scenes |
| **OpenUSD** | Universal Scene Description | Bridge between fVDB NIMs, Omniverse, game engines, and Spark |
| **WebGL2** | Browser GPU API | Spark’s rendering target; 98%+ device coverage |
| **Dyno JS → GLSL** | Spark’s shader graph DSL | Procedural / animated splat effects compiled to GPU |
| **NVIDIA NIM REST API** | JSON / HTTP | fVDB microservices callable from any backend |

## Competitive Landscape Context

| Competitor / Alternative | Capability Gap vs. Full Stack | Notes |
|---|---|---|
| **antimatter15/splat** (splat-webgl) | Single static object; no LoD, animation, or mesh fusion. | Spark supersedes this entirely. Your wiki already notes Spark as “advanced alternative.” |
| **Luma AI / Polycam** | Cloud capture → cloud viewer. Vendor lock-in, no local AI agents. | Full stack gives you self-hosted equivalent + AI agent layer. |
| **Google / Apple photogrammetry** | Mesh-based, not radiance fields. No real-time view-dependent rendering. | 3DGS quality + real-time performance wins. |
| **NeRFStudio / Nerfstudio** | Training pipeline, not a deployable web runtime. | Complements, but does not replace, Spark for delivery. |
| **Unreal Engine Nanite/Lumen** | Superior traditional graphics, but not 3DGS-native. Heavy client, not browser-first. | Spark targets instant web load; UE5 targets installed AAA games. Different market. |

## Business Opportunity Vectors

Eight distinct vectors were derived from this relation map. See the companion document in the `ideas` private repository for full business plans: [[3dgs-business-plan-2026 — external]]

1. **SplatStream** — 3D product photography SaaS (e-commerce)
2. **RoomSplat** — Virtual staging / interior design (real estate)
3. **CityScope AI** — City-scale digital twin (enterprise / gov)
4. **LiveAvatar** — Volumetric telepresence (sales/support)
5. **GaussianStage** — Browser-based virtual production studio
6. **DocentAI** — AI-guided cultural heritage tourism
7. **SpatialSearch** — 3D scene understanding API (construction/insurance)
8. **DynoAds** — Programmable 3D advertising unit network

## Strategic Conclusion

The window for a **web-first spatial media platform** is open because:

1. **Creation** is now accessible (sparse-view 3DGS, 2-5 photos)
2. **Scale** is API-accessible (fVDB NeRF-XL NIM for city-scale)
3. **Delivery** is universal (Spark 2.0 WebGL2, mobile-capable, LoD streaming)
4. **Intelligence** is local and affordable (RTX AI PCs, ACE, llama.cpp)

Previously, any one of these was a research project. In 2026, they compose into a deployable production stack. The companies that win will be the ones that **own the delivery format** (Spark/.RAD equivalents), **own the content pipeline**, or **own the vertical application** (real estate, tourism, digital twins).

## See Also

- [[3d-gaussian-splatting]] — Core concept of 3DGS
- [[splat-webgl]] — Earlier WebGL viewer (superseded by Spark)
- [[awesome-3dgs]] — Paper/implementation index
- [[fvdb-overview]] — NVIDIA fVDB framework
- [[fvdb-architecture]] — fVDB system architecture
- [[fvdb-microservices]] — NIM deployment patterns
- [[nvidia-ace-for-games]] — AI character pipeline
- [[nvidia-ai-apps-rtx-pcs-overview]] — RTX AI ecosystem
- [[interiorgs-business-cases]] — Prior InteriorGS market analysis
- [[blueprint-collaborative-3dgs]] — AWS collaborative editing blueprint

## References

- sparkjsdev/spark GitHub repository (479+ commits, 2.7k stars, Rust/WASM core)
- Spark 2.0 documentation: System Design, LoD, Procedural Splats, Performance Tuning
- NVIDIA fVDB research paper (2024) and developer blog
- NVIDIA ACE for Games overview and GDC demonstrations
- NVIDIA AI Apps for RTX PCs SDK catalog
