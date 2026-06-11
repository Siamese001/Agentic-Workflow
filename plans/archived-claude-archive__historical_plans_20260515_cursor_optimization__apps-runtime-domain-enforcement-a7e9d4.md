---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-runtime-domain-enforcement-a7e9d4.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-runtime-domain-enforcement-a7e9d4.md'
source_sha256: 3e56eb14a726231450425c0e5c64b69c5a5c8b96b1041818034207077d3568bb
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: apps_* Runtime Domain-Enforcement Certification Completion

> Correcting false-positive `APPS_SPINE_CERTIFIED` signoff. Make 100% runtime signoff contingent on live domain enforcement — not artifact presence.

**Author-Gate context**: User explicitly accepted scope. Do not argue scope, do not split runtime. Runtime = full governed path (spine + static contracts + ASE + C0 FEC + Exit packet + X1 + X2 + X3 + OTEL + replay + negative controls).

**Prior work credit**: ~40% of Phase 2 wiring already landed in plan `apps-eval-harness-parity-f8d4a2` (W1–W6, 194 tests passing). Gaps that remain drive this plan.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.P1–W1.P3 | Augment cert requirement spine — 12 new APPS-DOM-* rows + claim-type controls + schema | ~25k | `apps_e2e_requirements_source.json` is authoritative; compiler picks up new rows deterministically | 🟡 Draft | 12 APPS-DOM rows added, claim_type controls registered, canary still passes |
| W2 | W2.P1–W2.P3 | Per-app `__main__.py` + `rubric_output_mapper` for the 7 apps missing Exit invocation | ~60k | apps_shared/cert/exit_eval_hook.py is stable; each app has a DecisionPacket-equivalent to project into dim_scores | 🟡 Draft | All 8 runtime apps invoke `maybe_invoke_exit_eval` on cert route; `app_specific_eval.bound=True` observable per app |
| W3 | W3.P1–W3.P2 | Evidence producers — assertion emitters that read OTEL/proof artifacts and emit PASS rows per APPS-DOM requirement | ~35k | `exit.app_specific_eval` span fields are populated (W1.P1 prior session wired this) | 🟡 Draft | `tools/cert/apps_e2e/emit_apps_domain_enforcement_assertions.py` emits row-specific PASS/FAIL for each APPS-DOM-NNN row per app |
| W4 | W4.P1–W4.P2 | Per-app domain negative controls — fabrication/personalization/coverage/unsupported-answer scenarios that must produce `x3_disposition != ALLOW` | ~45k | `artifacts/certification/apps_e2e/_domain_negative_controls/` replaces sandbox fixtures; per-app scenarios deterministic | 🟡 Draft | Each of 8 apps has ≥1 scenario proving domain-failing output is blocked; verifier asserts `x3_disposition in {DENY, SAFE_ABSTAIN, ESCALATE}` |
| W5 | W5.P1–W5.P3 | FEC presence gate + empty-judge-roster gate + OTEL span field assertions | ~30k | `app_specific_evaluator.py` already fail-closes on `evidence_required_but_empty` per-dim; we add top-level FEC presence for evidence_required apps | 🟡 Draft | `check_apps_e2e_spine_certification.py` fail-closes on any APPS-DOM-NNN FAIL |
| W6 | W6.P1 | Verifier + CI integration: promote compiler to require APPS-DOM rows; update CI gate to fail on missing evidence | ~20k | `scripts/compile_apps_e2e_signoff.py` design is pluggable — 12 new rows just feed the existing loop | 🟡 Draft | `python scripts/compile_apps_e2e_signoff.py` exits non-zero if any APPS-DOM row lacks PASS; compiler canary still passes |
| W7 | W7.P1–W7.P3 | Tests: unit + integration + E2E + OTEL + replay | ~50k | test infrastructure at `tests/_apps_contract/` is the canonical home | 🟡 Draft | 14 new tests from user request §5; all 194 existing tests still pass; 4-app empty-judge backlog documented as intentional fail-closed behavior |
| W8 | W8.P1 | Final compile + report: run compiler, fill per-app status table, emit SIGNED_OFF or FAILED | ~15k | All prior waves green | 🟡 Draft | User-requested Phase 6 final report delivered with per-app PASS/FAIL matrix |

