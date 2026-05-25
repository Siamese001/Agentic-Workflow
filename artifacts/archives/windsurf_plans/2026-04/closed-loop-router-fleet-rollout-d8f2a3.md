# Closed-Loop Router Fleet Rollout — Generic Helper + L1/c0 Exemplar

Plan ID: `closed-loop-router-fleet-rollout-d8f2a3`
Status: In-progress (W1 executing)
Author: Cascade
Created: 2026-04-26

## Problem

Audit (2026-04-26) of `agentic_core/L0..L6` finds **15+ Router classes with
hardcoded thresholds and zero closed-loop wiring**. Only `HealingRouter`
(L2/cascade, just landed in plans `c4d8a1` W1+W2) writes a `ROUTER_DECISION:`
marker, persists predictions, and binds outcomes. The other 9 matrix routers
plus the unmatrix'd routers below are constitutional §29 violations:

| Router | File | Static-threshold evidence |
|--------|------|---------------------------|
| L0 path | `agentic_core/L0_routing/reasoning/path_router.py` | `DEFAULT_ABSTAIN_THRESHOLD` magic number; hardcoded `[0.0, 1.0]` floors |
| L0 agentic | `agentic_core/L0_routing/reasoning/agentic_router.py` | `min_confidence: float = 0.2` constructor default |
| L0 ensemble | `agentic_core/L0_routing/reasoning/ensemble_router.py` | hardcoded fallback confidences (0.3, 0.4, 0.1, 0.8 weight); meta-learner is in-memory only — non-durable |
| L0 graph-aware | `agentic_core/L0_routing/reasoning/graph_aware_router.py` | unaudited |
| L0 shadow classifier | `agentic_core/L0_routing/reasoning/shadow_router_classifier.py` | unaudited |
| L1 retrieval | `agentic_core/L1_cognition/reasoning/retrieval_router.py` | `_DEFAULT_PLANS` table indexed by intent; `SLO_BUDGETS_MS` hardcoded; pure-regex intent classifier |
| L1 query | `agentic_core/L1_cognition/reasoning/query_router.py` | unaudited |
| L1 advanced l0 | `agentic_core/L1_cognition/reasoning/ml_decision_support/models/advanced_l0_router.py` | unaudited |
| L2 lane | `agentic_core/L2_execution/capability/lane_router.py` | static `_lane_map` dict |
| L3 query | `agentic_core/L3_orchestration/reasoning/engines/query_router.py` | unaudited |
| L3 sovereign-mcp | `agentic_core/L3_orchestration/reasoning/engines/sovereign_mcp_router.py` | unaudited |

The W1/W2 implementation in `HealingRouter` is **good but bespoke** — each
router rewriting the marker emission + ledger writes + outcome binding +
posterior-fallback dance is a copy-paste anti-pattern that will rot.

## Goal

1. **Extract** the closed-loop pattern from `HealingRouter` into a generic,
   dependency-injected helper at `tools/ledgers/router_helper.py` so any
   future router can wire closed-loop in **<20 lines**, not 200.
2. **Refactor** `HealingRouter` to use the helper (validates that it actually
   serves the proven case).
3. **Wire** `L1/RetrievalRouter` as the second exemplar (matrix row #3
   L1/c0). Different decision semantics from L2/cascade — proves the helper
   generalizes.
4. **Document + writeback** so the remaining 9+ routers can be wired in
   future waves with zero ambiguity.

## Why these targets

- **Helper** = leverage. One concrete wiring + one helper API ≈ 9 future
  wirings in <100 LOC each.
- **HealingRouter refactor** = correctness check. If the helper can't replace
  the bespoke implementation cleanly, the API is wrong.
- **`L1/RetrievalRouter`** = best second exemplar. Different shape from L2:
  - Decision payload is *plan dict* (multi-field structured output), not single
    tier label. Tests the helper's payload flexibility.
  - Outcome metric is "did the retrieval plan satisfy SLO?" — distinct from
    success/fail boolean. Tests outcome-extraction flexibility.
  - High fan-in: every retrieval call goes through it. Posterior gets data fast.

## Out of Scope (deferred)

- Wiring routers 4–11 in the audit table (each a separate plan; helper makes
  them ~50 LOC each after this lands).
- Replacing `EnsembleRouter`'s in-memory `MetaLearner` with durable storage
  (separate concern from the closed-loop ledger; deserves its own ADR).
- Auto-flipping any router's static thresholds based on accumulated data
  (data-gated; rails are sufficient for now).
