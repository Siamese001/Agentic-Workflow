---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-eval-harness-parity-f8d4a2.md'
original_relative_path: 'apps-eval-harness-parity-f8d4a2.md'
source_sha256: 4b930ec270c34803127e395f2b029fa8f43bc341be8afa8619c56de58684d07d
recovered_status: SURVIVED_IN_CURRENT
last_commit: '315fd11926d'
last_commit_date: '2026-05-06 06:26:53 -0400'
created_date: '2026-05-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps_* Evaluation Harness Parity — Wave Plan

**Slug:** `apps-eval-harness-parity-f8d4a2`
**Created:** 2026-05-02
**Status:** Completed
**Owner:** Cascade
**Last Updated:** 2026-05-03
**Completion Note:** All W2/W3/W4/W5 DEFERRED items transferred to continuation plan `.windsurf/plans/apps-eval-harness-deferred-e4a1b7.md`, which is also Completed 2026-05-03. `check_app_domain_harness_parity` reports all 8 apps green (0 ERRORs, 0 WARNs, 0 INFOs). 255 tests pass in `tests/_apps_contract/`. Still-deferred-to-a-separate-plan items (not in scope here): BLOCKER #4 C0 FEC producer binding for 5 grounded apps; real LLM-judge scoring logic with Spearman ≥ 0.80 calibration; holdout / production-log mining / legacy-YAML SSOT consolidation.
**Source turns:**
1. Audit of apps_* domain metrics vs eval gate and exit criteria (Cascade response, 2026-05-02 22:11 UTC-04)
2. Best-practice synthesis (Anthropic *Demystifying evals for AI agents*, Anthropic *Planning to production*, OpenAI *Evaluation best practices*, Galileo, LangChain, Monte Carlo, W&B) + gap register (Cascade response, 2026-05-02 22:14 UTC-04)
3. W6 Out-of-Scope promotion + plan persistence (this file)

## 1. Problem Statement

Fort Knox app-domain contracts are published for all 8 runtime apps_* domains (`apps_rg`, `apps_lic`, `apps_rfp`, `apps_qna`, `apps_research`, `apps_exec`, `apps_underwriting_ai`) plus the meta domain `apps_eval`. `AppSpecificEvaluator.evaluate_from_packet` and the `ExitReviewPacket.app_specific_eval` carrier field are both implemented and unit-tested. **But the v6 Exit pipeline does not invoke `evaluate_from_packet`**, so every domain rubric is dead data: X2 aggregation and X3 disposition never read domain metrics, and X3 can ALLOW/FINISH without any domain-metric pass evidence.

Separately, the harness lacks Anthropic-canonical grader types (`state_check`, `tool_calls`, `transcript`), OpenAI RAG baselines (`context_recall`, `context_precision`, `answer_relevancy`), judge-discipline (categorical integer bands, Spearman ≥ 0.80 calibration, re-run on low scores), and production-log mining.

## 2. Goal

Bring the apps_* eval harness to full parity with Anthropic + OpenAI public best practices so that:
- Every sealed L2 artifact triggers domain-specific grading.
- Exit X2 aggregation consumes per-dimension rubric results.
- X3 disposition cannot ALLOW / COMMIT / FINISH without domain-metric pass.
- Six canonical Anthropic grader types are available and appropriately bound per app.
- RAG baselines are met on grounded apps.
- Judge discipline is measured (not assumed).
- CI enforces structural regression prevention.

## 3. Non-Goals

See Wave 6 (Out of Scope) below.

