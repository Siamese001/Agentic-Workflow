---
trigger: model_decision
description: Use this rule whenever a refactoring, hotspot analysis, blast radius, test-scope, or GraphDB query is needed — the P6b/P7 per-run analyst artifacts are the PRIMARY source because they are pre-computed, deterministic, and shipped with every ADG run.
---
# ADG P7 Analyst Artifacts — Primary Source for Refactoring

> SSOT reference: `tools/generate/generate_full_adg.py` P6b + P7 blocks.
> Extends: `adg-hotspot-enforcement.md`, `adg-graph-layer-enforcement.md`, `adg-canonical-invariants.md`.

## Why This Rule Exists

Every full ADG run (`python tools/generate_full_adg.py`) now produces **7 analyst-grade
artifacts** that pre-compute the exact analyses rules and skills demand — burndown,
blast radius, centrality, seams, refactor candidates, GraphDB query families, and
runtime witness-tier satisfaction. They are deterministic, cached in the per-run zip,
and require zero additional queries.

**Invariant:** these artifacts are the PRIMARY source for the questions below. Live ADG
MCP calls (`adg_violations`, `adg_edge_fanin`, `adg_edge_fanout`) remain VALID but are
SECONDARY — use them only when the artifact does not cover the specific question or
the snapshot is older than the last code change.

---

## The 7 Per-Run Analyst Artifacts

All under `artifacts/adg/` and included in `adg_run_<ts>.zip`:

| # | Artifact | Produced By | Primary Use |
|---|----------|-------------|-------------|
| 1 | `adg_graphdb_projection_<ts>.json` | P6b: `tools/graphdb/project_graph.py` | NetworkX node-link JSON — full 76k-node / 255k-edge graph projection |
| 2 | `adg_graphdb_metadata_<ts>.json` | P6b: `SnapshotMetadata` | Commit SHA, node/edge counts, projection timestamp |
| 3 | `adg_graphdb_index_<ts>.json` | P6b: `SnapshotManager` | Snapshot registry / lookup index |
| 4 | `adg_graphdb_queries_<ts>.json` | P7: `tools/graphdb/queries/*` | 9 StructuralQueries + BlastRadius hubs + 7 layer subgraphs — pre-run over the NX graph |
| 5 | `adg_structural_outputs_<ts>.json` | P7: `tools/adg/structural_outputs.py` | Burndown + top-20 blast-radius + seams + top-20 centrality |
| 6 | `adg_refactor_accelerator_<ts>.json` | P7: `tools/adg/refactor_accelerator.py` | Top-20 refactor candidates with ADG + 90-day churn + impacted tests |
| 7 | `adg_runtime_spine_<ts>.json` | P7: `tools/adg/mv_runtime_spine.py` | 6 handoff views + 13 cross-cutting families + semantic satisfaction check |

All are non-blocking at generation time; absence in the zip means the helper raised and
was logged by the caller. Consult the ADG generation log before falling back to live
MCP queries.

---

## Question → Artifact Routing Table (PRIMARY source)

| Question | PRIMARY artifact + field | SECONDARY (live MCP) |
|----------|--------------------------|----------------------|
| "Which files should I refactor first?" | `adg_refactor_accelerator_<ts>.json` → `candidates[]` (already ranked by ADG + churn + blast + impacted tests) | `adg_violations` + manual ranking |
| "Top-N blast radius targets?" | `adg_structural_outputs_<ts>.json` → `blast_radius` (top 20) | `adg_edge_fanout` transitive walk |
| "Top-N centrality hubs?" | `adg_structural_outputs_<ts>.json` → `centrality` (top 20) | `mv_hotspot_centrality` |
| "Where are the chokepoint seams?" | `adg_structural_outputs_<ts>.json` → `seams` | `mv_graph_chokepoint_bridges` |
| "Current burndown / P0/P1/P2 totals?" | `adg_structural_outputs_<ts>.json` → `burndown` | `adg_violations` |
| "Which tests cover a refactor target?" | `adg_refactor_accelerator_<ts>.json` → `candidates[i].impacted_tests` | `tools/adg/adg_test_selector.py` |
| "90-day git churn on this file?" | `adg_refactor_accelerator_<ts>.json` → `candidates[i].churn_90d` | `git log --since` |
| "High fan-in/out hubs?" | `adg_graphdb_queries_<ts>.json` → `blast_radius.high_fan_in_out_hubs` | `adg_edge_fanin` manual iteration |
| "Layer purity / L0/L5/L6 role violations?" | `adg_graphdb_queries_<ts>.json` → `structural.l0_l1_l6_role_purity` | live MV query |
| "Gravity / layer reach violations?" | `adg_graphdb_queries_<ts>.json` → `structural.gravity_import_violations` + `illegal_layer_reach` | `v_p0_*`, `v_p1_*` P-views |
| "UWG / provider bypass?" | `adg_graphdb_queries_<ts>.json` → `structural.uwg_durable_write_conformance` | `v_p0_write_bypass_uwg` |
| "Capability / tool provider chokepoints?" | `adg_graphdb_queries_<ts>.json` → `structural.capability_tool_provider_chokepoint_conformance` | manual MV query |
| "Agentic spine completeness?" | `adg_graphdb_queries_<ts>.json` → `structural.agentic_spine_completeness` | manual MV query |
| "L2 lifecycle conformance?" | `adg_graphdb_queries_<ts>.json` → `structural.l2_lifecycle_conformance` | manual MV query |
| "Grounding / contract separation?" | `adg_graphdb_queries_<ts>.json` → `structural.grounding_contract_separation` | manual MV query |
| "Trace / replay / eval coverage?" | `adg_graphdb_queries_<ts>.json` → `structural.trace_replay_eval_coverage` | manual MV query |
| "Extract a layer subgraph (L0..L6)?" | `adg_graphdb_queries_<ts>.json` → `analyst.subgraph_L<N>` | `adg_nodes_by_layer` |
| "Runtime handoff witness satisfaction?" | `adg_runtime_spine_<ts>.json` → `handoff_views[]` + `semantic_failures` | `mv_runtime_spine` live query |
| "Cross-cutting family witness counts?" | `adg_runtime_spine_<ts>.json` → `cross_cutting_families[]` | live MV query |
| "Need to walk the full graph programmatically?" | `adg_graphdb_projection_<ts>.json` (NetworkX node-link JSON, load via `networkx.readwrite.json_graph`) | projection re-run |

