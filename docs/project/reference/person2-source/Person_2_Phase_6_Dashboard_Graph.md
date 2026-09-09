# Phase 6 - Dashboard and Knowledge Graph Visualization

## Plan

Connect dashboard metrics and recent reviews to backend history data, then connect the graph page to graph nodes and edges returned for a selected migration.

## Implementation

Connected the Dashboard and Knowledge Graph pages to live endpoints:

- Dashboard loads `GET /history` and `GET /stats` with Phase 1 mock fallback if the backend is unavailable.
- Dashboard cards now show saved analysis count, average score, and critical analysis count.
- Recent dashboard rows link to live history IDs.
- History is reused as the source of truth for recent reviews.
- Graph loads `GET /graph/{migration_id}` for the latest analyzed migration.
- Graph node labels, types, and relationship labels come from the backend graph response.
- The graph page retains a mock preview when no live analysis exists.
- Replaced the static positioned-card preview with an interactive React Flow canvas including draggable nodes, zoom/pan controls, minimap, labeled edges, and animated risk edges.

## Review checklist

- Dashboard metrics are calculated from backend data.
- Recent reviews link to real saved analyses.
- Graph nodes and edges come from the selected migration.
- Relationship labels match the report.
- Empty history and empty graph states work.

## Issues found

The initial graph preview used fixed labels and did not consume real node or edge data. Dashboard metrics were also hard-coded. The first live graph implementation still used static cards rather than a graph interaction library.

## Fixes applied

Replaced hard-coded dashboard values with API-backed values and replaced fixed graph content with live graph data plus a safe mock fallback. Added `@xyflow/react` for actual graph interaction and edge rendering.

## Evidence

The integration smoke test returned one saved analysis, stats with count/average/critical values, and a graph with 10 nodes and 8 edges. Frontend build passes with 189 modules transformed after React Flow integration.

## Sign-off status

Complete. Dashboard and graph data flows are connected, and the graph is interactive.