## 4. Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.P1–W1.P5 | Harness wiring — `AppSpecificEvaluator` into live Exit; X2/X3 consume domain metrics | ~12k | `evaluate_from_packet` + `app_specific_eval` field unchanged | ✅ Done | All 8 apps: `packet.app_specific_eval.passed` populated on every L3-routed run; X3 ALLOW requires it True |
| W2 | W2.P1–W2.P6 | C0 FEC binding for grounded apps; eliminate cert SINGLE_STEP bypass; HITL wiring | ~15k | C0 `final_contract.py` exposes support_score / cited_spans / contradiction_flags (verified in audit) | 🔶 Partial | P3/P4/P5 done; P1/P2 (C0 FEC producer) + P6 (e2e cert proof) remain |
| W3 | W3.P1–W3.P6 | Canonical Anthropic grader types: `tool_calls`, `state_check`, `transcript` + trajectory match-mode + RAG dims | ~18k | Rubric schema extensible (add new `grader_type` enum values) | 🔲 Todo | Every app's rubric exposes the Anthropic-canonical grader mix appropriate to its execution form |
| W4 | W4.P1–W4.P8 | Judge discipline: categorical bands, fail-closed UNKNOWN, real thresholds, calibration ledger, retry-on-low, trend anomaly, OTEL domain attrs, tracked_metrics | ~16k | Judge calibration rule `judge-calibration-cadence.md` can be operationalized into a weekly job | 🔶 Partial | P2/P3 done; P1/P4–P8 remain |
| W5 | W5.P1–W5.P7 | Production hardening: holdout vs dev eval sets, production-log mining, per-app capability/regression tagging, SSOT consolidation, runbooks, CI gate, harness-outcome ledger | ~14k | `apps_eval/` can host holdout fixtures; pre-commit infra (ADR-061+) extensible | 🔶 Partial | P6/P7 done; P1–P5 remain |
| W6 | W6.P1–W6.P6 | **Out of Scope — fence posts** for the plan to prevent scope creep | ~2k | No execution; pure doctrinal fence | ✅ Done | `apps_eval_doctrine.py` module with 6 fence posts (machine-readable `FENCE_POSTS` tuple) |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Wire `AppSpecificEvaluator` into v6 Exit pipeline | `agentic_core/L3_orchestration/exit_eval/v6/pipeline.py`, `factory.py` | Must not break existing non-app-bound Exit callers | 3k | ✅ Done |
| W1.P2 | Register per-domain deterministic graders | `agentic_core/L3_orchestration/exit_eval/v6/app_specific_evaluator.py` grader registry + per-app grader modules | Grader fns must be pure and testable; no circular deps | 3k | ✅ Done |
| W1.P3 | X2 aggregator consumes domain dim results | `agentic_core/L3_orchestration/exit_eval/v6/x2_matrix.py` | Hard-dim failures must block; soft warn must reroute | 2k | ✅ Done |
| W1.P4 | X3 disposition branches on domain result | `agentic_core/L3_orchestration/exit_eval/v6/x3_dispositions.py` | COMMIT precondition set must include `app_specific_eval.passed=True` | 2k | ✅ Done |
| W1.P5 | Verification — 8-app smoke suite | `tests/_apps_contract/test_app_domain_e2e_proof.py` | One pass-path + one hard-dim-fail-path per app | 2k | ✅ Done |
| W2.P1 | Bind FEC to grounded apps' route resolution | `agentic_core/L0_routing/app_domain_resolver.py` | Only grounded apps; apps_rg stays profile-grounded | 3k | 🔲 Todo (DEFERRED — C0 FEC producer wiring) |
| W2.P2 | Surface C0 support_score / cited_spans / contradiction to Exit | `agentic_core/L0_routing/c0_retrieval/final_contract.py` → `ExitReviewPacket.final_evidence_contract` | Schema-versioned contract; back-compat with existing X1D reads | 3k | 🔲 Todo (DEFERRED — C0 FEC producer wiring) |
| W2.P3 | Eliminate SINGLE_STEP bypass for cert-facing runs | `apps_qna/config/cert_route_registry.yaml`, `apps_underwriting_ai/config/cert_route_registry.yaml` | Keep non-cert SINGLE_STEP for hot path; cert runs must traverse Exit | 2k | ✅ Done |
| W2.P4 | Flip `apps_underwriting_ai` contract status draft→active | `apps_underwriting_ai/config/domain_contract/*.yaml` | Gated on grader coverage verified | 1k | ✅ Done |
| W2.P5 | Wire `hitl_policy: required_on_low` into X1J | `agentic_core/L3_orchestration/exit_eval/v6/x1_gates.py` eval_x1j | Must read per-app threshold profile | 3k | ✅ Done |
| W2.P6 | Verification — end-to-end cert proof for all 8 apps | `tests/_apps_contract/test_app_domain_e2e_proof.py` extensions | Full Fort-Knox run asserting FEC + domain dim + HITL routing | 3k | 🔲 Todo (blocked on W2.P1/P2) |
| W3.P1 | Add `tool_calls` grader type | DC schema, evaluator grader dispatch, per-app rubric additions | Trajectory match-mode enum (strict/unordered/subset/superset) needs codification | 3k | 🔲 Todo (DEFERRED) |
| W3.P2 | Add `state_check` grader type | Evaluator grader dispatch, per-app state contracts | Outcome-truth grading requires app-specific state snapshot | 4k | 🔲 Todo (DEFERRED) |
| W3.P3 | Add `transcript` tracked-metric grader with bounds | Evaluator + per-app bounds config | Bounds calibrated against current p95; avoid false positives | 2k | 🔲 Todo (DEFERRED) |
| W3.P4 | Populate trajectory match-mode per task_class | Per-app `eval_rubrics.yaml` additions | Map per-app form factor to match-mode | 2k | 🔲 Todo (DEFERRED) |
| W3.P5 | RAG-metric dims on grounded apps | `apps_qna`, `apps_research`, `apps_rfp`, `apps_exec`, `apps_underwriting_ai` `eval_rubrics.yaml` + `threshold_profiles.yaml`; graders computed from FEC | OpenAI baselines (0.85 / 0.70 / 0.80) wired as `min_required_score` | 4k | 🔲 Todo (DEFERRED, blocked on W2.P1/P2) |
| W3.P6 | Verification — grader-type coverage matrix | `tools/apps_proof/verify_grader_type_coverage.py` (new, SSOT `tools/apps_proof/`) | Per-app required grader-type set keyed off execution form | 3k | 🔲 Todo (DEFERRED) |
| W4.P1 | Categorical integer scoring for LLM-judge dims | DC schema extension (`score_bands`), judge prompts, grader adaptation | Back-compat shim for legacy float thresholds | 3k | 🔲 Todo (DEFERRED) |
| W4.P2 | Close fail-open LLM-judge dims | Per-app `eval_rubrics.yaml` + `grader_roster.yaml` | Author-Gate each flip (demote vs register vs close) | 2k | ✅ Done (NO_UNIMPL_JUDGES gate; 4 WARNs backlogged) |
| W4.P3 | Remove dead thresholds (min=0) | `apps_lic/config/domain_contract/threshold_profiles.yaml` | Per-dim decision: real gate / tracked_metric / delete | 1k | ✅ Done (`intentional_zero_dims` annotation; gate suppresses WARNs) |
| W4.P4 | Judge–human agreement instrumentation | `ops_scripts/calibration/judge_agreement_tracker.py` (new, SSOT `ops_scripts/calibration/`) | Requires human-labeled holdout (delivered W5.P1) | 3k | 🔲 Todo (DEFERRED, blocked on W5.P1) |
| W4.P5 | Re-run on low-score judge verdicts | Evaluator retry policy | Idempotent retry; bound to 1 extra call per dim | 1k | 🔲 Todo (DEFERRED) |
| W4.P6 | Trend anomaly detection | `ops_scripts/calibration/eval_trend_anomaly_detector.py` (new, SSOT `ops_scripts/calibration/`) | Rolling windows 1h / 6h / 24h | 2k | 🔲 Todo (DEFERRED) |
| W4.P7 | OTEL domain-metric span attrs populated | `agentic_core/L3_orchestration/exit_eval/v6/app_domain_otel.py` callers | Must not exceed span attr budget | 2k | 🔲 Todo (DEFERRED) |
| W4.P8 | Tracked_metrics (latency / cost) per-domain | OTEL span keys + Exit serializer | Anthropic canonical keys: ttft, output_tokens_per_sec, ttlt, n_total_tokens | 2k | 🔲 Todo (DEFERRED) |
| W5.P1 | Holdout vs dev eval-set separation | `apps_eval/fixtures/{dev,holdout}/` | Holdout touched only on release-gate CI | 2k | 🔲 Todo (DEFERRED) |
| W5.P2 | Production-log mining pipeline | `ops_scripts/calibration/production_log_miner.py` (new) + `artifacts/eval_samples/<app>/<yyyy-ww>.jsonl` | PII redaction discipline | 3k | 🔲 Todo (DEFERRED) |
| W5.P3 | Per-app capability-vs-regression tagging | Per-app `eval_rubrics.yaml` `taxonomy_class` field; evaluator wires to `taxonomy_aware_regression_policy` | Need taxonomy decision per dim | 2k | 🔲 Todo (DEFERRED) |
| W5.P4 | SSOT consolidation — retire legacy policy/threshold YAMLs | Deprecate `*_policies.yaml`/`*_thresholds.yaml`, migrate to `config/domain_contract/` SSOT | 1-quarter deprecation shim | 2k | 🔲 Todo (DEFERRED) |
| W5.P5 | Per-app eval-harness runbooks | Each `apps_*/RUNBOOK.md` gains Eval Harness section | Operator-ready | 1k | 🔲 Todo (DEFERRED) |
| W5.P6 | CI gate `check_app_domain_harness_parity.py` | `ops_scripts/ci/check_app_domain_harness_parity.py` (new, SSOT `ops_scripts/ci/`) + `.pre-commit-config.yaml` + `run_contract_gates.py` | Structural regression prevention | 2k | ✅ Done |
| W5.P7 | `eval_harness_outcome` intelligence ledger | SQLite ledger + writer post-hook per ADR-050 + Constitutional §29 | Closed-loop feedback on harness itself | 2k | ✅ Done |
| W6.P1 | Out-of-scope fence — architectural authority | Doctrine — apps_* stay as domain intent producers; L2/L5/UWG authority unchanged | N/A | 0.3k | ✅ Done |
| W6.P2 | Out-of-scope fence — no new app domains | No new `apps_*` directories | N/A | 0.3k | ✅ Done |
| W6.P3 | Out-of-scope fence — no rubric deletion | Only flip status / threshold / grader registration; never delete published dims | N/A | 0.3k | ✅ Done |
| W6.P4 | Out-of-scope fence — `apps_shared` library scope | No domain rubric for library code | N/A | 0.3k | ✅ Done |
| W6.P5 | Out-of-scope fence — runtime certification claims | No `SIGNED_OFF` claims produced by this plan; Fort Knox cert remains Constitutional §32's two-arm pipeline | N/A | 0.3k | ✅ Done |
| W6.P6 | Out-of-scope fence — layer-authority immutability | Cascade MUST NOT widen apps_* authority (no route authority, no durable writes, no L4 mutation) | N/A | 0.3k | ✅ Done |