**Total scope**: ~280k tokens across 8 waves, 22 phases. Single session can realistically execute W1–W3; W4 onward is next-session work unless user extends.

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Define APPS-DOM-001..012 rows | `certification/apps_e2e_requirements_source.json` | `requirement_count` increment, `depends_on_req_ids` chain discipline, `allowed_verifier_commands` for new emitter, `allowed_artifact_classes` registry growth | 12k | Draft |
| W1.P2 | Register new claim types + controls | `certification/apps_e2e_requirements_source.json:claim_type_required_controls` | New claim_type `APPS_DOMAIN_RUNTIME_ENFORCEMENT` with 5+ required controls | 4k | Draft |
| W1.P3 | Extend assertion schema | `certification/schemas/apps_evidence_assertion.schema.json` | Add enum values for new controls; validator must stay strict | 6k | Draft |
| W2.P1 | apps_rg live-cert mode + rubric mapper | `apps_rg/__main__.py`, `apps_rg/engines/rubric_output_mapper.py` (new), `apps_rg/config/cert_route_registry.yaml` | DecisionPacket equivalent is `FinalResumeBundle`; projection to 7-dim rubric | 12k | Draft |
| W2.P2 | apps_lic + apps_rfp + apps_qna + apps_research + apps_exec live-cert mode | 5× `__main__.py` + 5× `rubric_output_mapper.py` + 5× `cert_route_registry.yaml` | Each app has different output shape; mapper must be deterministic | 32k | Draft |
| W2.P3 | apps_eval live-cert mode (evaluator-of-evaluators) | `apps_eval/__main__.py` + mapper | Bootstrapping problem: apps_eval evaluates other apps; its own rubric is about calibration stability | 12k | Draft |
| W3.P1 | Evidence producer: domain enforcement assertions | `tools/cert/apps_e2e/emit_apps_domain_enforcement_assertions.py` (new) | Reads `artifacts/apps_<x>/runs/<ts>/otel_runtime_trace.json`; extracts `exit.app_specific_eval` span fields; emits PASS/FAIL per (app × APPS-DOM-NNN) | 22k | Draft |
| W3.P2 | Evidence producer: negative control assertions | `tools/cert/apps_e2e/emit_apps_negative_control_assertions.py` (new) | Reads scenario result from `_domain_negative_controls/`; emits PASS iff x3_disposition != ALLOW | 12k | Draft |
| W4.P1 | Domain negative controls: 8 apps × 1 scenario each | `artifacts/certification/apps_e2e/_domain_negative_controls/<app>/scenario_01_*.yaml` + runner | apps_rg fabricated credential; apps_lic fake personalization; apps_rfp missing req; apps_qna unsupported answer; apps_research stale source; apps_exec boilerplate; apps_underwriting_ai fairness violation; apps_eval calibration drift | 32k | Draft |
| W4.P2 | Negative-control runner | `tools/cert/apps_e2e/run_domain_negative_controls.py` (new) | Runs each scenario through the app's live pipeline + Exit hook; captures x3_disposition; writes result JSON | 12k | Draft |
| W5.P1 | FEC presence gate | `agentic_core/L3_orchestration/exit_eval/v6/preflight.py` (augment) OR new X1 check | For apps with `evidence_required=true` in any rubric dim: FEC must have non-empty `support_score`, `evidence_refs`, `source_lineage`, `policy_hash`, `blueprint_hash`, `replay_refs` | 12k | Draft |
| W5.P2 | Empty-judge-roster fail-closed promotion | `agentic_core/L3_orchestration/exit_eval/v6/app_grader_registry.py` + `app_specific_evaluator.py` | Empty roster for a required dim → FAIL (not UNKNOWN). Currently advisory via `NO_UNIMPL_JUDGES`. Exception: `informational_only=true` in threshold profile | 10k | Draft |
| W5.P3 | OTEL span field completeness gate | `agentic_core/L3_orchestration/exit_eval/v6/pipeline.py` (augment span attrs) + new check | Add per-dim `status`, `evidence_refs_count`, `grader_refs`, `confidence`, `abstain_flag`, `judge_abstain_count`, `x1_domain_gate_result`, `x2_domain_aggregate_result`, `x3_domain_consequence` | 10k | Draft |
| W6.P1 | Compiler + CI gate update | `scripts/compile_apps_e2e_signoff.py`, `ops_scripts/ci/check_apps_e2e_spine_certification.py` | Compiler signoff matrix adds 12 APPS-DOM rows; CI gate fail-closes | 18k | Draft |
| W7.P1 | Unit tests (14 from user request §5 items 1–4) | `tests/_apps_contract/test_apps_dom_unit.py` | AppSpecificEvaluator structured verdicts; missing required metric fail-closed; UNKNOWN fail-closed; empty roster fail-closed | 14k | Draft |
| W7.P2 | Integration tests (items 5–9) | `tests/_apps_contract/test_apps_dom_integration.py` | Live Exit invocation; `app_specific_eval` populated; X1/X2/X3 consume dims; X3 blocks on required fail | 18k | Draft |
| W7.P3 | E2E + OTEL + replay (items 10–14) | `tests/_apps_contract/test_apps_dom_e2e.py`, `test_apps_dom_otel.py`, `test_apps_dom_replay.py` | Per-app pass + negative scenarios; SINGLE_STEP reaches Exit; FEC missing cannot ALLOW; OTEL fields present; deterministic replay | 22k | Draft |
| W8.P1 | Final compile + per-app status report | Run compiler + emit Phase 6 report | Per user request Phase 6 section | 8k | Draft |

