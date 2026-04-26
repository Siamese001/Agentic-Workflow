# Apps Metrics & Feedback Substrate — Wire `apps_shared` Instrumentation Into All `apps_*`

Status: **SUPERSEDED 2026-04-26**
Superseded By: `.windsurf/plans/apps-agentic-core-convergence-b4e5f1.md`
Reason: Author-Gate audit revealed this plan would have entrenched parallel observability in `apps_shared` while bypassing canonical `agentic_core/L6_observability/`. Five structural gaps (G1 ghost UWAI, G2 parallel observability, G3 L4/UWG bypass, G4 dead `agentic_core` capability, G5 SovereignBaseAgent skip) must be resolved first. Metrics/feedback returns as W6 inside the convergence program, riding canonical L6 surfaces.
Original Owner: Cascade
Original Tier: T3
Original Decision: Author-Gate `architecture_choice` 2026-04-26 — Option A "Shared substrate in `apps_shared/`" selected (confidence 0.78, gap 0.16, precedent=none)
Replanning Decision: Author-Gate `architecture_choice` 2026-04-26 — Option A "Replan as agentic_core convergence program" selected (confidence 0.81, gap 0.19)
Audit Evidence: `docs/reports/plans/apps-agentic-core-coverage-audit-b4e5f1.md`
SSOT: `.windsurf/plans/apps-metrics-feedback-substrate-7c9e3d.md` (retained for traceability — DO NOT execute)

---

## Goal

Enhance metrics emission and feedback loops across all `apps_*` (`apps_eval`, `apps_exec`, `apps_lic`, `apps_research`, `apps_rfp`, `apps_rg`, `apps_underwriting_ai`) so each governed run produces:

1. **Metrics** — counters / timers / histograms emitted via the existing `AppsTracingMixin` + `open_telemetry_tracing_adapter_util` substrate, with a standard metric vocabulary.
2. **Feedback** — outcome capture routed through the existing `FeedbackLoop` substrate (`apps_shared/types/feedback_loop_types.py`) into:
   - L6 system_learning (`system_learning/runtime_hitl_consumer.py` + `system_learning/meta_learning/`)
   - Eval rubrics consumers
   - The intelligence ledger family (ADR-050, `artifacts/ledgers/`) where mappable
3. **Single insertion point** — extend `apps_shared/integrations/governed_app_runner.py:GovernedAppRunner.run_governed_core()` so every governed app inherits both behaviors without per-app rewiring of `engines/`.

Non-goal: building a new metrics backend, displacing OTEL, or reworking the L5/L6 doctrine described in `docs/reference/00_L5_Policy_Plane/00.x_*.md`.

---

## Existing Substrate (reuse, do not duplicate)

| Surface | Path | Status |
|---|---|---|
| Tracing mixin | `apps_shared/mixins/apps_tracing_mixin.py` | Present, used by 1 caller (`apps_lic/engines/control_plane.py`) |
| OTEL adapter | `apps_shared/utils/open_telemetry_tracing_adapter_util.py` | Present |
| Metric type util | `apps_shared/utils/metric_type_util.py` | Present (233 matches, vocabulary defined) |
| Feedback loop | `apps_shared/types/feedback_loop_types.py` (`FeedbackLoop`, `QualityFeedback`, `AdaptiveThresholds`) | Present, **zero callers in `apps_*`** |
| Feedback orchestrator types | `apps_shared/types/feedback_loop_orchestrator_types.py` | Present, zero callers in `apps_*` |
| Governed runner base | `apps_shared/integrations/governed_app_runner.py:GovernedAppRunner` | Inherited by every `apps_*/integrations/governed_*_run.py` |
| L6 OTEL ingest | `agentic_core/L6_observability/otel_runtime_ingest.py` | Receives spans |
| L6 decision events | `agentic_core/L6_observability/decision_events_schema.py` | Schema for outcome events |
| Runtime HITL consumer | `system_learning/runtime_hitl_consumer.py` | L6 feedback sink |

---

## ADG_GRAPH_LAYER_EVIDENCE

(Constitutional §22 — populated during Phase 0 ADG queries.)

| Artifact | Source | Use in this plan |
|---|---|---|
| `mv_graph_reverse_dependency_hotspots` (filtered to `governed_app_runner`) | ADG materialized view | Confirm fan-in of `GovernedAppRunner` across `apps_*` (expected ≥7) — drives the single-insertion-point claim |
| `mv_graph_chokepoint_bridges` | ADG materialized view | Verify `governed_app_runner.run_governed_core` is the chokepoint between L_APP and L2/L5/L6 |
| `mv_dependency_cone_risk` (root = `apps_shared.types.feedback_loop_types`) | ADG materialized view | Sized blast radius of feedback substrate before wiring |
| Semantic edges: `flows_to`, `emits_side_effect`, `writes_to` | ADG semantic edges | Trace metric/feedback emission path from runner → OTEL → L6 |
| `v_p1_zero_caller_infra` | P-view | Confirms `feedback_loop_types` is currently zero-caller from `apps_*` (justifies wave 1) |
| `v_p2_duplicated_adapters` | P-view | Sanity-check that no per-app metric duplicate already exists |

