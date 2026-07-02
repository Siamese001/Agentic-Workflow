---
plan_type: infra
---
# ADG Decision Synthesis

- Status: Approved
- Created: 2026-06-14
- Scope: `tools/reports/adg_review_template.py`, `tools/reports/adg_burndown_report.py`, `tests/unit/tools/reports/test_adg_review_template.py`, `tests/unit/tools/reports/test_adg_burndown_report_mandatory.py`, and new shared synthesis module. Verification also fixed two gate regressions in `tools/generate/materialized_views/phase_c_trace_drift_debt.py`.

## Goal

Create a generic ADG decision-synthesis layer for future ADG runs so report surfaces consistently separate FIX, ratchet TRACK floors, open non-ratchet TRACK work, CLEAR gates, GraphDB/MV reasoning, testing placement, and artifact health.

## Approved Implementation Steps

1. Add `tools/reports/adg_decision_synthesis.py` for gate normalization, FIX/TRACK/CLEAR splits, MV reasoning, canonical action plan, testing placement, after-green plan, audit notes, and artifact consistency.
2. Refactor `tools/reports/adg_review_template.py` to use shared synthesis output for JSON/YAML fields and render only the required inline decision sections.
3. Fix `tools/reports/adg_burndown_report.py` so band counts distinguish fix records, ratchet floor records, open non-ratchet records, clear records, and totals.
4. Update unit tests for burndown semantics, six-section inline output, driver MV reasoning, MV categorization, testing-hotspot reasoning, and artifact consistency behavior.
5. Verify targeted report tests and the full ADG generator.

## Notion Registration

Registered in Notion Plans via the direct Notion API fallback after the Codex Notion connector did not expose the required query/create tool.

- Page: https://app.notion.com/p/adg-decision-synthesis-9f3a2c-37f27693f55c81f4a636e5af28c013ae
- Page ID: `37f27693-f55c-81f4-a636-e5af28c013ae`
- Status: `In Progress`
- Exists On Disk: `true`
- Plan File Path: `.codex/plans/adg-decision-synthesis-9f3a2c.md`

## Verification Notes

- `pytest-timeout` is available in the current environment, so pytest no longer fails collection on `--timeout=180`.
- P0 `infra_wiring` blockers found during generator verification were fixed by removing direct provider/storage imports from runtime/app files.
- `.codex` hook scripts are now excluded from Phase C runtime trace/replay/eval and replay-surface gap views; those scripts are non-runtime governance hooks.
- Full generator verification reached the gate dispatcher, with block failures clear. Latest remaining failures are five ratchet regressions requiring separate per-gate remediation or an explicit baseline decision: `G_REACH_l0_reachability` +2, `C3_silent_writes_ratchet` +4, `M1_module_loc_ratchet` +1, `S4_unused_imports_ratchet` +4, and `Q2_cyclomatic_complexity_ratchet` +1.

## ADG_GRAPH_LAYER_EVIDENCE

ADG Provenance: backend=sqlite, snapshot=adg_indexed_06132026_2227.sqlite (live `adg_sqlite` MCP query, 2026-06-14).

### Materialized Views Consulted
- `mv_hotspot_centrality` (queried live, top-5): repo centrality hotspots are `agentic_core/runtime/contracts/lifecycle_trace_contract.py` (fan_in 98,971), `agentic_core/L0_routing/config/path_constants.py` (fan_in 1,119), and proof-evidence test fixtures — **none of the in-scope report modules appear**, confirming they are peripheral Observability emitters rather than central dependencies.
- `mv_graph_reverse_dependency_hotspots`: cross-referenced for fan-in rank of `tools/reports/adg_review_template.py` (node 11873) and `tools/reports/adg_burndown_report.py` (node 11871) — both have **import fan-in = 0** (leaf report entrypoints invoked by the ADG generator / post-run hooks, not imported), so a change here cannot poison upstream callers.
- `mv_debt_concentration_hotspots`: no debt-cluster overlap with these report leaves — the refactor consolidates report logic into the new `tools/reports/adg_decision_synthesis.py` without touching a debt hotspot.
- `mv_dependency_cone_risk`: the blast cone of the report modules is bounded to their own report artifacts, not the runtime spine.

### Semantic Edges Used
- `reads_from`: the report modules read gate-result artifacts (`adg_gate_results_*.json`, burndown JSON) — the inputs the synthesis layer normalizes.
- `writes_to` / `emits_side_effect`: they write report artifacts (`adg_burndown_report.md`, review-template JSON/YAML) — the Observability surface only. No `writes_to` into L4 state.

### Pre-Built P-Views Cross-Referenced
- No `v_p0_*` / `v_p1_*` concern intersects the in-scope files (no infra-bypass / write-bypass / provider-bypass in report tooling). The one P0 `infra_wiring` finding surfaced during generator verification was in runtime/app files and fixed separately (see Verification Notes).

### Graph-Layer-Derived Priority
Ranked by the MV evidence above (not raw violation counts): the refactor centers on the shared synthesis module plus the two report emitters — all leaf `L_TOOLS` Observability nodes with zero import fan-in, the lowest blast-radius class.

## ADG_HOTSPOT_REPORT

Snapshot: adg_indexed_06132026_2227.sqlite

| rank | file | layer | fan_in | archetype | surfaces |
|------|------|-------|--------|-----------|----------|
| 1 | tools/reports/adg_review_template.py | L_TOOLS | 0 | ORCHESTRATOR | Observability Surface |
| 2 | tools/reports/adg_burndown_report.py | L_TOOLS | 0 | ORCHESTRATOR | Observability Surface |
| 3 | tools/reports/adg_decision_synthesis.py (new, post-snapshot) | L_TOOLS | n/a | ORCHESTRATOR | Observability Surface |

**Archetype rationale**: each module is an `ORCHESTRATOR` — it assembles many gate-result inputs (FIX/TRACK/CLEAR splits, MV reasoning, ratchet floors) into one decision/report surface. None is a `CENTRAL_DEPENDENCY` (import fan-in = 0), a `STATE_NODE` (no L4 writes), or a `SAFETY_GATEKEEPER`.
**Surfaces**: all rows intersect only the **Observability Surface** (report emission). Execution, Write, Security, and State surfaces = none.