---

## Required Protocol for T2/T3 Refactoring

Before drafting any refactoring plan or wave queue:

1. **Locate the latest run artifacts.** Find the most recent `adg_indexed_<ts>.sqlite` under `artifacts/adg/`; the matching P7 artifacts share the same `<ts>` stem.
2. **Load the refactor accelerator FIRST.** Its `candidates[]` array IS the ranked hotspot queue. Do not recompute by hand.
3. **Cross-reference structural_outputs.** For each top candidate, pull its centrality score + blast-radius size + seam proximity from `adg_structural_outputs_<ts>.json`.
4. **Cross-reference graphdb_queries.** Check whether any candidate appears in `illegal_layer_reach`, `uwg_durable_write_conformance`, `gravity_import_violations`, or `l0_l1_l6_role_purity` — these drive the refactor *strategy* (layer move vs exception narrowing vs boundary insertion).
5. **Cross-reference runtime_spine.** If a candidate shows `semantic_failures` in the runtime spine report, the refactor MUST close the handoff witness gap (not just narrow the exception).

---

## Plan Output Requirements (extends `adg-hotspot-enforcement.md`)

In addition to `## ADG_HOTSPOT_REPORT` and `## ADG_GRAPH_LAYER_EVIDENCE`, plans that
consume P7 artifacts SHOULD include:

```markdown
## ADG_P7_ARTIFACT_EVIDENCE

**Snapshot**: adg_indexed_<ts>.sqlite
**Artifacts consulted** (per-run zip: adg_run_<ts>.zip):
- adg_refactor_accelerator_<ts>.json — top-N candidates, churn_90d, impacted_tests
- adg_structural_outputs_<ts>.json — burndown, blast_radius, seams, centrality
- adg_graphdb_queries_<ts>.json — structural query families
- adg_runtime_spine_<ts>.json — handoff + cross-cutting witness tiers (if relevant)

**Candidate selection**:
| rank | file | layer | churn_90d | blast_radius | centrality | impacted_tests | archetype |
|------|------|-------|-----------|--------------|------------|----------------|-----------|
| 1    | ...  | ...   | ...       | ...          | ...        | ...            | ...       |

**Strategy signals from graphdb_queries**:
- <candidate> appears in <query_name> → refactor strategy: <layer move | exception narrowing | boundary insertion | seam extraction>

**Runtime witness gaps**:
- <family> → <orphaned_count> / <zero_count> → refactor MUST restore witness tier
```

---

## Blocking Conditions

| Condition | Action |
|-----------|--------|
| No `adg_refactor_accelerator_<ts>.json` for current snapshot | Regenerate ADG: `python tools/generate_full_adg.py` |
| P7 artifacts older than last code change | Regenerate ADG before planning |
| Plan uses live MCP iteration when P7 artifact answers the same question | BLOCKED — use artifact; cite live MCP only for artifact gaps |
| P7 helper logged `skipped` in ADG generation log | Investigate why; do not plan refactoring on stale data |

---

## Relationship to Other Rules

- **`adg-hotspot-enforcement.md`** — still authoritative for the hotspot report. This rule specifies the **primary data source** for that report.
- **`adg-graph-layer-enforcement.md`** — still authoritative for MV/semantic-edge/P-view citations. This rule specifies that `adg_graphdb_queries_<ts>.json` ships those same analyses pre-run.
- **`adg-canonical-invariants.md`** — unchanged. SQLite is still canonical; P7 artifacts are **projections** of SQLite truth.
- **`adg-repair-discipline.md`** — repair loops can consult `adg_refactor_accelerator_<ts>.json` → `candidates[i].impacted_tests` for scoped test selection instead of `tools/adg/adg_test_selector.py`.

---

## Quick Path Reference

```
artifacts/adg/
├── adg_indexed_<ts>.sqlite                   # canonical (don't read directly for analysis — use artifacts below)
├── adg_graph_<ts>.sqlite                     # P6 graph projection (SQLite edges)
├── adg_graphdb_projection_<ts>.json          # P6b NetworkX node-link
├── adg_graphdb_metadata_<ts>.json            # P6b metadata
├── adg_graphdb_index_<ts>.json               # P6b index
├── adg_graphdb_queries_<ts>.json             # P7 GraphDB query families (PRIMARY)
├── adg_structural_outputs_<ts>.json          # P7 burndown/blast/seams/centrality (PRIMARY)
├── adg_refactor_accelerator_<ts>.json        # P7 ranked refactor candidates (PRIMARY)
├── adg_runtime_spine_<ts>.json               # P7 runtime witness tiers (PRIMARY)
└── adg_run_<ts>.zip                          # archive containing all of the above
```

---

## Fallback Policy

If P7 artifacts are unavailable (stale snapshot, helper skipped, fresh checkout):

1. Regenerate: `python tools/generate_full_adg.py`
2. If regeneration fails, fall back to live ADG MCP queries (`adg_*` tools)
3. If live MCP is down, run `/mcp-failure-rca`
4. Never fall back to `grep_search` for dependency / hotspot / blast-radius questions — that is a constitutional violation (§ADG-First).
