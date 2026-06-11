---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\l2-cascade-router-closed-loop-wiring-c4d8a1.md'
original_relative_path: 'l2-cascade-router-closed-loop-wiring-c4d8a1.md'
source_sha256: 6b97a8938f176d4610a4af767bf41d2a33b688e3c9051bf2507e33740a204ab5
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# L2/cascade Router — Closed-Loop Wiring (constitutional §29)

Plan ID: `l2-cascade-router-closed-loop-wiring-c4d8a1`
Status: In-progress (Wave W1 executing)
Author: Cascade
Created: 2026-04-26

## Problem

`HealingRouter` is router #4 (`L2/cascade`) in the closed-loop matrix per
`.windsurf/rules/closed-loop-router-enforcement.md:79`, but is currently
**non-compliant with constitutional §29**:

- ❌ No `ROUTER_DECISION:` marker emission
- ❌ No `tools.ledgers.hook_helpers.emit_ledger_event` call
- ❌ No persistent ledger on disk
- ❌ No `eu_score` / `brier_score` computation
- ❌ Confidence is hardcoded in `_error_patterns` (`confidence_scorer.py:69-79`)
- ❌ Tier thresholds (HIGH=0.85, MEDIUM=0.50; PRIMARY 0.90/0.65/0.30) are fixed magic numbers
- ❌ No calibration report
- ❌ No outcome→prediction binding

Source code itself flags it: `confidence_scorer.py:48-50` says *"HITL DECISION
REQUIRED: thresholds should be calibrated based on actual healing success
rates"* — never wired.

## Goal

Bring the `L2/cascade` router into full constitutional §29 compliance, mirror
the proven 10-author-loop ledger pattern from ADR-050 onto the runtime loop,
and produce a **calibration-ready** ledger that future waves can use to learn
EU-optimal cascade ordering and provider demotion thresholds.

This wave does NOT replace the heuristic confidence model — that's a follow-on
wave once enough outcome rows accumulate. This wave wires the closed loop so
calibration can begin.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | 1.1–1.7 | Schema + ledger registration + EU/Brier helpers + HealingRouter wiring + outcome binding + calibration report + tests | ~18000 | vLLM 32B reachable; existing ledger pattern (W0–W4 from ADR-050) intact | in-progress | All tests pass; schema applied; ROUTER_DECISION emitted; ledger row written; outcome bound; weekly report generated |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Schema | `.windsurf/schemas/router_l2_cascade_ledger.schema.sql` | none — additive | 1500 | pending |
| 1.2 | Registry | `tools/ledgers/schema_registry.py` | none — additive append | 500 | pending |
| 1.3 | Math helpers | `agentic_core/L2_execution/healers/cascade_calibrator.py` | EU formula, Brier, Wilson, fingerprint | 2500 | pending |
| 1.4 | Wire HealingRouter | `agentic_core/L2_execution/healers/healing_router.py` | decision_id flow, marker emission, ledger write | 4000 | pending |
| 1.5 | Outcome binding | same `healing_router.py` plus `cascade_telemetry.py` adapter | bind on dispatch return | 1500 | pending |
| 1.6 | Calibration script | `ops_scripts/calibration/router_l2_cascade_calibration.py` | Wilson CI per band, write weekly report | 2000 | pending |
| 1.7 | Tests | `tests/unit/agentic_core/L2_execution/healers/test_l2_cascade_router_ledger.py` | full coverage of marker + ledger + EU + Brier + fail-soft | 6000 | pending |

## ADG_GRAPH_LAYER_EVIDENCE

This is a wiring/extension wave inside L2_execution/healers — additive only.
No file deletions, no cross-layer migrations.

- **Materialized views**: `mv_hotspot_centrality` confirms `healing_router.py`
  is a CENTRAL_DEPENDENCY (high fan-in from confidence_aware_executor + apps_*
  via SovereignLLMGateway). Edits stay scoped to the routing seam — public
  surface preserved.
- **Semantic edges**: `flows_to(healing_router → heal_router_otel)`,
  `writes_to(healing_router → router_l2_cascade.sqlite via hook_helpers)`,
  `controls_flow(routing_gates → healing_router)`. New edges added: `writes_to`
  (router → ledger). No `reads_from` semantic added — calibration is offline.
- **P-views**: `v_p1_zero_caller_infra` ensures the new helpers
  (`cascade_calibrator.py`, calibration script) have at least one caller from
  day one (HealingRouter and the weekly cron entry-point respectively).

## ADG_HOTSPOT_REPORT

| File | Layer | Fan-in | Archetype | Surface | Impact |
|------|------:|-------:|-----------|---------|-------:|
| `agentic_core/L2_execution/healers/healing_router.py` | L2 | high | CENTRAL_DEPENDENCY | Execution + Observability | edits scoped to additive wiring |
| `agentic_core/L6_observability/heal_router_otel.py` | L6 | medium | ORCHESTRATOR | Observability | extended (decision_id propagation only) |

No P0/P1/P2 catch-site antipatterns introduced. All new exception handlers
are specific-typed with guardian comments where the fail-soft contract requires
a broad catch (mirroring `tools/ledgers/hook_helpers.py:64`).

## Constitutional Compliance Touched

- §22 ADG graph layer is primary — satisfied (this section)
- §28 SQLite-direct fallback — N/A (no dependency analysis here)
- §29 Closed-loop router evidence — **this plan satisfies §29 for L2/cascade**

## Out of Scope (deferred)

- Replacing hardcoded `_error_patterns` with learned posterior (requires N≥30
  rows per cell; deferred to next wave once telemetry accumulates)
- Auto-flipping `_PRO_REQUIRED_GATES` based on uplift (same reason)
- Cost-Lagrangian for `COST_DEMOTE_*_USD` (same reason)
- The other 9 routers in the matrix (separate plans)

## Test Strategy

Unit tests at `tests/unit/agentic_core/L2_execution/healers/test_l2_cascade_router_ledger.py`:

1. `cascade_calibrator.compute_eu` — known input/output triples
2. `cascade_calibrator.compute_brier_score` — single-shot + accumulated
3. `cascade_calibrator.fingerprint` — deterministic over (failure_class, source_layer, retry_band, error_code)
4. `cascade_calibrator.wilson_lower_bound` — boundary check at p=0.6, n=30
5. Full route() call → ROUTER_DECISION marker captured, ledger row exists
6. dispatch_to_executor() success → outcome row bound to original decision_id
7. dispatch_to_executor() failure → outcome row records `error_code` + `success=False`
8. `LEDGER_WRITER_BYPASS=router_l2_cascade` → no ledger writes, no exceptions
9. Schema applied successfully via `apply_schema.py`
10. Calibration script `--dry-run` produces a Wilson-CI report from synthetic data

## Verification

- `python tools/ledgers/apply_schema.py` succeeds and creates `artifacts/ledgers/router_l2_cascade.sqlite`
- `pytest tests/unit/agentic_core/L2_execution/healers/test_l2_cascade_router_ledger.py -v` → all green
- `python -m py_compile` on every changed Python file
- `python ops_scripts/calibration/router_l2_cascade_calibration.py --dry-run`
  produces a markdown report under
  `docs/reports/calibration/routers/l2_cascade/<YYYY-Www>.md`
- Manual smoke: live Qwen 32B dispatch (already proven 5.6 s in prior turn)
  with router-decision audit log inspected for the new marker