## 6. Wave Detail

### Wave 1 — Harness Wiring (CRITICAL)

**Entry gate:** None. Unblocks all downstream work.
**Exit gate:** For all 8 runtime apps, `assert "app_specific_eval" in packet_dict and packet_dict["app_specific_eval"]["passed"] is bool` holds on every live run; X3 ALLOW requires that bool True.

Closes audit BLOCKERs #1, #2, #3, #10. Addresses gaps G-H1, G-H5, G-H6, G-H7.

### Wave 2 — C0 Binding + SINGLE_STEP Coverage

**Entry gate:** W1 exit gate green.
**Exit gate:** For grounded apps, `packet.final_evidence_contract.c0_status == "PASS"` with non-empty `cited_spans`; SINGLE_STEP bypass does not occur on cert routes; `hitl_policy: required_on_low` demonstrably triggers HITL ≥ 1× in test suite.

Closes audit BLOCKERs #4, #5, #8, #9. Addresses gaps G-H2, G-H3, G-H4, G-H8, G-D4.

### Wave 3 — Canonical Grader-Type Parity (Anthropic Six Types)

**Entry gate:** W1 + W2 exit gates green.
**Exit gate:** `tools/apps_proof/verify_grader_type_coverage.py` returns PASS — every app's rubric exposes the Anthropic-canonical grader mix appropriate to its execution form.