Phase 0 (ADG green-light) MUST capture these views into `docs/reports/plans/apps-metrics-feedback-substrate-7c9e3d-evidence.md` before Phase 1 begins.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W0 | P0.1 | ADG green-light + evidence capture | ~3k | Redis hot cache or ADG SQLite healthy | Todo | Hotspot/chokepoint claims proven; evidence MD written |
| W1 | P1.1, P1.2 | Extend `GovernedAppRunner` with metrics + feedback hooks (single insertion point) | ~8k | `AppsTracingMixin` and `FeedbackLoop` APIs are stable | Todo | Runner emits standard metrics + writes feedback record per run; existing tests still pass |
| W2 | P2.1..P2.7 | Per-app activation: each `apps_*/integrations/governed_*_run.py` inherits new behavior; verify metric vocabulary | ~6k | W1 complete | Todo | All 7 apps emit canonical metrics under `apps.<name>.*`; feedback rows captured |
| W3 | P3.1, P3.2 | L6 sink wiring: feedback → `runtime_hitl_consumer` + ledger router | ~5k | L6 OTEL ingest reachable | Todo | Feedback rows appear in L6 + at least one ledger (`tool_routing` or `progress_eta`) |
| W4 | P4.1, P4.2 | Tests + CI gate: `check_apps_metrics_emission.py`, contract tests per app | ~4k | pytest_mcp healthy | Todo | New gate green; per-app contract test green; coverage ≥80% on touched code |
| W5 | P5.1 | Verification + writeback (Memory + Notion ADR + MCP Registry note if needed) | ~2k | All prior waves done | Todo | DECISION_CAPTURED + WRITEBACK receipts emitted |

Total est: ~28k tokens.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P0.1 | ADG evidence capture | `docs/reports/plans/apps-metrics-feedback-substrate-7c9e3d-evidence.md` (new) | ADG MCP must be healthy; Redis cache fallback | 3k | Todo |
| P1.1 | Extend `GovernedAppRunner` with `AppsTracingMixin` mixin + standard metric emission helper (`_emit_run_metrics()`) | `apps_shared/integrations/governed_app_runner.py` | Mixin order must precede other base classes; preserve existing behavior | 4k | Todo |
| P1.2 | Add `FeedbackLoop` integration: each `run_governed_core()` writes a `QualityFeedback` after `_translate()` | `apps_shared/integrations/governed_app_runner.py`, new `apps_shared/integrations/_feedback_emit.py` (small helper) | Feedback metric vocabulary must align with `metric_type_util` constants | 4k | Todo |
| P2.1 | `apps_eval` activation + smoke test | `apps_eval/integrations/governed_eval_exception.py`, `apps_eval/integrations/eval_ingress_runner.py` | Eval has its own engines — only the runner-side change | 1k | Todo |
| P2.2 | `apps_exec` activation | `apps_exec/integrations/governed_exec_run.py` | None | 0.7k | Todo |
| P2.3 | `apps_lic` activation (already touches `AppsTracingMixin` in `control_plane.py` — verify no double-instrumentation) | `apps_lic/integrations/governed_lic_run.py`, `apps_lic/engines/control_plane.py` | Avoid double-emission | 1.2k | Todo |
| P2.4 | `apps_research` activation | `apps_research/integrations/governed_research_run.py` | None | 0.7k | Todo |
| P2.5 | `apps_rfp` activation | `apps_rfp/integrations/governed_rfp_run.py` | None | 0.7k | Todo |
| P2.6 | `apps_rg` activation | `apps_rg/integrations/governed_rg_run.py`, `apps_rg/integrations/rg_ingress_runner.py` | RG has 45 engines — none touched, just runner | 1k | Todo |
| P2.7 | `apps_underwriting_ai` activation | `apps_underwriting_ai/integrations/__init__.py` (verify it inherits the runner) | UWAI may not yet use `GovernedAppRunner` — confirm first | 0.7k | Todo |
| P3.1 | Wire `FeedbackLoop` sink to `system_learning/runtime_hitl_consumer.py` (existing consumer is the canonical L6 ingress) | new `apps_shared/integrations/_feedback_l6_bridge.py` | Bridge must be optional + fail-soft | 3k | Todo |
| P3.2 | Map a subset of feedback events to ADR-050 ledgers (`tool_routing`, `progress_eta`) via existing `LedgerConsulter` writers | `apps_shared/integrations/_feedback_ledger_router.py` (new) | Only emit to ledgers where the feedback truly fits the schema; do not overload | 2k | Todo |
| P4.1 | New CI gate `ops_scripts/ci/check_apps_metrics_emission.py` — fails if any `governed_*_run.py` does not inherit `GovernedAppRunner` (or equivalent metric path) | new gate | Pre-commit + run_contract_gates wiring | 2k | Todo |
| P4.2 | Contract test `tests/apps_shared/test_governed_runner_metrics_feedback.py` + per-app smoke `tests/<app>/test_metrics_emission.py` | tests | Reuse existing `pytest_mcp` infra; no skip/xfail | 2k | Todo |
| P5.1 | Verification (`run_contract_gates.py`, full `pytest -k metrics_emission`) + writeback: DECISION_CAPTURED already emitted, plus Memory `ProceduralPattern:AppsMetricsFeedbackSubstrate`, Notion ADR row in ADR Registry (`ADR-NNN-apps-metrics-substrate`) | `docs/architecture/adr/`, Memory MCP, Notion ADR Registry | None | 2k | Todo |