## APPS-DOM Requirement Rows (frozen in W1.P1)

| req_id | Title | Control(s) | Acceptance rule |
|---|---|---|---|
| APPS-DOM-001 | DOMAIN_CONTRACT_ACTIVE | `app_domain_contract_active` | Every runtime apps_* has active rubric + threshold_profile + grader_roster; no draft |
| APPS-DOM-002 | DOMAIN_EVALUATOR_LIVE_INVOKED | `app_specific_evaluator_invoked` | `exit.app_specific_eval` span observed with `app_id=<owner_app>` in the signed run's OTEL trace |
| APPS-DOM-003 | EXIT_PACKET_APP_SPECIFIC_EVAL_BOUND | `exit_packet_app_eval_bound` | `exit_review_packet.app_specific_eval.bound=True` at runtime for every app with required domain metrics |
| APPS-DOM-004 | X1_CONSUMES_DOMAIN_METRICS | `x1_domain_gate_consumed` | X1 (or APP_DOMAIN shadow gate at X2) treats app-specific dims as first-class verdicts; reason_codes surface dim IDs |
| APPS-DOM-005 | X2_AGGREGATES_DOMAIN_VERDICTS | `x2_domain_aggregate_present` | X2 decision includes `failed_gate_ids=["APP_DOMAIN"]` or app-dim reason_codes when bound eval fails |
| APPS-DOM-006 | X3_BLOCKS_DOMAIN_FAILURES | `x3_domain_block_proved` | Per-app negative control: bad domain output produces `x3_disposition in {DENY, SAFE_ABSTAIN, ESCALATE}` |
| APPS-DOM-007 | C0_FEC_BOUND_WHEN_EVIDENCE_REQUIRED | `c0_fec_bound` | Apps with any `evidence_required=true` rubric dim carry non-empty `final_evidence_contract` with all 10 required fields |
| APPS-DOM-008 | JUDGE_ROSTER_AND_UNKNOWN_FAIL_CLOSED | `judge_roster_populated`, `unknown_fail_closed` | Required judge metrics have non-empty rosters; UNKNOWN/abstain/timeout/parse-fail → FAIL (not PASS); `informational_only=true` is the only exception |
| APPS-DOM-009 | DOMAIN_OTEL_PROOF_PRESENT | `domain_otel_fields_complete` | `exit.app_specific_eval` span carries all 13 required fields (user Phase 2 §9 list) |
| APPS-DOM-010 | DOMAIN_NEGATIVE_CONTROL_BLOCKS_ALLOW | `domain_negative_control_blocks` | Per-app negative control → X3 does not ALLOW |
| APPS-DOM-011 | SINGLE_STEP_STILL_RUNS_EXIT_ENFORCEMENT | `single_step_exit_invoked` | `route_contract.execution_form=SINGLE_STEP` apps still emit `exit.app_specific_eval` span on cert runs |
| APPS-DOM-012 | L2_ARTIFACT_EVALUABILITY | `l2_artifact_evaluable` | L2 sealed artifact carries sealed output + evidence_refs + counters + artifact_refs sufficient for Exit to evaluate all rubric dims |