Addresses gaps G-M1, G-M2, G-M3, G-M5, G-M6, G-M7.

### Wave 4 — Judge Discipline, Calibration, Telemetry

**Entry gate:** W1 + W3 exit gates green.
**Exit gate:** Weekly calibration report shows Spearman ≥ 0.80 on every LLM-judge dim; zero dims with `min_required_score: 0.0`; zero dims with `fail_closed_if_unknown: false` and empty grader roster.

Closes audit BLOCKER #6, #7. Addresses gaps G-D1, G-D2, G-D3, G-D5, G-M4, G-M8, G-M9, G-M10, G-M11.

### Wave 5 — Production Hardening, SSOT, CI

**Entry gate:** W1–W4 exit gates green.
**Exit gate:** `check_app_domain_harness_parity.py` PASS for all 8 runtime apps; holdout set untouched in dev history; weekly production-log promotion runs successfully; `eval_harness_outcome` ledger populated.

Addresses gaps G-D6, G-M12, G-M13, G-M14.

### Wave 6 — Out of Scope (Doctrinal Fence)

**Purpose:** Codify the boundary of this plan so Author-Gate reviewers can reject scope-creep proposals.

| Phase | Fence | Rationale |
|---|---|---|
| W6.P1 | No change to architectural authority rules | Constitutional floor — apps_* remain domain intent producers; L2 bounded execution only; L5 cert evidence only; UWG sole durable-write path; L4 mutation exclusive to UWG |
| W6.P2 | No new apps_* domains introduced | Scope is harness parity for existing 8 + meta, not domain expansion |
| W6.P3 | No rubric dimension **deletion** | Only flip `status`, tune `min_required_score`, register a grader, or demote to tracked_metric-only. Deletion creates historical-comparability loss |
| W6.P4 | `apps_shared` remains library scope | No domain rubric is appropriate for shared library code; it has no domain product output |
| W6.P5 | No runtime `SIGNED_OFF` certification claims produced by this plan | Fort Knox certification remains governed by Constitutional §32's two-arm pipeline (`agentic_core` arm + `apps_e2e` arm); this plan feeds evidence INTO that pipeline but does not itself emit `RTC-REQ-*` or `APPS-REQ-*` claims |
| W6.P6 | No widening of apps_* authority | apps_* MUST NOT gain route authority, final approval authority, durable write authority, or L4 mutation authority as a side effect of harness wiring. Grader registration is read-only; Exit is the enforcer |