---

## Gap Register

- **G1** — `apps_underwriting_ai/integrations/__init__.py` currently 1 byte; need to confirm whether UWAI runs via `GovernedAppRunner` at all. If not, P2.7 may need to upgrade UWAI to use the runner first (out-of-scope expansion → would emit a `DEFERRED_SCOPE:` marker if so).
- **G2** — `apps_lic/engines/control_plane.py` already imports `AppsTracingMixin` directly. P2.3 must verify the mixin isn't applied twice via runner inheritance + direct use.
- **G3** — Feedback → ledger mapping is opportunistic; only `tool_routing` and `progress_eta` ledgers fit cleanly. Other 8 ledgers in ADR-050 family are out of scope for this plan.
- **G4** — `metric_type_util.py` defines vocabulary already; this plan does not extend it. If new metric names are needed, that becomes a separate `parameter_tune` Author-Gate.

---

## Rollback Checkpoints

| Checkpoint | Trigger | Action |
|---|---|---|
| End of W1 | New runner tests fail | Revert `governed_app_runner.py` change; keep `_feedback_emit.py` shelved |
| End of W2 | Any per-app smoke fails | Disable feedback emission via env flag `APPS_FEEDBACK_DISABLED=1`; keep tracing |
| End of W3 | L6 ingest hangs (per `mcp-serialization.md`) | Make L6 bridge async-fire-and-forget with a 500 ms budget; do not block the run |
| End of W4 | New CI gate red on existing apps | Mark gate `manual` stage initially; promote to `pre-commit` after one clean cycle |

---

## Constitutional / Doctrinal Alignment

- §17 Memory lifecycle — write `ProceduralPattern:AppsMetricsFeedbackSubstrate` after P5.1.
- §22 ADG graph-layer primary driver — fulfilled by ADG_GRAPH_LAYER_EVIDENCE section + Phase 0.
- §24 Deferred-scope capture — if G1 expands UWAI scope, emit `DEFERRED_SCOPE:` marker rather than silently widening.
- §25 MCP serialization — L6 bridge in P3.1 must be local SQLite/file write, not an MCP call from inside the runner hot path.
- ADR-050 intelligence ledger family — feedback router in P3.2 reuses existing ledger writers; does not create new ledgers.
- v33 §6D evaluation-promotion gate — feedback signals from this substrate become the candidate input for any future eval-promotion proposal (out of scope here).

---

## Acceptance Criteria

1. `GovernedAppRunner.run_governed_core()` emits a span hierarchy `apps.<name>.governed_e2e` with standard attributes (`run_id`, `route_id`, `intent`, `support_target`, `duration_ms`, `outcome`).
2. Each governed run records exactly one `QualityFeedback` via `FeedbackLoop` keyed by `app_name`.
3. All 7 `apps_*` show metrics + feedback in a smoke test (`pytest -k metrics_emission`).
4. CI gate `check_apps_metrics_emission.py` is green.
5. No existing tests in `apps_*` regress.
6. No raw `opentelemetry` import is introduced outside `apps_shared/utils/open_telemetry_tracing_adapter_util.py` (preserves the existing canonical-adapter rule baked into `apps_tracing_mixin.py`).
7. Writeback complete: ADR row in Notion ADR Registry, Memory `ProceduralPattern:AppsMetricsFeedbackSubstrate`, plan status updated to Done.

---

## Open Author-Gates (anticipated downstream)

- If P2.7 reveals UWAI does not use `GovernedAppRunner`: **architecture_choice** Author-Gate on whether to upgrade UWAI now or defer.
- If P3.2 reveals feedback events match more than 2 ledgers: **architecture_choice** on routing fan-out.
- If `metric_type_util` vocabulary needs extension: **parameter_tune** Author-Gate.

These are not pre-decided; they will be opened only if the trigger fires during execution.
