# L0 Authority Boundary & Raw Execution Burndown Wave

**Plan ID**: `l0-authority-burndown-3a7b21`
**Status**: Todo
**Created**: 2026-04-28
**Source**: Backlog snapshot — items #2 (676.6), #19 (416.5), #20 (416.1) all L0 + Execution/Security

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