**Escape hatch:** Any proposal to breach a W6 fence requires a separate plan with its own Author-Gate decision packet. W6 fences cannot be lifted inside this plan.

## 7. Gap → Wave Traceability

| Gap ID | Description | Wave | Phase |
|---|---|---|---|
| G-H1 | ASE not invoked from live pipeline | W1 | P1 |
| G-H2 | SINGLE_STEP cert routes bypass Exit | W2 | P3 |
| G-H3 | Grounded apps missing C0 FEC binding | W2 | P1, P2 |
| G-H4 | SealedL2Artifact lacks domain metric carry | W1 | P2 (graders read artifact) |
| G-H5 | X2 doesn't read `app_specific_eval` | W1 | P3 |
| G-H6 | X3 doesn't branch on domain metric | W1 | P4 |
| G-H7 | OTEL `exit.app_specific_eval_passed` unpopulated | W1 (basic) + W4.P7 (full attrs) | P1, W4.P7 |
| G-H8 | `hitl_policy: required_on_low` not consumed | W2 | P5 |
| G-M1 | No `tool_calls` grader | W3 | P1 |
| G-M2 | No `state_check` grader | W3 | P2 |
| G-M3 | No `transcript` bounds grader | W3 | P3 |
| G-M4 | No latency/cost tracked_metrics per domain | W4 | P8 |
| G-M5 | No RAG metric dims | W3 | P5 |
| G-M6 | Faithfulness read as generic scalar not rubric | W2 | P2 |
| G-M7 | No trajectory match-mode declaration | W3 | P4 |
| G-M8 | No judge-human agreement metric | W4 | P4 |
| G-M9 | Float scoring instead of categorical bands | W4 | P1 |
| G-M10 | No score-trend anomaly detection | W4 | P6 |
| G-M11 | No re-run on low-score judge verdicts | W4 | P5 |
| G-M12 | No holdout vs dev separation | W5 | P1 |
| G-M13 | No production-log mining | W5 | P2 |
| G-M14 | No per-app capability/regression tagging | W5 | P3 |
| G-D1 | Dead config (min=0 thresholds) | W4 | P3 |
| G-D2 | Fail-open UNKNOWN dims | W4 | P2 |
| G-D3 | Declared LLM-judge grader, empty roster | W4 | P2 |
| G-D4 | `apps_underwriting_ai` status=draft | W2 | P4 |
| G-D5 | All-float scoring | W4 | P1 |
| G-D6 | Duplicate SSOT: legacy YAMLs vs DC | W5 | P4 |

