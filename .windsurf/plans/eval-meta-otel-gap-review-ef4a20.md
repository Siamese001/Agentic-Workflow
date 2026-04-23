# Plan — Eval Harness + Meta-Learning Bus + OTel/Tracing Gap Review

**Slug**: `eval-meta-otel-gap-review-ef4a20`
**Status**: DRAFT (gap analysis complete, awaiting approval)
**Tier**: T3 (cross-layer, >5 files, affects L_APP / L_SL / L6)
**ADG snapshot**: `adg_indexed_04222026_1939.sqlite` (nodes=73,395, edges=544,861, healthy sqlite+redis)
**ADG provenance**: `backend=sqlite, snapshot=adg_indexed_04222026_1939.sqlite`
**Authored**: 2026-04-22

---

## Intent

User request: *"review evaluation harness and metrics feeding into meta learning bus; ensure otel and tracing are implemented fully; use ADG GraphDB hotspots fan in/out materialized views to drive gap analysis and implementation."*

This plan delivers:
1. An ADG-backed gap analysis of (a) eval harness, (b) meta-learning bus SSOT, (c) OTel/tracing coverage.
2. A bounded remediation sequence to close the gaps.

---

## Executive Summary of Findings

| # | Finding | Evidence (ADG) | Severity |
|---|---|---|---|
| F1 | **Eval harness is structurally isolated.** `apps_eval` has exactly 1 import edge into `system_learning` and 0 into `L6_observability` across 46 modules. | `edges` where `source_file LIKE 'apps_eval/%'` AND `symbol LIKE 'system_learning.%'` = 1 row; into `L6_observability.*` = 0 rows | **P1 / Structural** |
| F2 | **Eval harness has zero OTel/tracing.** `apps_eval` has 0 imports of `opentelemetry`, `agentic_core.adg.runtime.tracer`, `consensus_otel`, `heal_router_otel`, or `enhanced_observability`. | grep confirms 0 matches; ADG `edges` confirms 0 tracing-marker imports from `apps_eval/%` | **P1 / Observability Surface** |
| F3 | **Eval harness does not feed the meta-learning bus.** `apps_eval/*` has 0 imports of any `MetaLearningBus` symbol. | `edges` WHERE `source_file LIKE 'apps_eval/%' AND symbol LIKE '%MetaLearningBus%'` = 0 rows | **P1 / Write Surface** |
| F4 | **Two independent `MetaLearningBus` implementations** plus one shim. `engines/meta_learning_bus.py` (indep) vs `meta_learning/meta_learning_bus.py` (canonical w/ `get_process_bus`); `ports/meta_learning_bus.py` is an 8-line shim. Consumers split 2 / 2 / 3. | ADG fan-in on symbol ids 50356 / 50422 / 50439 (counts 2 / 2 / 3); file content of `ports/*.py` confirms shim | **P1 / State Surface (SSOT drift)** |
| F5 | **Tracing uptake is near-zero in system_learning and L6.** Only 2/215 system_learning modules and 2/81 L6 modules import any tracing marker. The OTel-proper import (`from opentelemetry`) appears in only 1 file total (`system_learning/types/telemetry_store_protocol.py`). | ADG `edges` import-marker scan; grep confirms | **P1 / Observability Surface** |
| F6 | **Canonical tracer has only 3 production callers.** `agentic_core.adg.runtime.tracer` is imported by `healing_router.py`, `qwen_vllm/telemetry.py`, and `L6/heal_router_otel.py`. `consensus_otel.py` has **no production callers** (only tests). | grep for `from agentic_core.adg.runtime.tracer` + `from agentic_core.L6_observability.(consensus_otel|heal_router_otel)` | **P2 / Observability** |
| F7 | **ADG graph-layer overlay is under-populated on current snapshot.** Zero materialized views (`mv_*`) and zero P-views (`v_p*`) exist. Semantic edges ARE populated (flows_to=63k, emits_side_effect=29k, reads_from=106k, writes_to=3985, resolves_callsite=54k, controls_flow=52k). | `sqlite_master` query on snapshot returns 0 `mv_*` and 0 `v_p%` objects; `edges.relation_type` counts confirm semantic-edge presence | **P2 / Tooling** (violates constitutional §22 gate expectation) |
| F8 | **Symbol-level side-effect edges do not resolve into target dirs.** Despite 29k global `emits_side_effect` edges, 0 originate from symbols whose `resolved_path` is in `apps_eval/`, `system_learning/`, or `agentic_core/L6_observability/`. This is either an ADG build-depth gap or confirms F2/F3 (these domains truly emit no observable side-effects). | symbol-level join: `nodes.entity_type='symbol' AND resolved_path LIKE '<dir>%' JOIN edges ON src_id WHERE relation_type='emits_side_effect'` = 0 in every target dir | **P2 / ADG build coverage** |
| F9 | **Eval→Learning bridge exists but is under-wired.** The single `apps_eval → system_learning` edge is `regression_detector.py → get_sl_memory_bridge` — a memory bridge, NOT a bus publish path. Scorecards, scenario runs, retrieval-eval results, HITL-decision-quality results have no bus path. | `edges` WHERE `source_file LIKE 'apps_eval/%' AND symbol LIKE 'system_learning.%'` returns exactly one row | **P1 / Write Surface** |