- Removing `import sqlite3` from the 8 pre-existing L0..L6 violators
  (separate cleanup wave).

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W1 | 1.1–1.7 | Helper + L1/c0 wiring + tests + writeback | ~22000 | in-progress |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Helper API | `tools/ledgers/router_helper.py` (new) | API surface design — must serve both L2/cascade (single tier) and L1/c0 (plan dict) | 4000 | pending |
| 1.2 | router_l1_c0 schema + registry + skill | `.windsurf/schemas/router_l1_c0_ledger.schema.sql`, `tools/ledgers/schema_registry.py`, `.windsurf/skills/ledger-consulter-router-l1-c0/SKILL.md` | additive only | 2000 | pending |
| 1.3 | HealingRouter refactor — DEFERRED | `agentic_core/L2_execution/healers/healing_router.py` | preserve all 38 existing tests; reduce LOC | 4000 | **deferred** — its 38 tests pin a specific marker format (`tier=`, `provider=`, `gate=`) that differs from the helper's generic shape. Refactor would be a regression. Helper API is validated by the L1/c0 wiring + dedicated helper unit tests. |
| 1.4 | RetrievalRouter wiring | `agentic_core/L1_cognition/reasoning/retrieval_router.py` | preserve existing route() signature + behavior; closed-loop is additive | 4000 | pending |
| 1.5 | Helper unit tests | `tests/unit/tools/ledgers/test_router_helper.py` | full coverage of record_decision/bind_outcome/get_posterior + fail-soft | 4000 | pending |
| 1.6 | RetrievalRouter integration tests | `tests/unit/agentic_core/L1_cognition/reasoning/test_retrieval_router_closed_loop.py` | verify marker + ledger row + outcome bind | 2500 | pending |
| 1.7 | Apply schema, run gates, commit, push, writeback | (verification) | none | 1500 | pending |

## ADG_GRAPH_LAYER_EVIDENCE

This wave is **additive infrastructure** — no semantic refactoring across
layers, no file deletions. The added files satisfy the graph-layer
primitives:

- **Materialized views**:
  - `mv_hotspot_centrality` confirms `healing_router.py` is high fan-in
    (CENTRAL_DEPENDENCY) — refactoring to use the helper PRESERVES public
    API; only internals change.
  - `mv_dependency_cone_risk` shows `tools/ledgers/` is a stable hub — adding
    `router_helper.py` here matches the existing topology.
- **Semantic edges added**: `healing_router → router_helper (uses)`,
  `retrieval_router → router_helper (uses)`,
  `router_helper → hook_helpers (writes_to)`, `router_helper →
  posterior_reader (reads_from)`. No new cross-layer violations.
- **P-views**: `v_p1_zero_caller_infra` — every new file has at least one
  caller from day one (the two exemplar routers + future tests).

## ADG_HOTSPOT_REPORT

| File | Layer | Fan-in | Archetype | Surface | Impact |
|------|------:|-------:|-----------|---------|-------:|
| `healing_router.py` | L2 | high | CENTRAL_DEPENDENCY | Execution+Observability | refactor only — public API unchanged |
| `retrieval_router.py` | L1 | very high | CENTRAL_DEPENDENCY | Execution | additive wiring only — public API unchanged |
| `tools/ledgers/router_helper.py` | tools | new | CENTRAL_DEPENDENCY (target) | Observability | 0 callers at creation; 2 by end of wave |

No P0/P1/P2 catch-site antipatterns introduced. All exception handlers in
the helper are specific-typed with guardian comments where fail-soft is
required.

## Constitutional Compliance

- **§22** ADG graph layer is primary — satisfied (this section).
- **§28** SQLite-direct fallback — N/A.
- **§29** Closed-loop router evidence — **this plan extends §29 compliance
  to L1/c0 and provides reusable infrastructure for the remaining 7 matrix
  routers**.

## Test Strategy

`tests/unit/tools/ledgers/test_router_helper.py`:

1. `record_decision()` writes ledger row with prescribed payload shape
2. `record_decision()` emits `ROUTER_DECISION:` marker with all required fields
3. `bind_outcome()` updates the row, computes Brier, sets band correctly
4. `get_posterior()` aggregates per (decision_class, fingerprint)
5. Posterior gates correctly at `n_floor`
6. `LEDGER_WRITER_BYPASS` is honored
7. Fail-soft: ledger import error returns empty handle; routing untouched
8. Fail-soft: SQLite error in posterior returns `used=False`
9. Multiple routers writing to same ledger don't collide
10. Decision payload accepts arbitrary nested JSON

`tests/unit/agentic_core/L1_cognition/reasoning/test_retrieval_router_closed_loop.py`:

1. `RetrievalRouter.route()` emits the §29 marker
2. Ledger row records intent, plan_dict, slo_budget
3. Outcome binding reflects whether the implied budget fit the SLO
4. Posterior path activates above floor (mocked)
5. Existing public API behavior preserved (delegates to existing tests)

`tests/unit/agentic_core/L2_execution/healers/test_l2_cascade_router_ledger.py`
(extended): all 38 existing tests must pass after HealingRouter refactor.

## Verification

- 38 existing L2/cascade router tests still pass
- 1618 broader L2 tests still pass
- New helper test file ≥10 tests, all green
- New L1 wiring test file ≥5 tests, all green
- `check_ledger_writer_contract.py` → all 12 ledgers conform
- `check_router_calibration_evidence.py` → OK
- Live smoke: real `RetrievalRouter.route("how does X work?")` writes a
  ledger row + emits the marker
