---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-eval-harness-closeout-b7c9d2__dup178.md'
original_relative_path: 'apps-eval-harness-closeout-b7c9d2__dup178.md'
source_sha256: d90f04575098590f274f72844b4cb370681dc50afda9752b260a28921d0683fa
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps_* Eval Harness — Closeout Plan

**Slug:** `apps-eval-harness-closeout-b7c9d2`
**Created:** 2026-05-03
**Status:** Live
**Parent plans:**
- `.windsurf/plans/apps-eval-harness-parity-f8d4a2.md` (Completed)
- `.windsurf/plans/apps-eval-harness-deferred-e4a1b7.md` (Completed)

**Owner:** Cascade

## 1. Problem Statement

The parent plan `apps-eval-harness-parity-f8d4a2` defined ~30 wave-phases. Direct execution closed 9; the continuation plan `apps-eval-harness-deferred-e4a1b7` closed 13 more, leaving 8 still-open parent-plan phases. This closeout plan executes the tractable subset of the remaining 8 and explicitly scopes the rest out to dedicated future plans.

## 2. Goals

Close the last tractable deferred items from the parent plan:

- **W3.P5** RAG metric dims on 5 grounded apps with OpenAI baselines (0.85 / 0.70 / 0.80)
- **W5.P3** Per-app capability-vs-regression taxonomy tagging
- **W5.P5** Per-app RUNBOOK Eval Harness sections (8 apps)
- **W5.P4** Legacy policy/threshold YAML deprecation notices + migration shim
- **W2.P6** End-to-end cert hook verification (extended integration tests)

## 3. Non-Goals (explicitly deferred to dedicated future plans)

- **BLOCKER #4 — W2.P1/P2 C0 FinalEvidenceContract producer binding** for 5 grounded apps. Requires per-app retrieval-integration tracing and is deep cross-cutting work.
- **W5.P1 Holdout vs dev eval-set separation**. Requires fixture restructure + CI-integration policy.
- **W5.P2 Production-log mining**. Requires PII-redaction policy + Author-Gate per sample class.
- **Real LLM-judge scoring logic** with Spearman ≥ 0.80 calibration. Stubs landed in `e4a1b7` W2; real logic needs human-labeled holdout (W5.P1 blocker).
- **Rubric dimension deletion** (parent W6.P3 fence). Additions only.

## 4. Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.P1–W1.P2 | RAG metric dims on 5 grounded apps + validation | ~8k | Rubric schema already supports additive dim additions; producers populate dim_scores per W1/e4a1b7 contract | Todo | Each of apps_qna/research/rfp/exec/underwriting_ai rubric carries context_recall/context_precision/answer_relevancy dims with OpenAI baselines |
| W2 | W2.P1–W2.P2 | Capability-vs-regression taxonomy tagging | ~5k | ScoreDimension extension already lives in e4a1b7 pattern | Todo | Every rubric dim across 8 apps has `taxonomy_class`; gate verifies coverage |
| W3 | W3.P1 | Per-app RUNBOOK Eval Harness sections | ~4k | Existing RUNBOOK.md files under each app | Todo | 8 apps have a "## Eval Harness" section following the shared template |
| W4 | W4.P1 | Legacy YAML deprecation notices | ~4k | Legacy `*_policies.yaml` / `*_thresholds.yaml` loaders exist in a few apps | Todo | Deprecation warnings emit on legacy-file load; migration path documented |
| W5 | W5.P1 | E2E cert-hook verification extension | ~4k | apps_qna + apps_underwriting_ai cert entrypoints already adopted the hook (e4a1b7 W1) | Todo | Integration tests exercise the full SINGLE_STEP cert → Exit hook → ledger path |
| W6 | W6.P1 | Doctrinal fence — explicit non-goals | ~1k | No execution | Todo | Non-goals enumerated with pointers to future-plan placeholders |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Add RAG dims to 5 grounded apps' rubrics | `apps_{qna,research,rfp,exec,underwriting_ai}/config/domain_contract/eval_rubrics.yaml` | Additions only, preserve existing dims; dim weights must sum ≤ 1.0 | 6k | Todo |
| W1.P2 | Verify rubric shapes + gate | new test + existing gate verifies RAG-dim presence per app | Dim IDs must match the OpenAI canonical names exactly | 2k | Todo |
| W2.P1 | Add `taxonomy_class` field to ScoreDimension | `agentic_core/L4_state/contracts/app_domain.py` — vocab + validation | Back-compat: default empty; optional field | 2k | Todo |
| W2.P2 | Migrate rubrics + add gate TAXONOMY_COVERAGE | 8 apps' eval_rubrics.yaml + `check_app_domain_harness_parity.py` | Each dim gets `taxonomy_class: capability | regression | tracked_metric` | 3k | Todo |
| W3.P1 | Append Eval Harness RUNBOOK sections | 8 apps' `RUNBOOK.md` | Shared template wording; keep each concise | 4k | Todo |
| W4.P1 | Legacy-YAML deprecation + shim | new `apps_shared/config/legacy_yaml_deprecation.py` + loader integrations | Warnings are DeprecationWarning class; no hard break | 4k | Todo |
| W5.P1 | Extend e2e cert-hook verification tests | `tests/_apps_contract/test_w2p3_exit_eval_hook.py` + new integration test | Must cover both apps_qna + apps_underwriting_ai code paths | 4k | Todo |
| W6.P1 | Non-goals doctrinal fence | `.windsurf/plans/` this file §3 + FENCE_POSTS module note | Declarative; no code | 1k | Todo |