---

## ADG_HOTSPOT_REPORT

Ranked hotspots driving the remediation wave order. Impact = `violations × (1 + log10(1 + fan_in)) × layer_multiplier`. Fan-in from symbol-level `imports` edges. Layers: L_APP=L2 (×1.0), L_SL=L3 (×1.75), L6=×0.75.

| Rank | File | Layer | Fan-in | Archetype | Surface(s) | Impact | Notes |
|------|------|-------|:------:|-----------|-----------|-------:|-------|
| 1 | `system_learning/meta_learning/meta_learning_bus.py` | L_SL | 2 (direct) + 3 (via `ports` shim) = **5 transitive** | STATE_NODE + ORCHESTRATOR | State Surface, Write Surface, Observability Surface | 1.75 × (1+log10(6)) × penalty=3 | **Canonical bus.** Splitting this away from `engines/*.py` is the highest-value single action. |
| 2 | `system_learning/engines/meta_learning_bus.py` | L_SL | 2 | CENTRAL_DEPENDENCY (divergent) | State Surface, Write Surface | 1.75 × (1+log10(3)) × 3 | Independent implementation creating SSOT drift. |
| 3 | `apps_eval/engines/scenario_runner.py` | L_APP | 0 (orphan per ADG, likely dynamic) | ORCHESTRATOR | Execution Surface, Observability Surface | 1.0 × 1.0 × 5 (size=43kB) | **Largest eval engine, zero tracing, zero bus publish.** |
| 4 | `apps_eval/engines/regression_detector.py` | L_APP | 0 | STATE_NODE | Observability Surface | 1.0 × 1.0 × 4 | Only eval file touching `system_learning` — via memory bridge only. |
| 5 | `apps_eval/engines/hitl_decision_quality_engine.py` | L_APP | 0 | CENTRAL_DEPENDENCY | State Surface, Observability Surface | 1.0 × 1.0 × 3 | HITL quality scoring — high-value signal not emitted to bus. |
| 6 | `apps_eval/engines/scorecard_engine.py` | L_APP | 0 | STATE_NODE | Write Surface | 1.0 × 1.0 × 3 | Scorecards not published. |
| 7 | `agentic_core/L6_observability/utils/engines/meta_learning_bridge.py` | L6 | 0 | CENTRAL_DEPENDENCY | Observability Surface | 0.75 × 1.0 × 3 | `L6MetaLearningBridge` — orphaned bridge class, potential merge point. |
| 8 | `agentic_core/L6_observability/consensus_otel.py` | L6 | 0 (production) | SAFETY_GATEKEEPER (unused) | Observability Surface | 0.75 × 1.0 × 2 | Tracer helper with tests but no prod callers. |

