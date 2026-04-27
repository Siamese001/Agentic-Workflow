# Wave E — ADG Semantic Card Projection

**Tier**: T3 (cross-layer: tools/ingestion + agentic_core L3/L4 retrieval)
**ADG Snapshot**: 04222026_2022 (73,705 nodes, 546,404 edges) — healthy
**Parent Assessment**: `.windsurf/plans/adg-chromadb-retrieval-assessment-8a3f2b.md`
**Status**: Done (µW0–µW7 landed; three scope items deferred via DEFERRED_SCOPE markers)
**Execution Mode**: Micro-waves, one commit + push per µW

## Goal

Implement the **ADG → semantic card projection** layer that the 2026-04-06 assessment
recommended as the Option C foundation. Replace the raw-edge-bulk ingest
(`tools/ingestion/ingest_adg.py`, ~624k edge documents — the documented anti-pattern)
with a curated symbol / path / violation / hotspot card emitter that uses the already-built
materialized views (`mv_hotspot_centrality`, `mv_gateway_bypass_paths`,
`mv_graph_chokepoint_bridges`, `mv_dependency_cone_risk`, `mv_debt_concentration_hotspots`,
`mv_exemptions_near_critical_paths`) as truth.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| µW0 | E.0 | Plan file (this file) | 1k | — | Done | File exists at SSOT path |
| µW1 | E.1 | Card types + projector skeleton (`tools/ingestion/adg_cards/__init__.py`, `types.py`) | 2k | ADG SQLite readable | Done | Module imports clean; `SymbolCard`, `PathCard`, `ViolationCard`, `HotspotCard` dataclasses exist |
| µW2 | E.2 | Symbol + Hotspot emitters (`symbol_emitter.py`, `hotspot_emitter.py`) | 5k | `mv_hotspot_centrality` populated | Done | Emitters return non-empty iterables against live snapshot |
| µW3 | E.3 | Violation + Path emitters (`violation_emitter.py`, `path_emitter.py`) | 5k | `violations`, `mv_gateway_bypass_paths`, `mv_graph_chokepoint_bridges` populated | Done | Emitters return non-empty iterables against live snapshot |
| µW4 | E.4 | CLI entrypoint `tools/ingestion/project_adg_cards.py` + deprecation banner on `ingest_adg.py` | 3k | Card emitters stable | Done | CLI runs dry-run; prints counts per card kind |
| µW5 | E.5 | Unit tests for card shape + metadata invariants | 3k | pytest working | Done | 12/12 card tests pass |
| µW6 | E.6 | Stamp `adg_node_id` on code-chunk metadata in `ingest_code.py` | 2k | ADG resolved_path index available | Done | 10/10 chunks in live smoke resolve; 5/5 resolver tests pass |
| µW7 | E.7 | Writeback (memory entity + Notion row) | 1k | — | Done | Memory + Notion receipts present |

## Writeback Receipts

WRITEBACK: memory entities=`ProceduralPattern:ADGSemanticCardProjection`, `Project:WaveE-ADG-Card-Projection`
WRITEBACK: notion page=`https://www.notion.so/P3-Wave-E-E-0-E-7-ADG-semantic-card-projection-complete-34b27693f55c8167b376f83bbc0f5626` (Wave/Phase Convergence, Status=Done)

DECISION_CAPTURED: type=architecture_choice, repo_area=tools/ingestion/adg_cards, selected=Hybrid Graph+Vector via curated semantic cards, outcome=executed

**Total est tokens**: ~22k (well below single-session budget)

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| E.0 | Plan | `.windsurf/plans/wave-e-adg-card-projection-2df148.md` | — | 1k | Done |
| E.1 | Card types | `tools/ingestion/adg_cards/__init__.py`, `types.py` | Dataclass field minimality | 2k | Todo |
| E.2 | Symbol+Hotspot | `tools/ingestion/adg_cards/symbol_emitter.py`, `hotspot_emitter.py` | MV column drift | 5k | Todo |
| E.3 | Violation+Path | `tools/ingestion/adg_cards/violation_emitter.py`, `path_emitter.py` | MV absence on some snapshots | 5k | Todo |
| E.4 | CLI + deprecation | `tools/ingestion/project_adg_cards.py`, `tools/ingestion/ingest_adg.py` | Back-compat note | 3k | Todo |
| E.5 | Tests | `tests/unit/tools/ingestion/test_adg_cards.py` | MV availability in CI | 3k | Todo |
| E.6 | adg_node_id stamp | `tools/ingestion/ingest_code.py` | Path-to-node resolution perf | 2k | Todo |
| E.7 | Writeback | Memory + Notion | — | 1k | Todo |

## ADG_GRAPH_LAYER_EVIDENCE

Primary graph-layer drivers for this work (constitutional §22):
- **Materialized views (≥3)**: `mv_hotspot_centrality` (hotspot + symbol cards), `mv_gateway_bypass_paths` (path cards), `mv_graph_chokepoint_bridges` (path cards), `mv_dependency_cone_risk` (hotspot boost), `mv_debt_concentration_hotspots` (hotspot), `mv_exemptions_near_critical_paths` (violation context)
- **Semantic edges**: `flows_to`, `reads_from`, `writes_to`, `emits_side_effect`, `controls_flow`, `resolves_callsite` — surfaced in symbol-card neighbor summaries and path-card hop descriptions
- **P-views cross-ref**: `v_p0_apps_direct_infra`, `v_p0_write_bypass_uwg`, `v_p1_mis_layered_infra` — consumed by violation cards to pre-classify severity

## ADG_HOTSPOT_REPORT

Not a refactor of existing hot code — this is a new ingestion module. Hotspot archetype applies to *output* cards:
- Every `HotspotCard` row classified into `{CENTRAL_DEPENDENCY, ORCHESTRATOR, STATE_NODE, SAFETY_GATEKEEPER}` based on fan-in/fan-out/layer.
- Surface intersection (5 ADG Surfaces: Execution, Write, Security, State, Observability) carried as a metadata field on every card.

## Commit Protocol

Per user directive: **each µW gets its own commit and push.**
- Commit message format: `wave-e µW<n>: <scope>`
- Only stage files authored in this work; unrelated dirty tree preserved.
- After each push, update this plan's Status column.

## Out of Scope (deferred)

- HybridSearchEngine wiring (ADG-seed + ADG-rerank) — depends on cards existing and deserves its own plan after E.6 lands.
- ADG Coverage Hardening Phase 0 from the parent assessment — orthogonal governance work.
- Deprecating `repo_adg_graph` collection deletion — this plan only adds the deprecation banner; removal is a later wave after benchmark proves cards dominate.

DEFERRED_SCOPE: plan=wave-e-adg-card-projection-2df148 wave=E phase=E.F1 layer=L3 fan_in=0 surface=Execution coverage_gap_pct=100.0 est_tokens=6000 reason=hybrid search engine ADG seed and rerank wiring
DEFERRED_SCOPE: plan=wave-e-adg-card-projection-2df148 wave=E phase=E.F2 layer=L1 fan_in=0 surface=None coverage_gap_pct=99.7 est_tokens=8000 reason=ADG coverage hardening phase 0 from parent assessment
DEFERRED_SCOPE: plan=wave-e-adg-card-projection-2df148 wave=E phase=E.F3 layer=L4 fan_in=0 surface=State coverage_gap_pct=50.0 est_tokens=4000 reason=retire repo_adg_graph edge bulk collection after benchmark
