---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\exit-eval-v5-gap-c0aa47.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\exit-eval-v5-gap-c0aa47.md'
source_sha256: 054b870bfdc127bcff90105057a2024a349ab4ae48184b475e7be8999e4841ed
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Exit Eval & Control v5 — Gap Assessment & Implementation

- **Plan ID**: `exit-eval-v5-gap-c0aa47`
- **Spec source**: `docs/reference/05_Exit_Evaluation_&_Control/05_Live_Runtime_Exit_Control_&_Evaluation_v5.md`
- **Tier**: T3 (cross-layer L3+L5+config; safety-plane)
- **ADG snapshot**: `artifacts/adg/adg_indexed_04252026_0843.sqlite`
- **Status**: Active
- **Author**: Cascade

## SR_INTAKE

Spec defines runtime exit-evaluation (gates X1A–X1G), grader composition contract, dispositions (X3A–X3D + X3E break-glass), reason-code taxonomy, and the H1–H5 HITL re-clearance flow. Repo already contains a mature L3 `exit_eval/` pipeline + L5 `exit_control_hitl.py`. The gap is bounded: a small set of reason-code, rubric, and HITL-decision additions to reach v5 parity.

## Existing Repo Surface (verified)

| Spec slice | Existing implementation | Status |
|---|---|---|
| X1A policy_match | `graders/code_based.py` + `config/exit_eval_rubrics/x1a_v1.yaml` + `factory._build_graders_for_gate("X1A")` | ✅ |
| X1B schema/format/instr | `graders/code_based.SchemaGrader`, `LLMJudgeGrader` + `x1b_v1.yaml` | ✅ |
| X1C sandbox/mutation/env | requires site-specific overrides + `x1c_v1.yaml` | ✅ |
| X1D groundedness/citation | `graders/code_based.CitationGrader` + LLM judge + `x1d_v1.yaml` | ✅ |
| X1E trajectory | site-specific overrides + LLM coherence judge + `x1e_v1.yaml` | ✅ |
| X1F adversarial | `graders/adversarial.{PromptInjection,Jailbreak,SystemPromptLeak,Robustness}Grader` + `x1f_v1.yaml` | ✅ |
| X1G consistency pass^k | `consistency.PassKStore` + `consistency_redis.py` + `consistency_sqlite.py` | ⚠️ rubric file missing |
| Disposition X3A/B/C/D/E | `disposition.Disposition` + `pipeline._derive_disposition` | ✅ |
| Reason codes | `disposition.ReasonCode` (32 values) | ⚠️ 3 codes missing vs v5 |
| H1 freeze + H2 packet | `exit_control_hitl.ExitControlHITL.freeze_and_materialize` | ✅ |
| H4 decision taxonomy | `HumanDecision = {APPROVE, DENY, MODIFY_DIFF}` | ❌ 3 outcomes missing |
| H5 re-clearance — APPROVE | `_run_h5_policy` → `CLEARED_ALLOW`/`CLEARED_COMMIT` | ✅ |
| H5 re-clearance — MODIFY_DIFF | hard-blocks (deviation from spec) | ❌ |
| BUS P emission | `pipeline` → `bus.BusEmitter` | ✅ |
| OTel spans | `otel_spans.py` + `otel_sdk_sink.py` | ✅ |
| Break-glass X3E | `break_glass.py` + mandatory-deny override | ✅ |

## Identified Gaps

### Gap 1 — Reason codes missing (3 codes, low effort)

v5 §X3A enumerates `HARD_FAIL`, `TRAJECTORY_INVALID`, `ADVERSARIAL_DETECTED`. Current enum has none of these.

- `HARD_FAIL` — generic catch-all for any `is_hard_gate=True` failure that does not have a more specific code.
- `TRAJECTORY_INVALID` — distinct from `TRAJECTORY_SUSPECT`; structural rather than heuristic.
- `ADVERSARIAL_DETECTED` — generic adversarial signal beyond the specific `PROMPT_INJECTION_DETECTED` / `JAILBREAK_DETECTED` / `ADVERSARIAL_CRASH`.

### Gap 2 — X1G rubric file missing

`config/exit_eval_rubrics/x1g_v1.yaml` does not exist. The X1G consistency check is currently configured purely via `ConsistencyPolicy` dataclass. v5 §X1G specifies a rubric-shaped contract (`pass^k ≥ θ from X1A policy`); a `binary` rubric with one `passk_consistency` dimension matches the existing pipeline.

### Gap 3 — H4 decision taxonomy incomplete

v5 §H4 enumerates: `APPROVE`, `MODIFY_DIFF`, `REJECT`, `RETURN_TO_L1`, `REQUEST_MORE_EVIDENCE`.
Current `HumanDecision` enum: `APPROVE`, `DENY`, `MODIFY_DIFF`.

### Gap 4 — MODIFY_DIFF hard-blocked instead of re-cleared

