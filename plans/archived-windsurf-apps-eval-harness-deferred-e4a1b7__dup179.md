---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-eval-harness-deferred-e4a1b7__dup179.md'
original_relative_path: 'apps-eval-harness-deferred-e4a1b7__dup179.md'
source_sha256: fc8a2e9ace191d2917f10e8469886fe8168d8c7baf45e3511fff5aeb533fcc2f
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps_* Eval Harness — Deferred Scope Execution Plan

**Slug:** `apps-eval-harness-deferred-e4a1b7`
**Created:** 2026-05-03
**Status:** Live
**Parent plan:** `.windsurf/plans/apps-eval-harness-parity-f8d4a2.md` (Completed 2026-05-03)
**Owner:** Cascade
**Authority:** This plan consumes only the DEFERRED_SCOPE markers emitted during the parent plan's execution plus ancillary follow-ups surfaced by the `check_app_domain_harness_parity` CI gate.

## 1. Problem Statement

The parent plan `apps-eval-harness-parity-f8d4a2` closed 8 of 10 audit BLOCKERs across 9 wave-phases (W1, W2.P3, W2.P4, W2.P5, W4.P2, W4.P3, W5.P6, W5.P7, W6). Six DEFERRED_SCOPE items and one still-open BLOCKER (#4 C0 FEC producer binding) remain. The `check_app_domain_harness_parity` gate currently surfaces 6 WARNs that are the actionable backlog for these items.

This plan picks up the deferred work in six waves, scoped so each wave closes one axis of the remaining gap end-to-end.

## 2. Goals

- Close the 2 `NO_CERT_EXIT_INVOCATION` WARNs by adopting `maybe_invoke_exit_eval` in both per-app cert entrypoints.
- Close the 4 `NO_UNIMPL_JUDGES` WARNs by landing minimal, deterministic, type-safe stubs for each judge (calibration + real scoring logic remains deferred to a future holdout-backed plan).
- Extend `ScoreDimension.grader_type` with the 3 canonical Anthropic grader types (`tool_calls`, `state_check`, `transcript`) and route the evaluator dispatch.
- Land observability scaffolding: judge-human agreement tracker skeleton, score-trend anomaly detector skeleton, weekly rollup of `eval_harness_outcome` ledger.
- Promote the `check_app_domain_harness_parity` gate from advisory to fail-closed (with a rollback env-var), once all WARNs are green.

## 3. Non-Goals (carried forward from parent plan W6)

- **C0 FinalEvidenceContract producer wiring** for the 5 grounded apps (`apps_research`, `apps_rfp`, `apps_qna`, `apps_exec`, `apps_underwriting_ai`). Requires per-app retrieval-integration tracing and owns its own plan.
- **Real LLM-judge scoring logic** for the 4 stubbed judges (Spearman ≥ 0.80 calibration against a human-labeled holdout). Stubs land here; real logic owns its own plan with calibration-cadence budget.
- **Holdout vs. dev eval-set separation** + **production-log mining** + **SSOT consolidation of legacy policy/threshold YAMLs**. Each owns its own plan with PII-redaction and deprecation-shim Author-Gates.
- **Rubric dimension deletion** (parent W6.P3 fence).
- **Route authority or durable-write widening** (parent W6.P1/P6 fences).

## 4. Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.P1–W1.P3 | Per-app cert-entry adoption of `maybe_invoke_exit_eval` (apps_qna + apps_underwriting_ai) | ~6k | `apps_shared.cert.exit_eval_hook` already landed in parent plan; per-app `__main__` / cert entry is the only missing glue | Todo | Gate `NO_CERT_EXIT_INVOCATION` returns zero WARNs |
| W2 | W2.P1–W2.P5 | LLM-judge stubs (4 dims) — minimal deterministic stubs at canonical import paths | ~8k | Generic `read_dim_score_from_output` grader covers score reading; stubs only need to declare an importable module | Todo | Gate `NO_UNIMPL_JUDGES` returns zero WARNs |
| W3 | W3.P1–W3.P4 | Canonical Anthropic grader types (`tool_calls`, `state_check`, `transcript`) + trajectory match-mode + dispatch | ~12k | `ScoreDimension.grader_type` is a string today — extension is additive; per-app rubric migrations deferred | Todo | New enum values accepted by schema validator; evaluator dispatches without regressions; new verifier gate passes |
| W4 | W4.P1–W4.P4 | Judge discipline scaffolding — categorical score bands schema, retry-on-low policy, OTEL domain attrs, tracked_metrics | ~10k | OTEL span attribute budget allows 6 new keys per span; retry cap 1 per dim per run | Todo | New schema fields accepted; retry policy runs end-to-end; OTEL spans carry new attrs in test |
| W5 | W5.P1–W5.P3 | Observability — judge-human agreement tracker skeleton, score-trend anomaly detector skeleton, `eval_harness_outcome` weekly rollup | ~7k | Ledger writer already exists; skeletons write to `artifacts/calibration/` | Todo | All three scripts runnable; produce shape-valid JSON outputs |
| W6 | W6.P1–W6.P3 | CI gate promotion — advisory → fail-closed + pre-commit wiring + close-out tests | ~4k | All prior waves green; `APP_DOMAIN_HARNESS_PARITY_FAIL_CLOSED` already supported by the gate | Todo | `run_contract_gates.py` invokes the gate; pre-commit fails on ERROR severity |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Adopt hook in `apps_qna/__main__.py` | `apps_qna/__main__.py` or cert entry; new test | Must not alter SINGLE_STEP behavior for non-cert runs | 2k | Todo |
| W1.P2 | Adopt hook in apps_underwriting_ai cert entrypoint | `apps_underwriting_ai/integrations/execution_adapter.py` (or __main__); new test | Regulated-domain compliance — fail-soft strictly required | 2k | Todo |
| W1.P3 | Verification — gate green | `tests/_apps_contract/test_w2p3_exit_eval_hook.py` gate-green assertion | — | 1k | Todo |
| W2.P1 | `apps_rg.engines.judges.executive_positioning_judge` stub | new file + test | Stub must be importable and return sane UNKNOWN sentinel | 2k | Todo |
| W2.P2 | `apps_lic.engines.judges.response_likelihood_judge` stub | new file + test | — | 1.5k | Todo |
| W2.P3 | `apps_lic.engines.judges.brand_voice_judge` stub | new file + test | — | 1.5k | Todo |
| W2.P4 | `apps_rfp.engines.judges.win_theme_alignment_judge` stub | new file + test | — | 1.5k | Todo |
| W2.P5 | Verification — `NO_UNIMPL_JUDGES` gate green | update gate test expectations | — | 1k | Todo |
| W3.P1 | Extend `grader_type` enum | `agentic_core/L4_state/contracts/app_domain.py` score-dimension validation | Must accept new types; legacy rubrics unchanged | 3k | Todo |
| W3.P2 | Evaluator dispatch for `tool_calls` / `state_check` / `transcript` | `agentic_core/L3_orchestration/exit_eval/v6/app_grader_registry.py` | Dispatch fails-soft to UNKNOWN for unregistered graders | 4k | Todo |
| W3.P3 | Trajectory match-mode field + enum | `agentic_core/L4_state/contracts/app_domain.py` | Optional on ScoreDimension; default `none` | 2k | Todo |
| W3.P4 | Verifier gate `check_grader_type_coverage` | `ops_scripts/ci/check_grader_type_coverage.py` (advisory) | Advisory only; no rubric-migration enforcement | 3k | Todo |
| W4.P1 | Categorical `score_bands` optional schema field | `agentic_core/L4_state/contracts/app_domain.py` | Back-compat with float `min_required_score` | 3k | Todo |
| W4.P2 | Retry-on-low judge policy | `agentic_core/L3_orchestration/exit_eval/v6/app_specific_evaluator.py` | Idempotent; 1 retry per dim max | 3k | Todo |
| W4.P3 | OTEL domain-metric span attrs | `agentic_core/L3_orchestration/exit_eval/v6/app_domain_otel.py` | Respect span attr budget | 2k | Todo |
| W4.P4 | tracked_metrics (latency / cost / tokens) per-domain | OTEL span keys + pipeline serializer | Anthropic canonical keys | 2k | Todo |
| W5.P1 | Judge-human agreement tracker skeleton | `ops_scripts/calibration/judge_agreement_tracker.py` | Skeleton only; real Spearman calc deferred | 2k | Todo |
| W5.P2 | Score-trend anomaly detector skeleton | `ops_scripts/calibration/eval_trend_anomaly_detector.py` | Rolling windows 1h/6h/24h | 3k | Todo |
| W5.P3 | `eval_harness_outcome` weekly rollup | `ops_scripts/calibration/eval_harness_weekly_report.py` | Reads the W5.P7 ledger | 2k | Todo |
| W6.P1 | Promote gate to fail-closed | `ops_scripts/ci/check_app_domain_harness_parity.py` + `run_contract_gates.py` | Rollback via `APP_DOMAIN_HARNESS_PARITY_FAIL_CLOSED=0` | 2k | Todo |
| W6.P2 | Pre-commit wiring | `.pre-commit-config.yaml` | Don't block on WARN; block on ERROR | 1k | Todo |
| W6.P3 | Close-out tests | update parity-gate tests for fail-closed mode | — | 1k | Todo |

## 6. Wave Detail

### Wave 1 — Per-app Exit Hook Adoption (closes BLOCKER #5 end-to-end)

**Entry gate:** Parent plan W2.P3 landed (`apps_shared.cert.exit_eval_hook` exists + both cert_route_registry.yaml files declare `invoke_exit_eval: true`).
**Exit gate:** `check_app_domain_harness_parity` reports zero `NO_CERT_EXIT_INVOCATION` WARNs.

### Wave 2 — LLM-Judge Stubs (closes NO_UNIMPL_JUDGES WARNs)

**Entry gate:** Gate currently surfaces 4 `NO_UNIMPL_JUDGES` WARNs at exact import paths.
**Exit gate:** All 4 paths importable; `_resolve_judge_importable` returns `(True, …)` for each; gate reports zero `NO_UNIMPL_JUDGES` WARNs.

Stubs return the W1 generic-grader sentinel (UNKNOWN) so the existing W1 fallback chain continues to read from `run_context["output"]["dim_scores"]`. This keeps runtime behavior IDENTICAL to pre-stub state; the stubs only satisfy importability. Real scoring logic is deferred to a calibration-backed future plan.

### Wave 3 — Canonical Grader Types

**Entry gate:** None. Additive schema change.
**Exit gate:** `agentic_core.L4_state.contracts.app_domain.ScoreDimension` accepts `tool_calls`, `state_check`, `transcript`, `trajectory_match` strings; evaluator dispatches them (fails soft to UNKNOWN if no concrete grader registered); new advisory gate passes.

### Wave 4 — Judge Discipline Scaffolding

**Entry gate:** W3 exit green (evaluator dispatch understands new types).
**Exit gate:** Optional `score_bands` field accepted; retry-on-low runs at most once per dim per run; OTEL span attrs include new domain-metric keys; tracked_metrics serialized.

### Wave 5 — Observability

**Entry gate:** W5.P7 ledger (parent plan) is populated.
**Exit gate:** Three skeleton scripts exist under `ops_scripts/calibration/`, pass their own smoke tests, and produce shape-valid JSON outputs.

### Wave 6 — Gate Promotion

**Entry gate:** All prior waves green.
**Exit gate:** Gate runs fail-closed in `run_contract_gates.py`; pre-commit wiring blocks ERROR findings; close-out tests green.

## 7. Gap → Wave Traceability

| Gap | Parent plan status | This plan wave |
|---|---|---|
| W2.P3 per-app hook adoption | DEFERRED in parent | W1 |
| NO_UNIMPL_JUDGES × 4 | DEFERRED in parent | W2 |
| W3.P1-P4 grader-type schema | DEFERRED in parent | W3 |
| W4.P1 score bands, W4.P5 retry, W4.P7 OTEL attrs, W4.P8 tracked_metrics | DEFERRED in parent | W4 |
| W4.P4 judge-human agreement skeleton, W4.P6 trend anomaly, weekly rollup | DEFERRED in parent | W5 |
| CI gate promotion from advisory to fail-closed | New follow-up | W6 |
| **Still-deferred (multi-session)** | DEFERRED from this plan too | — |
| BLOCKER #4 C0 FEC producer binding for 5 grounded apps | DEFERRED | separate plan |
| Real judge scoring logic (Spearman calibration) | DEFERRED | separate plan |
| Holdout / production-log mining / SSOT consolidation | DEFERRED | separate plan |

## 8. Governance & Cross-References

- Constitutional §22 (ADG graph-layer primary)
- Constitutional §24 (deferred-scope capture) — this plan IS the pickup of those markers
- Constitutional §25 (MCP serialization — remote MCPs serial)
- Constitutional §31 (SSOT folder routing — all new scripts land under `ops_scripts/` or `tools/`)
- Constitutional §32 (Fort Knox certification discipline — W6.P5 parent fence unchanged)
- ADR-050 (intelligence-ledger-family — W5 extends the parent's ledger integration)
- `author-gate-enforcement.md` — any per-dim threshold change (none in this plan) requires its own Author-Gate
- `notion-plan-wave-deferral.md` — mid-plan Notion writes forbidden; batched at completion

## 9. Author-Gate Decision Points (anticipated)

| Wave.Phase | Decision | Trigger | Expected Disposition |
|---|---|---|---|
| W4.P1 | Categorical score-bands numeric-vs-enum | Schema shape call | Likely `[integer 0-3]` per Anthropic precedent |
| W6.P1 | Promote to fail-closed vs. keep advisory one more cycle | Risk-tier promotion | Depends on gate stability at that point |

## 10. Risks

| Risk | Mitigation |
|---|---|
| Judge stubs confused with real implementations | Every stub has a module docstring declaring STUB status + `IS_STUB = True` constant; gate check in W2 |
| `ScoreDimension.grader_type` enum extension breaks legacy rubric YAMLs | All new types are additive; existing `deterministic`, `llm_as_judge`, `hybrid` keep working |
| OTEL span attr additions exceed budget | W4.P3 stays under 6 new keys; verified by test |
| Gate promotion surfaces unforeseen ERRORs in CI | W6.P1 ships with `APP_DOMAIN_HARNESS_PARITY_FAIL_CLOSED=0` rollback; ops can revert without code change |

## 11. Timeline (indicative)

- W1 + W2 (closes the two WARN classes in the gate): 1 session
- W3: 1 session (schema + dispatch is additive but testing across 8 apps is non-trivial)
- W4: 1 session
- W5 + W6: 1 session
- **Total: 4 sessions** in the worst case; this session targets W1 + W2 + W3 fully, W4-W6 as budget permits

## 12. Metadata

- Plan file path: `.windsurf/plans/apps-eval-harness-deferred-e4a1b7.md`
- Notion Plans row: created 2026-05-03 with Status=Live
- Parent plan row: flipped to Status=Completed 2026-05-03
- Template: `.windsurf/templates/execution-plan-template.md`

## AG_QUEUE_SEED

None in this plan — all decisions that were Author-Gate class have been pre-decided by the parent plan's AG packets (W2.P3 picked D, W2.P4 picked B, W4.P2 picked A, W4.P3 picked A). Any new Author-Gate points encountered during execution will be surfaced inline per `author-gate-queue-drain.md`.