## 6. Wave Detail

### Wave 1 — RAG Metric Dims (closes W3.P5)

**Entry gate:** e4a1b7 W3 grader types landed (`ScoreDimension` accepts new types).
**Exit gate:** Each grounded app's eval_rubrics.yaml carries the 3 RAG dims with OpenAI-baseline thresholds and evidence_required/fail_closed flags appropriate to the dim's purpose.

RAG dims added per-app (canonical from OpenAI + Galileo + LangChain):

- `context_recall` (grader_type=llm_as_judge, min_required_score=0.85, fail_closed_if_unknown=false, evidence_required=true)
- `context_precision` (grader_type=llm_as_judge, min_required_score=0.70, fail_closed_if_unknown=false, evidence_required=true)
- `answer_relevancy` (grader_type=llm_as_judge, min_required_score=0.80, fail_closed_if_unknown=false, evidence_required=true)

All three are `fail_closed_if_unknown=false` so their absence (pending producer wiring) does not cascade-fail existing runs. Runtime behavior is unchanged until producers populate `output["dim_scores"]`.

### Wave 2 — Capability-vs-Regression Taxonomy (closes W5.P3)

Each dim is annotated with `taxonomy_class` in {`capability`, `regression`, `tracked_metric`}:

- `capability`: core ability the app MUST demonstrate (e.g., `factual_grounding`)
- `regression`: watchdog against known failure modes (e.g., `no_fabrication`)
- `tracked_metric`: observed but not gated (e.g., `latency_ms`, brand_voice)

Gate adds `TAXONOMY_COVERAGE` advisory finding for dims missing annotation.

### Wave 3 — RUNBOOK Eval Harness Sections (closes W5.P5)

Each app's `RUNBOOK.md` gains a `## Eval Harness` section describing:

- Which rubric (path + ID)
- Which threshold profile
- HITL policy
- How to run the advisory CI gate
- Where the eval_harness_outcome ledger rows appear

### Wave 4 — Legacy YAML Deprecation (closes W5.P4)

A small `apps_shared/config/legacy_yaml_deprecation.py` helper with `emit_deprecation(path, since, removal_target)` that issues a `DeprecationWarning` + logs structured ledger event. Consumers that load `*_policies.yaml` or `*_thresholds.yaml` call it once on import.

### Wave 5 — E2E Cert-Hook Verification (closes W2.P6)

Extends `test_w2p3_exit_eval_hook.py` with integration tests that:
- Invoke `maybe_invoke_exit_eval` against synthetic receipts
- Assert ledger rows appear in `eval_harness_outcome`
- Assert the hook is fail-soft when receipts are malformed

### Wave 6 — Non-Goals Fence

Doctrinal. No code. Cross-references the future-plan placeholders for each deferred item.

## 7. Gap → Wave Traceability

| Parent-plan gap | Disposition | This plan wave |
|---|---|---|
| W2.P1/P2 C0 FEC producer | Deferred to dedicated future plan | — (non-goal) |
| W2.P6 e2e cert proof | Closed | W5 |
| W3.P5 RAG dim thresholds | Closed | W1 |
| W5.P1 holdout vs dev | Deferred to dedicated future plan | — (non-goal) |
| W5.P2 production-log mining | Deferred to dedicated future plan | — (non-goal) |
| W5.P3 capability/regression tagging | Closed | W2 |
| W5.P4 legacy YAML deprecation | Closed | W4 |
| W5.P5 per-app RUNBOOKs | Closed | W3 |

## 8. Governance & Cross-References

- Constitutional §22 (ADG graph-layer primary)
- Constitutional §24 (deferred-scope capture)
- Constitutional §31 (SSOT folder routing — new files under `apps_shared/`, `ops_scripts/ci/`, `tests/_apps_contract/`)
- Constitutional §32 (Fort Knox cert discipline — no `SIGNED_OFF` emission from this plan)
- ADR-050 (intelligence-ledger-family — unchanged)
- `author-gate-enforcement.md` — no Author-Gate decision points anticipated (all additive, reversible)
- `notion-plan-wave-deferral.md` — mid-plan Notion writes forbidden; batched at completion

## 9. Author-Gate Decision Points (anticipated)

None. Every change is additive and either:
- Additive YAML field (non-breaking)
- Additive schema field with default `""` (non-breaking)
- Documentation append (non-breaking)
- Deprecation warning (non-breaking)
- Test extension

If an unforeseen Author-Gate surfaces mid-execution, it will be emitted inline per `author-gate-queue-drain.md`.

## 10. Risks

| Risk | Mitigation |
|---|---|
| RAG dim additions change overall weighted score | All 3 RAG dims carry low weight (0.05 each) and `fail_closed_if_unknown=false` — absence is silent |
| taxonomy_class gate noise on rubrics that haven't yet annotated | Default is `""`; gate emits INFO-severity "TAXONOMY_COVERAGE" and doesn't block |
| Legacy YAML deprecation warnings break strict-warnings CI | DeprecationWarning is filterable; tests set filter to default |

## 11. Timeline

Single session, ~6 waves × 15-30 min each. Ship in one PR.

## 12. Metadata

- Plan file path: `.windsurf/plans/apps-eval-harness-closeout-b7c9d2.md`
- Notion Plans row: Live status at creation; flipped to Completed at plan end
- Template: `.windsurf/templates/execution-plan-template.md`
