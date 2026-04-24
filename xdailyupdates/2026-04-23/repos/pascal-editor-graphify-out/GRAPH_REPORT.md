# Graph Report - pascal-editor  (2026-04-23)

## Corpus Check
- 308 files · ~563,014 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1293 nodes · 1811 edges · 36 communities detected
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 284 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 64|Community 64]]

## God Nodes (most connected - your core abstractions)
1. `GET()` - 67 edges
2. `SpatialGridManager` - 20 edges
3. `MergedOutlineNode` - 13 edges
4. `getWallCurveFrameAt()` - 13 edges
5. `generateExtrudedWall()` - 13 edges
6. `SpatialGrid` - 12 edges
7. `isCurvedWall()` - 12 edges
8. `handleWindowPointerMove()` - 11 edges
9. `getMaterialsForWall()` - 10 edges
10. `snapWallDraftPoint()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `createNodesAction()` --calls--> `GET()`  [INFERRED]
  packages/core/src/store/actions/node-actions.ts → apps/editor/app/api/health/route.ts
- `updateNodesAction()` --calls--> `GET()`  [INFERRED]
  packages/core/src/store/actions/node-actions.ts → apps/editor/app/api/health/route.ts
- `getTexture()` --calls--> `GET()`  [INFERRED]
  packages/viewer/src/lib/materials.ts → apps/editor/app/api/health/route.ts
- `getPresetTexture()` --calls--> `GET()`  [INFERRED]
  packages/viewer/src/lib/materials.ts → apps/editor/app/api/health/route.ts
- `loadPresetTexture()` --calls--> `GET()`  [INFERRED]
  packages/viewer/src/lib/materials.ts → apps/editor/app/api/health/route.ts

## Communities

### Community 0 - "Community 0"
Cohesion: 0.02
Nodes (92): adaptPanelRectToBounds(), addVectorToSvgPoint(), appendUniquePlanPoint(), buildCursorUrl(), buildFloorplanStairArrow(), buildFloorplanStairEntry(), buildGridPath(), buildGuideResizeDraft() (+84 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (25): resolveLevelObject(), hasWallChildOverlap(), getScaledDimensions(), scoreRegistration(), checkCanPlace(), resolveLevelNode(), GET(), playSFX() (+17 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (59): CurveFenceTool(), CurveWallTool(), applyFenceUVs(), createFenceCurveSpanParts(), createFencePartGeometry(), createFenceParts(), createStraightFenceSpanPart(), generateFenceGeometry() (+51 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (49): CeilingSystem(), ensureUv2Attribute(), generateCeilingGeometry(), updateCeilingGeometry(), addBox(), updateDoorMesh(), DoorTool(), updateFencePreview() (+41 more)

### Community 4 - "Community 4"
Cohesion: 0.08
Nodes (33): getCatalogMaterialById(), getLibraryMaterialIdFromRef(), getMaterialPresetByRef(), toLibraryMaterialRef(), handleCatalogSelect(), areWallsCollinearAcrossPoint(), areWallStylesCompatible(), buildMergedWallAttachmentUpdates() (+25 more)

### Community 5 - "Community 5"
Cohesion: 0.1
Nodes (36): handleKeyDown(), handleWheel(), getAdjustedStep(), handleKeyDown(), handleWheel(), stepPrecision(), buildUnionPolygonsFromRects(), clamp() (+28 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (25): getDefaultCatalogItem(), initializeEditorRuntime(), load(), applySceneGraphToEditor(), getDefaultLevelIdForBuilding(), getEditorUiStateForRestoredSelection(), getRestoredSelectionForScene(), getSelectionStorageKey() (+17 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (28): resolveMaterial(), applyMaterialMapProperties(), applyMaterialPresetTextures(), applyMaterialPresetToMaterials(), applyTextureProperties(), createMaterial(), createMaterialFromPreset(), createMaterialFromPresetRef() (+20 more)

### Community 8 - "Community 8"
Cohesion: 0.07
Nodes (26): calculateSnapPoint(), commitCeilingDrawing(), onCancel(), onGridClick(), onGridDoubleClick(), onGridMove(), applyPreview(), getPolygonCenter() (+18 more)

### Community 9 - "Community 9"
Cohesion: 0.12
Nodes (29): createFenceOnCurrentLevel(), distanceSquared(), findFenceSnapTarget(), projectPointOntoSegment(), snapFenceDraftPoint(), buildAttachmentMigrationPlan(), createWallOnCurrentLevel(), distanceSquared() (+21 more)

### Community 10 - "Community 10"
Cohesion: 0.11
Nodes (23): bboxOverlapArea(), buildSpace(), dedupeSequentialPoints(), detectSpacesForLevel(), detectSpacesFromWalls(), distanceToSegment(), extractRoomPolygons(), getDirectedWallBoundaryPoints() (+15 more)

### Community 11 - "Community 11"
Cohesion: 0.12
Nodes (20): pauseSceneHistory(), resumeSceneHistory(), applyNodePreview(), applyPreview(), getLinkedFenceSnapshots(), getLinkedFenceUpdates(), onCancel(), onGridClick() (+12 more)

### Community 12 - "Community 12"
Cohesion: 0.08
Nodes (9): ErrorBoundary, resetSceneHistoryPauseDepth(), getLevelHeight(), snapLevelsToTruePositions(), clearMaterialCache(), makeGroupTargets(), MergedOutlineNode, resetEditorInteractionState() (+1 more)

### Community 13 - "Community 13"
Cohesion: 0.15
Nodes (21): collectNodeIdsInBounds(), cross(), getNodeWorldXZ(), getSnappedGridPosition(), haveSameIds(), objectBoundsIntersectsBounds(), onCanvasPointerDown(), onCanvasPointerUp() (+13 more)

### Community 14 - "Community 14"
Cohesion: 0.13
Nodes (14): createHighlightedMaterial(), createHighlightedMaterials(), disposeHighlightedMaterials(), expandPolygon(), getEventObject(), getIntersectionMaterialIndex(), isNodeInCurrentLevel(), isNodeInZone() (+6 more)

### Community 15 - "Community 15"
Cohesion: 0.1
Nodes (6): handleAddZone(), handleClick(), handleColorChange(), handleDelete(), handleDoubleClick(), focusTreeNode()

### Community 16 - "Community 16"
Cohesion: 0.12
Nodes (10): BuildingRenderer(), DoorRenderer(), FenceRenderer(), BrokenItemFallback(), RoofSegmentRenderer(), useRegistry(), SlabRenderer(), StairSegmentRenderer() (+2 more)

### Community 17 - "Community 17"
Cohesion: 0.24
Nodes (12): dedupePolygonPoints(), insetPolygonFromCentroid(), pointLineDistance(), simplifyClosedPolygon(), simplifyPolyline(), ensureUv2Attribute(), generatePoolGeometry(), generatePositiveSlabGeometry() (+4 more)

### Community 19 - "Community 19"
Cohesion: 0.36
Nodes (12): getBoolean(), getEnumValue(), getFiniteNumber(), getNullableString(), getStringArray(), getVector3(), migrateNodes(), migrateRoofSurfaceMaterials() (+4 more)

### Community 20 - "Community 20"
Cohesion: 0.2
Nodes (6): ItemTool(), getInitialState(), MoveItemContent(), useDraftNode(), usePlacementCoordinator(), useSpatialQuery()

### Community 21 - "Community 21"
Cohesion: 0.2
Nodes (4): positiveModulo(), snapToGrid(), stripTransient(), isObject()

### Community 22 - "Community 22"
Cohesion: 0.25
Nodes (6): generateId(), cloneLevelSubtree(), cloneSceneGraph(), extractIdPrefix(), forkSceneGraph(), generateCollectionId()

### Community 24 - "Community 24"
Cohesion: 0.2
Nodes (2): SidebarProvider(), useIsMobile()

### Community 26 - "Community 26"
Cohesion: 0.5
Nodes (8): calculateSnapPoint(), commitZoneDrawing(), isValidPoint(), onGridClick(), onGridDoubleClick(), onGridMove(), updateLines(), updatePreview()

### Community 29 - "Community 29"
Cohesion: 0.38
Nodes (3): getLinkedWallSnapshots(), MoveWallTool(), samePoint()

### Community 31 - "Community 31"
Cohesion: 0.33
Nodes (2): loadAssetUrl(), resolveAssetUrl()

### Community 33 - "Community 33"
Cohesion: 0.47
Nodes (3): getLinkedFenceSnapshots(), MoveFenceTool(), samePoint()

### Community 35 - "Community 35"
Cohesion: 0.33
Nodes (2): PresetThumbnailGenerator(), usePresetsAdapter()

### Community 37 - "Community 37"
Cohesion: 0.6
Nodes (3): buildSceneGraphValue(), getChildIdsFromNode(), isSceneNode()

### Community 43 - "Community 43"
Cohesion: 0.83
Nodes (3): refreshSceneAfterHistoryJump(), runRedo(), runUndo()

### Community 47 - "Community 47"
Cohesion: 0.5
Nodes (1): Card()

### Community 49 - "Community 49"
Cohesion: 0.5
Nodes (1): ZoneSystem()

### Community 53 - "Community 53"
Cohesion: 0.5
Nodes (2): Grid(), useGridEvents()

### Community 57 - "Community 57"
Cohesion: 0.67
Nodes (1): cn()

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (2): deleteLevelWithFallbackSelection(), getAdjacentLevelIdForDeletion()

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (2): getIsActive(), handleClick()

## Knowledge Gaps
- **Thin community `Community 24`** (10 nodes): `sidebar.tsx`, `use-mobile.ts`, `cn()`, `SidebarHeader()`, `SidebarInset()`, `SidebarProvider()`, `SidebarResizer()`, `SidebarSeparator()`, `useSidebar()`, `useIsMobile()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (6 nodes): `loadAssetUrl()`, `saveAsset()`, `resolveAssetUrl()`, `resolveCdnUrl()`, `asset-storage.ts`, `asset-url.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (6 nodes): `preset-thumbnail-generator.tsx`, `presets-context.tsx`, `PresetThumbnailGenerator()`, `PRESETS_KEY()`, `PresetsProvider()`, `usePresetsAdapter()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (4 nodes): `Card()`, `CardTitle()`, `card.tsx`, `card.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (4 nodes): `zone-system.tsx`, `zone-system.tsx`, `noopRaycast()`, `ZoneSystem()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (4 nodes): `Grid()`, `grid.tsx`, `use-grid-events.ts`, `useGridEvents()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (3 nodes): `utils.ts`, `utils.ts`, `cn()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (3 nodes): `deleteLevelWithFallbackSelection()`, `getAdjacentLevelIdForDeletion()`, `level-selection.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (3 nodes): `getIsActive()`, `handleClick()`, `control-modes.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GET()` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 4`, `Community 37`, `Community 5`, `Community 7`, `Community 8`, `Community 10`, `Community 12`, `Community 13`, `Community 14`, `Community 22`, `Community 31`?**
  _High betweenness centrality (0.248) - this node is a cross-community bridge._
- **Why does `handleWindowPointerMove()` connect `Community 2` to `Community 0`, `Community 9`, `Community 1`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `markToolCancelConsumed()` connect `Community 8` to `Community 11`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 66 inferred relationships involving `GET()` (e.g. with `getTexture()` and `getPresetTexture()`) actually correct?**
  _`GET()` has 66 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `getWallCurveFrameAt()` (e.g. with `findFenceSnapTarget()` and `getFencePointAt()`) actually correct?**
  _`getWallCurveFrameAt()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `generateExtrudedWall()` (e.g. with `getWallThickness()` and `getWallMiterBoundaryPoints()`) actually correct?**
  _`generateExtrudedWall()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.02 - nodes in this community are weakly interconnected._