**5-Surface intersections**:
- F1 + F9 hit **Write + Observability + State** simultaneously (the eval pipeline's output path is entirely dark).
- F4 hits **State** (the bus is a shared state store for meta-learning).
- F6 hits **Observability** (a gatekeeper the system cannot rely on).

---

## ADG_GRAPH_LAYER_EVIDENCE

Per constitutional §22, T2/T3 refactoring plans must cite ≥3 materialized views, the semantic relations used, and P-view matches.

### Semantic edges (populated on this snapshot)

| Relation | Global count | Used for this plan |
|----------|-------------:|--------------------|
| `imports` | 157,544 | Fan-in / fan-out on all 3 `MetaLearningBus` symbols, eval harness cross-layer reach |
| `flows_to` | 63,738 | Expected to show eval results reaching bus — **absent from target dirs (F8)** |
| `emits_side_effect` | 29,361 | Expected to show eval engines emitting telemetry spans — **absent from target dirs (F8)** |
| `writes_to` | 3,985 | Expected on bus.publish paths — **absent from target dirs (F8)** |
| `reads_from` | 106,301 | Expected on consumers reading bus — low coverage in target dirs |
| `controls_flow` / `resolves_callsite` | 52k / 54k | Present but scoped away from these domains |

### Materialized views

**Status**: `mv_graph_reverse_dependency_hotspots`, `mv_hotspot_centrality`, `mv_graph_chokepoint_bridges`, `mv_graph_critical_path_blast_radius`, `mv_dependency_cone_risk`, `mv_path_criticality_rollup`, `mv_exemptions_near_critical_paths`, `mv_debt_concentration_hotspots` — **none of these exist on the current snapshot** (`sqlite_master` query returned 0 rows matching `mv_%`).

This is itself Finding **F7** and is an input to Wave 0 of this plan: *regenerate the full ADG with graph-layer overlay populated*. Until MVs exist, the §22 gate `check_graph_layer_evidence.py` will refuse to validate any further T2/T3 plan in this workspace. The ranked hotspot table above is built from raw `nodes` + `edges` + `violations` (degraded mode).

**Degraded-mode declaration** (per global_rules.md ADG-First Analysis):
`DEGRADED_FALLBACK: reason=mv_and_pview_overlay_absent_on_snapshot_04222026_1939; hotspot_ranking_from_raw_edges_and_violations; regeneration_required_in_W0`

### P-views

**Status**: no `v_p0_*` / `v_p1_*` / `v_p2_*` / `v_p3_*` views on snapshot. Target dirs scanned for P2 violations via `violations` table directly: 184 LOW-severity violations across all three target dirs, no MEDIUM/HIGH/CRITICAL. Violation profile is therefore *not* the gap — the gap is **missing wiring and missing spans**, not anti-pattern density.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|:-----------:|-------------|:------:|------------------|
| **W0** | P0.1 | Regenerate full ADG so MV + P-view overlay is populated (§22 gate can pass) | 🟢 3k | `tools/generate_full_adg.py` completes without SC-1 block; MV build step runs | ⬜ Todo | `sqlite_master` on new snapshot returns ≥8 `mv_*` rows and ≥4 `v_p*` rows |
| **W1** | P1.1, P1.2 | Collapse the `MetaLearningBus` 3-way drift to a single canonical class under `system_learning/meta_learning/` | 🟡 9k | `meta_learning/meta_learning_bus.py` is the canonical impl; `engines/meta_learning_bus.py` diverges (to be verified before edit) | ⬜ Todo | 1 class, ≥5 consumers migrated, `ports/*.py` remains as re-export shim with deprecation comment, full pytest green |
| **W2** | P2.1, P2.2, P2.3 | Wire eval harness → bus. `scenario_runner`, `scorecard_engine`, `regression_detector`, `hitl_decision_quality_engine`, `evaluation_retrieval_engine` each publish to canonical bus at end-of-run | 🟡 10k | Bus `publish` / `emit_outcome` signature compatible with structured `EvaluationOutcome` record; no circular import across L_APP→L_SL | ⬜ Todo | New ADG snapshot shows ≥5 `apps_eval/* → system_learning.meta_learning.meta_learning_bus.*` import edges; smoke test publishes + round-trips |
| **W3** | P3.1, P3.2 | Install tracing in eval harness via canonical tracer. Each `BaseEvalEngine.run()` implementer wraps its top-level entry in a span; `scenario_runner` adds per-scenario child span; `regression_detector` adds comparison span | 🟡 8k | `agentic_core/adg/runtime/tracer.py` is canonical; no new OTel SDK version required | ⬜ Todo | ADG snapshot shows ≥5 new imports of canonical tracer from `apps_eval/*`; OTel MCP `otel_spans_by_agent` reports non-zero spans after one scenario run |
| **W4** | P4.1, P4.2 | Install tracing in system_learning hotspots (bus publish/consume paths, runtime_hitl_consumer, shadow_drift_analyzer, meta_learning_bridge) | 🟡 8k | Tracer shim accepts no-op `NullTracer` fallback for environments without OTel SDK | ⬜ Todo | Tracing-marker import count in system_learning goes from 2 → ≥8; OTel spans emitted on bus publish |
| **W5** | P5.1 | Retire / repoint `agentic_core/L6_observability/consensus_otel.py` (zero production callers, only test callers) — either delete after verified-unused or re-wire into W4 bus-publish spans | 🟢 3k | No hidden dynamic importers (verify with ADG + grep for dotted-string refs) | ⬜ Todo | ADG shows production fan-in >0 OR file is archived with ADR note |
| **W6** | P6.1 | Regenerate ADG; re-run §22 `check_graph_layer_evidence.py`; publish written review doc `docs/reports/plans/eval-meta-otel-gap-review.md` summarizing deltas | 🟢 4k | Gates pass | ⬜ Todo | `ADG_GRAPH_LAYER_EVIDENCE` section in updated plan lists real MVs + P-view cross-refs; review doc linked from Notion Wave/Phase Convergence |

**Total estimate**: ~45k tokens across 6 waves. Token estimation method: manual bounded-scope estimate (line-count × per-line factor per wave). The `tools/utils/planning/token_estimator.py` pass will be re-run at W6 against finalized file list.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|:-----------:|:------:|
| P0.1 | Populate MV + P-view overlay | `tools/generate_full_adg.py` invocation only; no source edits | F7 | 3k | ⬜ |
| P1.1 | Verify canonical vs divergent bus impl | `system_learning/engines/meta_learning_bus.py`, `system_learning/meta_learning/meta_learning_bus.py` (read-only diff) | F4 | 3k | ⬜ |
| P1.2 | Collapse to canonical + shim the rest | `engines/meta_learning_bus.py` → re-export from `meta_learning/`; `ports/meta_learning_bus.py` re-export preserved | F4 | 6k | ⬜ |
| P2.1 | Add `apps_eval/integrations/meta_bus_publisher.py` thin adapter | NEW file + `apps_eval/__init__.py` update | F1, F3, F9 | 4k | ⬜ |
| P2.2 | Wire engines to publisher | `scenario_runner.py`, `scorecard_engine.py`, `regression_detector.py`, `hitl_decision_quality_engine.py`, `evaluation_retrieval_engine.py` | F1, F3, F9 | 5k | ⬜ |
| P2.3 | Add eval→bus round-trip smoke test | `tests/integration/apps_eval/test_eval_to_bus_roundtrip.py` (NEW) | F1, F9 | 1k | ⬜ |
| P3.1 | Tracer adapter for eval | `apps_eval/integrations/tracing.py` (NEW, imports canonical `agentic_core.adg.runtime.tracer`) | F2, F6 | 3k | ⬜ |
| P3.2 | Wrap 5 eval engine entry points in spans | same 5 engines as P2.2 | F2 | 5k | ⬜ |
| P4.1 | Wrap bus publish + consume in spans | `system_learning/meta_learning/meta_learning_bus.py`, `system_learning/engines/bus_consumer.py`, `system_learning/runtime_hitl_consumer.py` | F5 | 4k | ⬜ |
| P4.2 | Wrap hotspot system_learning engines | `shadow_drift_analyzer.py`, `prompt_drift_detector.py`, `meta_learning_replay_binding.py`, `L6/utils/engines/meta_learning_bridge.py` | F5, F6 | 4k | ⬜ |
| P5.1 | Retire or re-purpose `consensus_otel.py` | `agentic_core/L6_observability/consensus_otel.py` + test suite | F6 | 3k | ⬜ |
| P6.1 | Re-gen ADG + update plan + write review doc | `docs/reports/plans/eval-meta-otel-gap-review.md` (NEW) | — | 4k | ⬜ |

**Phase-level summary table present** (constitutional gate requirement).

---

## Gap Register

| Gap | Owner | Trigger to close |
|-----|-------|------------------|
| G1: `scenario_runner.py` canonical output schema not yet defined for bus | Next-session Cascade (P2.1 entry) | Author-Gate decision in P2.1 on `EvaluationOutcome` shape |
| G2: Unknown whether `engines/meta_learning_bus.py` has capabilities not in `meta_learning/meta_learning_bus.py` | P1.1 diff | P1.1 reads both files and produces a symbol-level diff table |
| G3: No confirmation that `consensus_otel.py` is truly unused — may have dotted-string dynamic reference | P5.1 entry | ADG fan-in + `grep "consensus_otel"` across all `*.py` / `*.yaml` / `*.json` |

---

## ADG Author-Gate Decision Checkpoints

The only decision requiring explicit Author-Gate surfacing (confidence gap ≥0.12) is anticipated at **P1.2** — whether to delete `engines/meta_learning_bus.py` after reconciliation vs leave it as a pure re-export shim. That decision will be made inside that phase using the `author-gate-decision-gate` workflow.

All other phases are deterministic once W0 and P1.1 produce their evidence.

---

## Success Criteria (plan-wide)

1. New ADG snapshot shows **≥5** import edges from `apps_eval/*` into `system_learning.meta_learning.meta_learning_bus.*`.
2. New ADG snapshot shows **≥5** import edges from `apps_eval/*` into `agentic_core.adg.runtime.tracer`.
3. Tracing-marker import count in `system_learning` rises from 2 → **≥8** and in `agentic_core/L6_observability/` from 2 → **≥5**.
4. Exactly **1** non-shim `MetaLearningBus` class definition repo-wide.
5. OTel MCP `otel_spans_by_agent` returns non-zero spans from the `apps_eval`-origin agent class after a one-scenario smoke run.
6. Full pytest suite green; zero skip additions; no new P2/P3 anti-patterns introduced.

---

## Referenced Evidence Artifacts

- Debug query scripts (this session, to be cleaned up or promoted to `tools/diag/`):
  - `tools/debug/_q_eval_meta_otel_gap.py` — MV/P-view availability + violations profile + edge-type distribution
  - `tools/debug/_q_otel_coverage.py` — module-level tracing import coverage
  - `tools/debug/_q_otel_coverage2.py` — symbol-level side-effect coverage + eval→SL/L6 import matrix
- ADG snapshot: `artifacts/adg/adg_indexed_04222026_1939.sqlite`
