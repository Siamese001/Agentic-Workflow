---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\hybrid-search-adg-seed-rerank-c58e21.md'
original_relative_path: '_archive\\2026-05\\hybrid-search-adg-seed-rerank-c58e21.md'
source_sha256: 41f57c94d99955c4cbd9f890776a14f234ebbb773fb13b14a1fc51ea78351ed6
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan — Hybrid Search Engine ADG Seed + Rerank Wiring

**Slug**: `hybrid-search-adg-seed-rerank-c58e21`
**Status**: Draft (awaiting /plan kick-off)
**Tier**: T2 (scoped, L3 retrieval-engine wiring; leverages existing cards)
**Parent marker**: `DEFERRED_SCOPE: plan=wave-e-adg-card-projection-2df148 wave=E phase=E.F1 layer=L3 fan_in=0 surface=Execution coverage_gap_pct=100.0 est_tokens=6000`
**Priority band**: **P3** (auto-scored)
**ADG baseline**: latest `adg_indexed_<ts>.sqlite` at kick-off
**ADG provenance**: `backend=sqlite, snapshot=adg_indexed_<ts>.sqlite`

---

## Intent

Wire the existing `tools/ingestion/adg_cards/` projection into `@c:/Git/Agentic-Workflow/agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py` so retrieval queries are seeded by ADG `HotspotCard`/`SymbolCard` neighbors and reranked by semantic edge proximity (`flows_to`, `resolves_callsite`). Today `hybrid_search_engine` uses only vector similarity — it ignores the pre-computed graph-aware cards produced by Wave E.

---

## ADG_GRAPH_LAYER_EVIDENCE

Primary drivers (constitutional §22):

- **Materialized views (≥3)**: `mv_hotspot_centrality` (seeds), `mv_dependency_cone_risk` (neighbor ranking), `mv_graph_chokepoint_bridges` (path-card boost), `mv_path_criticality_rollup` (rerank weight)
- **Semantic edges**: `flows_to` (direct data-flow proximity), `resolves_callsite` (call-graph proximity), `controls_flow` (branch-adjacency)
- **P-views**: `v_p0_provider_bypass` (exclude from seeds — known anti-pattern surface)

## ADG_HOTSPOT_REPORT

Hotspots recomputed at kick-off. Target archetypes for seeding:

- **CENTRAL_DEPENDENCY** (high fan-in) → high-value seeds
- **ORCHESTRATOR** (high fan-out) → related-query expanders

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|:---:|---|:---:|---|
| W1 | P1.1 | ADG seed adapter: card-query interface for hybrid engine | 1500 | adg_cards CLI stable | Todo | `adg_seed(query)` returns ≤10 SymbolCards |
| W2 | P2.1 | Wire seed adapter into `hybrid_search_engine.search()` | 1500 | W1 passes | Todo | Seeded results measurable vs. baseline |
| W3 | P3.1 | Edge-proximity rerank using semantic edges | 1500 | Edges indexed | Todo | Rerank shifts precision@10 ≥5pp on curated benchmark |
| W4 | P4.1 | Benchmark + ablation: seed-only vs. rerank-only vs. both | 1000 | Curated eval exists | Todo | Benchmark report in `docs/reports/plans/` |
| W5 | P5.1 | Writeback (memory ProceduralPattern + Notion row) | 500 | — | Todo | Receipts present |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|:---:|:---:|
| P1.1 | Seed adapter | `agentic_core/L3_orchestration/reasoning/engines/adg_seed_adapter.py` (new) | Card-query latency | 1500 | Todo |
| P2.1 | Engine wiring | `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py` | Preserve BM25 + vector paths | 1500 | Todo |
| P3.1 | Edge rerank | Same + `edge_proximity_reranker.py` (new) | Rerank-cost budget | 1500 | Todo |
| P4.1 | Benchmark | `tools/eval/retrieval_benchmark.py` (extend) | Baseline stability | 1000 | Todo |
| P5.1 | Writeback | Memory + Notion | — | 500 | Todo |

**Total est**: 6000 tokens (matches marker)

## Gap Register

| Gap | Impact | Resolution Wave |
|---|---|---|
| G-1 | ADG cards unused by hybrid engine | W2 |
| G-2 | No edge-proximity rerank | W3 |
| G-3 | No measurable lift evidence | W4 |

## Success Criteria (rollup)

1. `hybrid_search_engine.search()` accepts `use_adg_seed=True` flag
2. Precision@10 on curated benchmark ≥5pp improvement with seeds+rerank vs. baseline
3. Rerank latency ≤50ms on top-100
4. ProceduralPattern entity `ADGSeedRerankIntegration` in Memory
5. Notion Wave/Phase row flipped to Done

## Dependencies

- `tools/ingestion/adg_cards/` projection — DONE (Wave E µW1–µW7, commit unknown)
- `retrieval_benchmark.py` with curated queries — verify at kick-off

## Out of Scope

- New retrieval engine; this wires existing `hybrid_search_engine`
- Card emitter changes; cards are read-only here
- Retrieval-eval rubric redesign
