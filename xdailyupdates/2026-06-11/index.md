---
scrape_time: "2026-06-11T21:02:45Z"
storage_state_valid: true
sources_attempted: [likes, bookmarks, timeline]
likes_count: 0
bookmarks_count: 0
timeline_count: 10
retained_count: 2
repos_extracted: 0
gitnexus: not run (no repos extracted)
graphify: not run (not installed)
errors: []
---

# X Daily Update — 2026-06-11

| # | Author | Source | Priority | GitHub | Summary |
|---|--------|--------|----------|--------|---------|
| 1 | Martin Valigursky | timeline | timeline | — | Gaussian splat relighting in PlayCanvas (proxy mesh + sky/sun/point lights on captured scenes) |
| 2 | MrNeRF | timeline | timeline | — | 1B Gaussians (1,035,804,128) streamed at 60fps in 5GB VRAM |

## Suppressed

- @Ian Curtis — Fable 5 / World Labs creative generation (repeated Fable 5 discourse; already captured 2026-06-09 and 2026-06-10)
- @BijanBowen — Fable 5 network-packet visualization (repeated Fable 5 discourse)
- @ゆきち — Fable 5 low-poly 3D model generation (repeated Fable 5 discourse)
- @FOX One — FIFA World Cup ad (not AI/tech)
- @hrdk — Stock-chart dirt-bike game (marginal, not AI/tech)
- @Starlink — Internet ad (not AI/tech)
- @How To AI — World power grid map (data viz, not core AI/tech)
- @Three.js — empty post

## 1. Gaussian Splat Relighting in PlayCanvas — @Martin Valigursky

**Source:** X.com timeline | **Author:** @Martin Valigursky | **Time:** 2026-06-11 14:46 UTC

Gaussian splats are captures frozen in time — not anymore. Experimental **relighting** of splat scenes in the PlayCanvas engine, driven by a **proxy mesh**: swap the sky, drag the sun with its soft shadows, drop in point lights — all live on a captured scene. Includes a runnable demo.

**Analysis:** This represents a significant capability jump for the [[3d-gaussian-splatting]] ecosystem. Until now, Gaussian splats were static lighting captures — baking the illumination into the scene. Relighting via a proxy mesh means the captured scene becomes editable: users can change time of day, add artificial lights, or match lighting to a compositing target. PlayCanvas (which also produces [[supersplat]]) is positioning its engine as the platform for interactive 3DGS, now extending from viewing/editing to lighting manipulation. The "proxy mesh" approach suggests a lightweight geometry representation underlying the splats, enabling shadow casting and light interaction without requiring full mesh reconstruction.

**Relevance:** Fresh 3DGS technical signal; extends the PlayCanvas/SuperSplat narrative already covered in the wiki to include relighting as a new capability dimension.

## 2. 1 Billion Gaussians at 60fps — @MrNeRF

**Source:** X.com timeline | **Author:** @MrNeRF | **Time:** 2026-06-11 11:04 UTC

1 Billion Gaussians (1,035,804,128 exactly) streaming to the viewer at 60fps (vsync) and 5GB VRAM. "There is no limit anymore to how much it can do."

**Analysis:** This is a major rendering milestone for the [[3d-gaussian-splatting]] ecosystem. One billion Gaussians is approximately two orders of magnitude beyond what [[supersplat]] recently demonstrated (24M Gaussians). The claim of 5GB VRAM at vsync-locked 60fps suggests either a streaming/LOD architecture or a novel data structure. MrNeRF (maintainer of [[awesome-3dgs]]) is a credible source for 3DGS benchmarks. The commentary about "paid pseudo influencers" appears directed at others claiming similar results without open-source verification.

**Relevance:** Major 3DGS scaling milestone; cross-references the existing MrNeRF/awesome-3dgs coverage and the broader 3DGS performance thread in the wiki.

---

**No GitHub repos extracted.** GitNexus not run (no repos). Graphify not run (not installed).

**Related wiki pages:** [[3d-gaussian-splatting]], [[supersplat]], [[awesome-3dgs]], [[splat-webgl]], [[gaussian-impl]], [[queries/2026-06-10-x-daily]], [[queries/2026-06-09-x-daily]]