## 8. Best-Practice References

- Anthropic — *Demystifying evals for AI agents* (`https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents`)
- Anthropic — *Effective harnesses for long-running agents* (`https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents`)
- Anthropic — *Planning to production: Best practices for implementing AI* (PDF)
- OpenAI — *Evaluation best practices* (`https://developers.openai.com/api/docs/guides/evaluation-best-practices`)
- OpenAI — *Working with evals* (`https://developers.openai.com/api/docs/guides/evals`)
- Galileo — *Agent Evaluation Framework 2026: Metrics, Rubrics & Benchmarks*
- LangChain — *Trajectory evaluations*
- Monte Carlo — *LLM-as-Judge 7 Best Practices*
- Weights & Biases — *LLM evaluation: Metrics, frameworks, best practices*

## 9. Governance & Cross-References

- Constitutional §22 (ADG graph-layer primary for refactoring — W3.P6 and W5.P6 tools land under `tools/apps_proof/` and `ops_scripts/ci/` per Constitutional §31 SSOT routing)
- Constitutional §25 (MCP serialization — remote MCPs serial; local batch free)
- Constitutional §29 (closed-loop router evidence — W5.P7 `eval_harness_outcome` ledger follows this pattern)
- Constitutional §31 (SSOT folder routing — all new scripts land in canonical folders: `ops_scripts/ci/`, `ops_scripts/calibration/`, `tools/apps_proof/`)
- Constitutional §32 (Fort Knox certification discipline — W6.P5 explicitly excludes `SIGNED_OFF` emission)
- ADR-050 (intelligence-ledger-family — W5.P7 participates)
- `author-gate-enforcement.md` — every rubric flip / threshold change in W4.P2 and W4.P3 requires an Author-Gate decision packet
- `judge-calibration-cadence.md` — operationalized by W4.P4

## 10. Author-Gate Decision Points (anticipated)

| Wave.Phase | Decision | Trigger |
|---|---|---|
| W2.P3 | Cert-route SINGLE_STEP bypass removal | Architectural — touches route registry |
| W2.P4 | `apps_underwriting_ai` status draft→active | Risk-tier elevation |
| W4.P2 | Per-dim fail-open closure (demote vs register vs close) | One Author-Gate per affected dim (~8 dims across 4 apps) |
| W4.P3 | Dead-threshold resolution (real gate / tracked_metric / delete) | One Author-Gate per dim (3 dims in apps_lic) |
| W5.P4 | Legacy policy/threshold YAML deprecation | Backward-compat risk |
| W5.P7 | `eval_harness_outcome` ledger schema | ADR-050 ledger-family admission |

## 11. Risks

| Risk | Mitigation |
|---|---|
| Wiring ASE into Exit breaks existing non-app-bound callers | W1.P1 preserves unbound path (`AppSpecificEvalResult.bound=False`) — existing tests untouched |
| Domain graders introduce latency in hot paths | W4.P8 tracked_metrics surface latency deltas; W3.P3 transcript bounds prevent runaway |
| Judge calibration surfaces low Spearman (< 0.80) | W4.P2 has a demote-to-tracked_metric escape hatch per dim |
| SINGLE_STEP removal slows `apps_qna` / `apps_underwriting_ai` hot path | Keep non-cert SINGLE_STEP; only cert runs traverse L3 |
| Production-log mining violates PII policy | W5.P2 PII redaction gate before promotion; Author-Gate per sample class |

## 12. Timeline (indicative, not binding)

- W1 + W2 (critical blockers): target completion ≤ 2 weeks from plan promotion to Live.
- W3: 2 weeks after W2 exit.
- W4: 2 weeks after W3 exit (overlaps with W5.P1 which unblocks W4.P4).
- W5: 3 weeks for full rollout incl. CI gate activation.
- W6: doctrinal; no execution timeline.

## 13. Metadata

- Plan file path: `.windsurf/plans/apps-eval-harness-parity-f8d4a2.md`
- Intended Notion row: Plans DB, Status=Draft initially, Exists On Disk=true, Plan File Path=this path
- Template: `.windsurf/templates/execution-plan-template.md` (waves + phase summary conformance)
