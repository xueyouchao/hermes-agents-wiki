---                            
title: Splat WebGL Viewer
created: 2026-04-16
updated: 2026-04-16
type: entity
tags: [3dgs, gaussian-splatting, webgl, viewer, javascript, browser]                            
sources: [raw/repos/splat-webgl.md]                            
---                        
# Splat: WebGL 3D Gaussian Splatting Viewer
A pure JavaScript/WebGL implementation of a real-time renderer for 3D Gaussian Splatting. Runs entirely in the browser with no external dependencies.
## Overview
| Attribute | Value | |-----------|-------| | Stars | ~3,800+ | | Language | JavaScript (WebGL 1.0) | | License | Custom | | GitNexus | 40 symbols, 92 edges, 4 clusters, 2 flows |
## Key Features### Browser-Based Rendering- **No dependencies:** Pure JavaScript, just open index.html
- **WebGL 1.0:** Uses extensions, works in most browsers- **Progressive loading:** View model before all splats load- **Drag & drop:** Load custom .splat files### Controls
| Input | Action | |-------|--------| | Arrow keys | Move forward/back/strafe | | WASD | Camera rotation | | Mouse drag | Orbit | | Scroll | Zoom/move | | 0-9 | Switch camera views | | Drag .ply | Convert to .splat |### Technical Notes- Splat sorting done asynchronously in WebWorker- Does NOT support view-dependent SH effects (to reduce file size)- Uses weighted blended order-independent transparency- Alternative: [Spark](https://github.com/sparkjsdev/spot) for advanced features (THREE.js, animations)## File Format Support- **.splat:** Main format (compact binary)- **.ply:** Point clouds (auto-converts to .splat)- **cameras.json:** Camera definitions- URL parameter loading for remote files## Demo Examples- [Try it online](https://antimatter15.com/splat/)## Related Projects
- [[gaussian-impl]] — Reference implementation (generates .splat files)- [[awesome-3dgs]] — More resources- [Spark](https://github.com/sparkjsdev/spot) — Advanced THREE.js renderer## References- [GitHub](https://github.com/antimatter15/splat)- [Live Demo](https://antimatter15.com/splat/)- [Original 3DGS Paper](https://repo-sam.inria.fr/fungraph/3d-gaussian--splatting/)