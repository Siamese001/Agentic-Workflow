---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\l0-authority-burndown-3a7b21.md'
original_relative_path: '_archive\\2026-05\\l0-authority-burndown-3a7b21.md'
source_sha256: 3c532c4091cd5ae4a2923acc40c3ed0a3ee9635dc13542c1b03219cbe535855d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# L0 Authority Boundary & Raw Execution Burndown Wave

**Plan ID**: `l0-authority-burndown-3a7b21`
**Status**: **Mostly OBSOLETE — superseded by ADR-071 (2026-04-29)**
**Created**: 2026-04-28
**Source**: Backlog snapshot — items #2 (676.6), #19 (416.5), #20 (416.1) all L0 + Execution/Security
**Disposition ADR**: `docs/architecture/adr/ADR-071-l0-authority-boundary-disposition.md`

## 2026-04-29 Update (ADG Evidence + ADR-071)

ADG snapshot `adg_indexed_04282026_2152.sqlite` reveals:

- **W1.1 (17 authority breaches)**: Confirmed in `mv_authority_boundary_breaches`. **All 17 breaches are in ONE file** — `apps_shared/proof/scenario_base.py`. Disposition: **guardian exemption** (proof harness — cross-layer imports are the harness's purpose). See ADR-071.
- **W2.1 (3 raw exec sites)**: `v_p0_l0_raw_execution` returns **0 rows** — already fixed in upstream commits. **OBSOLETE**.
- **W4.1 (PathRouter dispatch)**: Unrelated to authority boundary; re-scoped to W5 routing-unification plan.

**Net remaining work**: Wave 1 only — apply guardian exemption header to `scenario_base.py` (done in commit accompanying ADR-071) + close the 2 stale Notion rows.

## ADG_HOTSPOT_REPORT

| Rank | Source File | Layer | breach_count | Archetype | Surface Reference | Disposition |
|---:|---|:---:|---:|---|---|---|
| 1 | `apps_shared/proof/scenario_base.py` | L_APP | 17 | ORCHESTRATOR | Execution Surface | Guardian-exempt (ADR-071) |

Single-file concentration: 17/17 (100%) of all `mv_authority_boundary_breaches` rows attribute to one proof harness. No CENTRAL_DEPENDENCY or SAFETY_GATEKEEPER hotspots remain in L0 after upstream commits cleared `v_p0_l0_raw_execution` to 0.

## ADG_GRAPH_LAYER_EVIDENCE

**Materialized views consulted (≥3, per constitutional §22):**

1. **`mv_authority_boundary_breaches`** — produced the 17-breach inventory. Grouped by `breach_class` (all `L_APP_core_bypass`) and by `(src_layer, dst_layer)` (14×L_APP→L0, 2×L_APP→L2, 1×L_APP→L1). Drives ADR-071 disposition.
2. **`mv_hotspot_centrality`** (filtered to `layer = 'L0'`) — confirms top L0 hotspots (`config/path_constants.py` fan_in=1136, `config/__init__.py` fan_in=257, `c0_retrieval/__init__.py` fan_in=191) are NOT involved in the authority breach. The breaches target L0 routing modules from outside the layer; the hotspots are inside the layer.
3. **`mv_critical_path_segments`** — `scenario_base.py` does not appear on any critical path because it is internal proof infrastructure, not a runtime dependency. Validates the guardian-exemption disposition: cross-layer imports here cannot poison production runtime.

**Semantic edges used (beyond `imports`):**
- `controls_flow` — confirms scenario_base orchestrates layer-by-layer execution (its purpose), not a covert side channel
- `resolves_callsite` — every L0/L1/L2 callsite resolved from `scenario_base` is direct invocation of public layer entry points, not access to internals

**P-views cross-referenced:**
- `v_p0_l0_raw_execution` — **0 rows** (was 3 at Notion-row creation). Defect already closed upstream.
- `v_p0_apps_direct_infra` — **0 rows**. Confirms no other apps_*/proof code is replicating the same pattern.
- `v_p1_mis_layered_infra` — surveyed, no L0 entries that would chain off the resolved breaches.

ADG snapshot: `adg_indexed_04282026_2152.sqlite`. Inventory CSV: `docs/reports/maintenance/l0_authority_breaches_catalog.csv` (17 rows, all single-source). CI gate: `ops_scripts/ci/check_authority_boundary_breaches.py` enforces total ≤17 + all-exempt-source invariant.

## Context

Three top-25 P1 items concentrate in **L0 routing/authority surface**:

- **#2 (impact 676.6)** — `2_authority_boundary` — 17 cross-layer authority breaches
- **#19 (impact 416.5)** — `v_p0_l0_raw_execution` — 3 raw execution sites bypass orchestrator
- **#20 (impact 416.1)** — `W5.P4 PathRouter dispatch` — RoutingFeatureVector wiring

These share the L0 layer, the same fan-in pattern (router → callers), and the same architectural concern (authority boundary discipline). Bundling them as one wave amortizes the ADG re-query cost and produces a coherent commit history.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| W1 — Authority boundary catalog | W1.1 | Enumerate 17 cross-layer authority breaches via `v_p0_l0_authority_boundary` | 4000 | ADG L0 layer surface stable | Todo | All 17 sites have ADR-tagged remediation status |
| W2 — Raw execution fix | W2.1 | Route 3 raw execution sites through orchestrator | 8000 | Orchestrator dispatch path stable | Todo | `v_p0_l0_raw_execution` returns 0 rows |
| W3 — Authority boundary remediation | W3.1, W3.2 | Refactor or exempt-with-evidence each of 17 breaches | 16000 | ADR W1.1 published | Todo | Cross-layer count drops to 0 or every remaining is guardian-exempt |
| W4 — PathRouter dispatch wiring | W4.1 | Wire RoutingFeatureVector through PathRouter (W5.P4 from sibling plan) | 6000 | RoutingFeatureVector schema stable | Todo | PathRouter dispatches with feature vector emit `ROUTER_DECISION:` markers |

**Total est. tokens**: ~34,000

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| W1.1 | Catalog 17 authority breaches | `v_p0_l0_authority_boundary` rows | Breaches not categorized | 4000 | Todo |
| W2.1 | Wire 3 raw exec sites through orchestrator | `agentic_core/L0_routing/raw_exec/`, orchestrator | Direct exec bypasses dispatch ceremony | 8000 | Todo |
| W3.1 | Refactor authority breaches (Tier 1: simple) | TBD from W1.1 catalog | Cross-layer imports | 8000 | Todo |
| W3.2 | Refactor authority breaches (Tier 2: structural) | TBD from W1.1 catalog | Architectural boundary fix needed | 8000 | Todo |
| W4.1 | PathRouter + RoutingFeatureVector wiring | `agentic_core/L0_routing/path_router.py`, callers | RoutingFeatureVector unwired | 6000 | Todo |

## ADG Graph Layer Evidence (populate at W1.1 start)

Required before W1.1 begins (constitutional §22):

- Materialized views: `mv_graph_reverse_dependency_hotspots` filtered to `layer='L0'`, `mv_graph_chokepoint_bridges`, `mv_dependency_cone_risk` for L0
- P-views: `v_p0_l0_raw_execution`, `v_p0_l0_authority_boundary`, `v_p0_apps_direct_infra` cross-referenced
- Semantic edges: `resolves_callsite`, `controls_flow` from L0 router into upstream apps_*

## ADG Hotspot Report (populate at W1.1 start)

| File | Layer | Fan-In | Archetype | Surface | Impact | Phase |
|------|------:|-------:|-----------|---------|-------:|-------|
| _populate at W1.1 start_ | L0 | – | CENTRAL_DEPENDENCY | Execution/Security | – | – |

## Dependencies

- Blocks: closure of L0 routing certification (3 P0 raw-exec sites must close before L0 can be marked production-stable)
- Depends on: ADG snapshot freshness, orchestrator dispatch stability
- Sibling plan: W4-P8 guardrail family (`w4-p8-guardrail-family-e93f8a.md`) — both touch L0/L5 surfaces but are independently executable

## Acceptance

- `v_p0_l0_raw_execution` returns 0 rows
- `v_p0_l0_authority_boundary` count drops from 17 to 0 (or remaining are guardian-exempt with ADR-linked justification)
- All 3 Notion rows (#2, #19, #20) flip to Status=Done