## Open Questions / Uncertainty

1. **apps_eval**: is it runtime-reachable by user requests, or purely a CI-time evaluator? If CI-only, APPS-DOM-* rows for apps_eval could be marked `is_runtime_app=false` + exempted. Default assumption: include it with a calibration-drift negative control.
2. **apps_shared**: library only per user Phase 3 note. Exclude from APPS-DOM per-app rows.
3. **Existing waivers** for apps_qna + apps_underwriting_ai (`SIGNED_OFF_WITH_WAIVERS` trust level): do APPS-DOM rows for those apps need waiver handling, or should they flip to full signoff now that W2.P3 adoption lands? Default: flip to full signoff on W2 completion.
4. **FEC-equivalent evidence contracts**: user Phase 2 §6 allows "approved equivalent evidence contract". For apps_underwriting_ai (SINGLE_STEP, no retrieval, deterministic feature derivation), does the feature-derivation receipt qualify? Default: yes, documented via `config/certification/evidence_contract_equivalents.yaml` (new).

## Non-Goals

- No thresholds weakened to pass tests.
- No required metrics flipped to `informational_only` without a documented policy exception.
- No cosmetic refactor of v6 Exit pipeline.
- No touching parallel-session files (see memory `8b11664b`).

## Definition of Done

1. 12 APPS-DOM rows added, schema valid.
2. 8 runtime apps invoke `maybe_invoke_exit_eval` on cert route; `exit.app_specific_eval` span observed per app.
3. 8 per-app domain negative controls present; each proves `x3_disposition != ALLOW`.
4. Empty judge rosters for required dims are fail-closed (not advisory).
5. FEC presence gate enforced for evidence_required apps.
6. `scripts/compile_apps_e2e_signoff.py` fail-closes on any APPS-DOM FAIL.
7. 14 new tests pass; all 194 existing pass.
8. Phase 6 final report delivered with per-app matrix + OVERALL APPS_* RUNTIME status.

## ADG_HOTSPOT_REPORT + ADG_GRAPH_LAYER_EVIDENCE

Deferred to W1.P1 execution — will run `adg_nodes_by_layer("L3")` + `adg_edge_fanout` on `pipeline.py` / `x2_matrix.py` / `x3_dispositions.py` to confirm no cross-layer break before wiring new code. Scope is additive (new files, new cert rows) so blast radius is bounded to L3 Exit + cert spine + per-app `__main__.py`.

## AG_QUEUE_SEED

```
AG_QUEUE_SEED: plan=apps-runtime-domain-enforcement-a7e9d4 id=AG-W1-requirement-rows depends_on= title=Confirm 12 APPS-DOM row shapes + claim_type naming before freezing requirements_source.json
AG_QUEUE_SEED: plan=apps-runtime-domain-enforcement-a7e9d4 id=AG-W2-mapper-scope depends_on=AG-W1-requirement-rows title=Confirm rubric_output_mapper signature shared across 7 apps vs per-app (scope vs consistency tradeoff)
AG_QUEUE_SEED: plan=apps-runtime-domain-enforcement-a7e9d4 id=AG-W4-negative-controls depends_on=AG-W2-mapper-scope title=Confirm negative-control scenario taxonomy — per user Phase 3 list vs broader
AG_QUEUE_SEED: plan=apps-runtime-domain-enforcement-a7e9d4 id=AG-W5-fec-equivalents depends_on=AG-W4-negative-controls title=Confirm evidence_contract_equivalents policy for SINGLE_STEP deterministic apps
AG_QUEUE_SEED: plan=apps-runtime-domain-enforcement-a7e9d4 id=AG-W6-waiver-handling depends_on=AG-W5-fec-equivalents title=Confirm whether apps_qna + apps_underwriting_ai flip from SIGNED_OFF_WITH_WAIVERS to full signoff on W2 completion
```