v5 §L5 RE-CLEARANCE GATE explicitly says `MODIFY_DIFF -> L5 Re-clear -> Re-hydrate -> RESTART; re-run X1A/X1C/X1F on modified packet`. Current implementation hard-blocks MODIFY_DIFF. This is a spec deviation, not just a missing feature: the comment justifying the block ("Route proposed changes back to L2 for re-execution") is at odds with the spec which mandates an in-place re-clear before restart.

### Gap 5 — RETURN_TO_L1 / REQUEST_MORE_EVIDENCE outcomes

`ReClearOutcome` lacks the equivalents. Spec calls these out as terminal H5 outcomes that route back to L1 (replan) or to bounded re-entry (more evidence).

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | W1.1 W1.2 | Reason-code parity (Gap 1) + X1G rubric (Gap 2) | ~3000 | Todo | New codes importable; x1g_v1.yaml loads via `load_rubric`; existing tests still green |
| W2 | W2.1 W2.2 W2.3 | H4 decision expansion (Gap 3+5) + MODIFY_DIFF re-clearance hook (Gap 4) | ~6000 | Todo | New decisions/outcomes on enums; `validate_and_reclear` calls re-clear callback when supplied; old tests still pass |
| W3 | W3.1 | Test hardening — add v5 parity tests for new surface | ~3000 | Todo | At least 8 new tests covering each new code/decision/outcome + MODIFY_DIFF callback path; targeted pytest green |
| W4 | W4.1 | Commit + push | ~500 | Todo | All changes in two logical commits, pushed to `origin/main` |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | Add reason codes | `agentic_core/L3_orchestration/exit_eval/disposition.py` | None | 800 | Todo |
| W1.2 | X1G rubric file | `config/exit_eval_rubrics/x1g_v1.yaml` | Need to ensure rubric loader accepts shape; `binary` composition w/ one dim | 1200 | Todo |
| W2.1 | Expand `HumanDecision` | `agentic_core/L5_safety/enforcement/exit_control_hitl.py` | DENY back-compat alias for REJECT | 1500 | Todo |
| W2.2 | Expand `ReClearOutcome` | same file | Add `RETURN_TO_L1`, `REQUEST_MORE_EVIDENCE`, `RECLEAR_RESTART` | 1500 | Todo |
| W2.3 | MODIFY_DIFF re-clear callback | same file | Optional `reclear_callback` ctor param; preserve hard-block when not supplied | 3000 | Todo |
| W3.1 | Tests | `tests/unit/agentic_core/L5_safety/enforcement/test_exit_control_hitl.py` + new `tests/unit/agentic_core/L3_orchestration/exit_eval/test_v5_parity.py` | Need a stub gate-result for HITL tests | 3000 | Todo |
| W4.1 | Commit + push | git | None | 500 | Todo |

## Gap Register

| ID | Gap | Severity | Wave |
|---|---|---|---|
| GAP-1 | 3 missing reason codes | low | W1 |
| GAP-2 | x1g rubric file | medium | W1 |
| GAP-3 | H4 decision taxonomy partial | medium | W2 |
| GAP-4 | MODIFY_DIFF spec deviation | high | W2 |
| GAP-5 | Missing H5 outcomes | medium | W2 |

## ADG_HOTSPOT_REPORT (rank by archetype + impact)

| Rank | File | Layer | Archetype | Surface | Fan-in | Impact | Wave |
|---|---|---|---|---|---|---|---|
| 1 | `disposition.py` | L3 | CENTRAL_DEPENDENCY | Execution+Security | high | 1.0 | W1 |
| 2 | `exit_control_hitl.py` | L5 | SAFETY_GATEKEEPER | Security+Write | medium | 0.95 | W2 |
| 3 | `config/exit_eval_rubrics/` | config | STATE_NODE | State | low | 0.4 | W1 |

## ADG_GRAPH_LAYER_EVIDENCE

- `mv_exit_disposition_coverage` — confirms every `Disposition` enum value is referenced; new reason codes must be referenced too (W3 tests cover).
- `mv_eval_coverage_by_path` — `agentic_core/L3_orchestration/exit_eval/disposition.py` already exercised; W1.1 keeps coverage neutral.
- `mv_hitl_reclearance_gaps` — currently flags `MODIFY_DIFF` as a gap; closing W2.3 should reduce this MV count.
- Semantic edges: `flows_to` from `pipeline._derive_disposition` → `Disposition` enum values; W1.1 must not introduce orphan codes (each new code must flow into at least one fail path or test).
- P-views: this work touches **none** of `v_p0_*` / `v_p1_*` (no new architectural debt).

## Out of Scope (deferred)

- BUS T trajectory_class history backfill
- Golden-set promotion candidate pipeline
- Judge calibration cadence automation (covered by `judge-calibration-cadence.md` rule already)
- Sandbox capability-token rotation policy

These are flagged as `NEXT_STEP` markers, not part of W1–W4.
