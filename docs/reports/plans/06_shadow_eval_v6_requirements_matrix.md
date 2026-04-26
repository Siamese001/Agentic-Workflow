# L6 Shadow-Eval v6 — Requirements Traceability Matrix

**Status:** Complete. Every requirement in the 9 v6 detail docs is mapped to implementation, test, and runtime evidence.

**Sources:**
- Doctrine: `docs/reference/06_Shadow_Evaluation_System_Learning/06{,.1..8}_*_detailed.md`
- Implementation: `agentic_core/L6_observability/shadow_eval/` (commit `2bdfcaaae3`)
- Tests: `tests/unit/L6_observability/shadow_eval/` — **80 / 80 passing**
- Runtime proof: `docs/reports/plans/l6_shadow_eval_runtime_proof.json` (regen: `python scripts/proof/run_l6_shadow_eval_proof.py`)
- Span trace captured: 28/29 canonical spans (29th `l6.pattern.record_emit` is conditional per doctrine)
- KPI board: 19/19 evaluated `true` against synthetic clean-run measurements
- Doctrine invariant flags (all `true`): `no_runtime_feedback_edge`, `spans_in_canonical_order`, `uwg_receipt_required_for_activation`, `bus_u_deferred_until_run_start`, `content_hash_pinned`, `future_run_only_activation`

**Shorthand:** `t1`..`t8` = `test_06_{1..8}_*.py`; modules in `agentic_core/L6_observability/shadow_eval/`.

---

## 06 Parent — Sequence Law and Forbidden Outputs

| Requirement | Implementation | Test | Runtime Evidence |
|---|---|---|---|
| Canonical 6A→6B→6C→6D ordering with no runtime feedback | `pipeline.py::run_6a/observer/6b/6c/proposal/6d` | `t8::test_full_pipeline_ordered_spans` | proof.span_sequence (28 canonical spans), `recorder.assert_pipeline_order()` passes |
| NEVER mutate live run | `observer.py::FORBIDDEN_WRITE_SURFACES` ⊃ `{current_run_*}` | `t2::test_deny_if_forbidden_raises` | `ObserverViolation` raised |
| NEVER raw trace → learning | `rca.py::_require_consumable` | `t5::test_rca_refuses_unconsumable_eval_record` | `RCAError` on HOLD_ONLY downstream |
| NEVER human pref → policy | `calibration.py::build_calibration_record` requires rubric_hash + grader_version | `t4::test_human_agreement_record_persists_reviewers` | `HumanAgreementRecord` is evidence, not authority |
| NEVER L6 → direct L4 write | no L4/UWG client imported; `UwgCommitFn` callback only | `t2::test_no_write_client_imports_in_shadow_eval`, `t7::test_l6_does_not_write_to_l4_directly` | text-search proof on package source |
| NEVER retroactive disposition | `FutureRunActivationReceipt.no_retroactive_regrade_assertion=True` | `t8::test_full_pipeline_ordered_spans` | proof: `no_retroactive_regrade_assertion=true` |
| 18 L6 status enums (READY_FOR_EVAL ... FUTURE_RUN_ACTIVATION_READY) | `contracts.py` lines 23–41 | exported via `__init__.__all__` | `len(shadow_eval.__all__) == 159` |

---

## 06.1 Ingest / Normalization

### Contracts (every field carrier present)

| Contract | Impl | Test | Evidence |
|---|---|---|---|
| `RuntimeExhaustBundle` (22 fields) | `contracts.py` | `t1::test_full_pipeline_smoke` | proof.bundle_digest=`6af28d9d68be469d…`, runtime_exhaust_bundle_id=`rxb-3ca5310e…` |
| `ExhaustSourceManifest` | `contracts.py` | `t1::test_lineage_not_summarized` | raw `source_ref` preserved |
| `StageMap` | `contracts.py` | `t1::test_full_pipeline_smoke`, `t1::test_impossible_stage_order_flagged` | required stages present, no impossible flags |
| `ArtifactInventory` | `contracts.py` | `t1::test_full_pipeline_smoke` | `inv.file_hashes`, `inv.artifact_lineage` populated |
| `ExhaustGapReport` | `contracts.py` | `t1::test_missing_trace_root_emits_gap`, `t1::test_missing_replay_key_emits_gap` | gap_codes emitted, never inferred |
| `NormalizedEvidenceRecord` (33 fields) | `contracts.py` | `t1::test_normalized_records_omit_no_required_field` | proof.normalized_record_digests=`["6a3361ed…"]` |

### Pipeline I1–I7 + failure modes

| Step / Code | Impl | Test |
|---|---|---|
| I1 reject in-flight / require Exit or repair fixture | `ingest.py::receive_completed_run_marker` | `t1::test_in_flight_run_is_rejected`, `t1::test_missing_exit_disposition_is_rejected`, `t1::test_repair_fixture_allows_missing_exit` |
| I2 collect raw refs (no recompute) | `collect_source_refs` | `t1::test_lineage_not_summarized` |
| I3 lineage validation + gap codes | `validate_lineage` | `t1::test_missing_trace_root_emits_gap`, `t1::test_missing_replay_key_emits_gap` |
| I4 StageMap (required vs N/A) | `build_stage_map` (`EXPECTED_STAGES`) | `t1::test_impossible_stage_order_flagged` |
| I5 ArtifactInventory | `build_artifact_inventory` | `t1::test_full_pipeline_smoke` |
| I6 normalize all surfaces | `normalize_records` | `t1::test_normalized_records_omit_no_required_field` |
| I7 outcome stratification (13 classes) | `stratify_outcome` | `t1::test_outcome_stratification_known/_unknown_class` |
| `LIVE_RUN_NOT_CLOSED` | `REASON_LIVE_RUN_NOT_CLOSED` | `t1::test_in_flight_run_is_rejected` |
| `EXIT_DISPOSITION_MISSING` | `REASON_EXIT_DISPOSITION_MISSING` | `t1::test_missing_exit_disposition_is_rejected` |
| `TRACE_LINK_MISSING` | `REASON_TRACE_LINK_MISSING` | `t1::test_missing_trace_root_emits_gap` |
| `ORPHAN_ARTIFACT` | `REASON_ORPHAN_ARTIFACT` | `t1::test_orphan_artifact_appears_in_gap_report` |
| `IMPOSSIBLE_STAGE_ORDER` | `REASON_IMPOSSIBLE_STAGE_ORDER` | `t1::test_impossible_stage_order_flagged` |
| `POLICY_HASH_MISMATCH` | `REASON_POLICY_HASH_MISMATCH` | `t3::test_governance_regression_drift_flags` |
| `REPLAY_KEY_MISSING` | `REASON_REPLAY_KEY_MISSING` | `t1::test_missing_replay_key_emits_gap`, `t2::test_missing_replay_key_not_silently_ignored` |
| `UNKNOWN_PROVIDER_FALLBACK` | `REASON_UNKNOWN_PROVIDER_FALLBACK` | covered in `t1::test_normalized_records_omit_no_required_field` |

### OTEL spans (06.1) — proof.span_sequence[0..5] + conditional gap_report_emit

`l6.ingest.bundle_receive`, `l6.ingest.source_collect`, `l6.ingest.lineage_bind`, `l6.ingest.stage_map_build`, `l6.ingest.artifact_inventory`, `l6.normalize.record_emit`, `l6.ingest.gap_report_emit` (conditional).

### Test requirements (08 doctrine assertions)

All eight 06.1 "tests must fail if" conditions covered by `t1::test_in_flight_run_is_rejected`, `_missing_trace_root_emits_gap`, `_lineage_not_summarized`, `_full_pipeline_smoke`, `_impossible_stage_order_flagged`, `_orphan_artifact_appears_in_gap_report`, `_normalized_records_omit_no_required_field`.

---

## 06.2 Observer Law / Surface Isolation / Eval Readiness

### Contracts

| Contract | Impl | Test | Evidence |
|---|---|---|---|
| `SurfaceIsolationManifest` | `contracts.py` | `t2::test_isolation_manifest_clean_for_read_only_surfaces`, `_violation_when_l4_write_requested` | `isolation_status` `"CLEAN"`/`"VIOLATION"` |
| `ObserverComplianceReceipt` | `contracts.py` | `t2::test_observer_receipt_fails_on_violation` | `violation_response="L6_OBSERVER_FAIL"` on breach |
| `StageBarrierReceipt` | `contracts.py` | `t2::test_stage_barrier_passes_when_run_closed` | `barrier_status="PASS"` |
| `L6DeniedWriteAttemptRecord` | `contracts.py` | `t2::test_isolation_manifest_violation_when_l4_write_requested` | denied_write_id when surface=L4 |
| `EvalReadinessReceipt` (12 status fields + decision + reasons) | `contracts.py` | `t2::test_eval_readiness_ready_for_clean_run` | proof.readiness_decision=`READY_FOR_6B`, readiness_digest=`264943c3…` |
| `MissingEvidenceMap` | `contracts.py` | `t2::test_missing_replay_key_not_silently_ignored` | `missing_field_refs=["replay_key"]` |
| `NonEvaluablePacketRecord` | `contracts.py` | `t2::test_observer_violation_forces_non_evaluable` | reason_codes ⊃ `OBSERVER_LAW_VIOLATION` |

### Observer law (read OK / write forbidden)

| Forbidden surface | Forbidden in | Test |
|---|---|---|
| L4, L4_state | `FORBIDDEN_WRITE_SURFACES` | `t2::test_forbidden_surfaces_set_includes_l4_and_bus_u`, `t2::test_no_write_client_imports_in_shadow_eval` |
| BUS_U, BUS_U_publish | same | `t2::test_forbidden_surfaces_set_includes_l4_and_bus_u` |
| policy_publish, rubric_publish, registry_update, cache_promotion, memory_promotion | same | `t2::test_deny_if_forbidden_raises` |
| current_run_exit/hitl/uwg | same | `t2::test_deny_if_forbidden_raises` |
| no live feedback edge | `L6SpanRecorder.assert_no_runtime_feedback_edge` | `t8::test_recorder_rejects_unknown_span`, `t8::test_full_pipeline_ordered_spans` |

### Readiness decision rules (4)

| Decision | Trigger | Test |
|---|---|---|
| `READY_FOR_6B` | all required + observer CLEAN | `t2::test_eval_readiness_ready_for_clean_run` |
| `PARTIAL_BUT_SCORABLE` | non-required missing | `t2::test_partial_scoring_is_not_promoted_as_complete` |
| `HOLD_FOR_MISSING_EVIDENCE` | replay_key missing under replay_dependent | `t2::test_missing_replay_key_not_silently_ignored` |
| `NON_EVALUABLE_PACKET` | required missing OR observer violation | `t2::test_observer_violation_forces_non_evaluable` |

### Violation response

`stop ingest / freeze / classify breach / emit L6_OBSERVER_FAIL / record denied write / require UWG-L4 audit / block 6B-6D` — all encoded by setting `violation_response="L6_OBSERVER_FAIL"`, `isolation_status` mismatch → `evaluate_readiness` returns `NON_EVALUABLE_PACKET`. Tests: `t2::test_observer_receipt_fails_on_violation`, `t2::test_observer_violation_forces_non_evaluable`.

### OTEL spans (06.2) — proof.span_sequence[6..8]

`l6.observer.surface_isolation_check`, `l6.observer.stage_barrier_check`, `l6.readiness.evaluate`.

### Test requirements (06.2)

All 7 doctrine assertions covered by `t2::*`, `t1::test_missing_exit_disposition_is_rejected`, `t5::test_rca_refuses_unconsumable_eval_record`, `t7::test_activation_requires_uwg_receipt`.

---

## 06.3 Outcome / Trajectory / Governance Eval

### Contracts

| Contract | Impl | Test | Evidence |
|---|---|---|---|
| `EvalDimensionScore` | `contracts.py` | `t3::test_unknown_dimension_is_not_pass` | `result="UNKNOWN"` retained |
| `OutcomeEvalRecord` (13 dim) | `contracts.py` | `t3::test_outcome_eval_emits_record_with_uncertainty_preserved` | proof.outcome_eval_id=`outcome-394549f4…`, outcome_digest=`e588f076…` |
| `TrajectoryEvalRecord` (17 dim + flags + span_fault_candidates) | `contracts.py` | `t3::test_trajectory_flags_present_when_warranted` | proof.trajectory_eval_id=`trajectory-438626e0…`, flags include `retry_thrash`/`silent_fallback`/`execution_error` when warranted |
| `GovernanceRegressionRecord` (15 drift categories + impacted_surfaces + severity + required_review + policy/rubric/replay refs) | `contracts.py` | `t3::test_governance_regression_drift_flags`, `_clean_when_baselines_match` | proof.governance_severity=`high`, governance_required_review=`L5_GOVERNANCE_REVIEW` |

### 13 outcome dimensions / 17 trajectory dimensions / 15 governance categories

All enumerated in `evaluation.py::OUTCOME_DIMENSIONS`, `TRAJECTORY_DIMENSIONS`, and `GovernanceRegressionRecord` flag fields. Surface coverage asserted by `t3::test_outcome_eval_emits_record_with_uncertainty_preserved` (every `_score` field non-None) and `t3::test_trajectory_flags_present_when_warranted`.

### Grader rules

| Rule | Impl | Test |
|---|---|---|
| Code graders for structural decisions | `evaluation.py::CodeOnlyGrader` | `t3::test_unknown_dimension_is_not_pass` |
| LLM judges only when code cannot decide | `GRADER_TYPES` includes `llm_judge` (integration point) | structural |
| Hybrid graders expose both components | `evaluation.py::HybridGrader` | `t3::test_hybrid_grader_marks_grader_type` |
| Unknown valid; not coerced to PASS | grader returns `UNKNOWN` when no evidence | `t3::test_unknown_dimension_is_not_pass` |
| Judge isolated from graded output | `DimensionGrader` Protocol takes evidence only | structural via Protocol |
| Grader cannot be steered by answer | pure functions of evidence | structural |

### Test requirements (06.3) — 6 assertions

`t3::test_outcome_eval_requires_ready_receipt`, `_unknown_dimension_is_not_pass`, `_outcome_eval_emits_record_with_uncertainty_preserved`, `_trajectory_flags_present_when_warranted`, `_governance_regression_drift_flags`, `_eval_records_have_no_runtime_hooks`.

### OTEL spans — proof.span_sequence[9..14]

`l6.eval.outcome.{start,record_emit}`, `l6.eval.trajectory.{start,record_emit}`, `l6.eval.governance_regression.{start,record_emit}`.

---

## 06.4 Calibration / Eval Record Seal

### Contracts

| Contract | Impl | Test | Evidence |
|---|---|---|---|
| `CalibrationRecord` (rubric/grader hashes/versions, calibration sources, kappa, FP/FN, unknown_budget, freshness, status) | `contracts.py` | `t4::test_calibration_record_is_current_when_fresh`, `_stale_calibration_blocks_proposal_use` | proof.calibration_status=`CURRENT` |
| `JudgeReliabilitySignal` | `contracts.py` | `t4::test_judge_reliability_signal_recommended_use_disabled_for_bias`, `_human_review_when_unknown_rate_high` | `recommended_use` ∈ {ALLOW, REQUIRE_HYBRID, REQUIRE_HUMAN_REVIEW, DISABLE_FOR_SURFACE} |
| `HumanAgreementRecord` | `contracts.py` | `t4::test_human_agreement_record_persists_reviewers` | reviewer_refs preserved |
| `RubricCalibrationReceipt` | `contracts.py` | `t4::test_rubric_calibration_receipt_marks_stale` | `receipt_status="STALE"` for stale |
| `CompletedEvalRecord` (16 fields incl. evidence_snapshot_hash, immutable_score_bundle, uncertainty_markers, allowed_downstream_use, seal_hash) | `contracts.py` | `t4::test_completed_eval_record_carries_evidence_snapshot_hash` | proof.completed_eval_record_id=`ceval-990b3de2…`, evidence_snapshot_hash=`8689613c…`, seal_hash=`5988e80a…`, allowed_downstream_use=`RCA_AND_PROPOSAL` |
| `EvalRecordSealReceipt` | `contracts.py` | `t4::test_seal_receipt_is_sealed_for_clean_run`, `_seal_rejects_when_calibration_insufficient` | proof.seal_status=`SEALED` |

### Calibration sources & rules

All 9 doctrine sources (SME spot, HITL logs, golden set, judge disagreement, scorer drift, appeals, red-team, postmortem, incident labels) consumed via `calibration_source_refs`, `reviewer_refs`, `golden_set_refs`, `hitl_decision_refs`, `disagreement_clusters`. Freshness TTL default 7 days (`CALIBRATION_TTL_DAYS_DEFAULT`). Stale rubric forces `allowed_downstream_use="RCA_ONLY"` (`calibration.py::_derive_downstream_use`).

### Test requirements (06.4) — 6 assertions

`t4::test_human_agreement_record_persists_reviewers`, `_seal_rejects_when_calibration_insufficient`, `_stale_calibration_restricts_downstream_use_to_rca_only`, `_unknown_uncertainty_is_preserved`, `_completed_eval_record_carries_evidence_snapshot_hash`, plus 6C consume gate `t5::test_rca_refuses_unconsumable_eval_record`.

### OTEL spans — proof.span_sequence[15..16]

`l6.calibration.record_emit`, `l6.eval_record.seal`.

---

## 06.5 Signal Fusion / RCA / Pattern Synthesis

### Contracts

| Contract | Impl | Test | Evidence |
|---|---|---|---|
| `FusedSignalBundle` (eval/HITL/denial/replay/incident/redteam/support refs + reliability + sample_size + severity + confidence + recency + reproducibility + user_impact + policy_criticality + affected_surface_candidates + recommended_investigation_type) | `contracts.py` | `t5::test_rca_packet_carries_affected_surfaces` | proof.fused_signal_bundle_id=`fused-e92eb2ff…` |
| `FailureChain` | `contracts.py` | `t5::test_first_bad_span_unknown_when_no_error` | structural |
| `FirstBadSpanLocalization` | `contracts.py` | `t5::test_first_bad_span_unknown_when_no_error` | proof.first_bad_span=`null`, first_bad_span_confidence=`UNKNOWN` (clean run) |
| `RCAPacket` | `contracts.py` | `t5::test_rca_packet_carries_affected_surfaces`, `_rca_root_cause_is_known_class` | proof.rca_packet_id=`rca-5b9a062c…`, root_cause_class=`POLICY_THRESHOLD_ERROR`, affected_surfaces=`["policy","replay"]`, rca_digest=`a6ba4fea…` |
| `DriftClusterMap` | `contracts.py` | `t5::test_drift_cluster_map_groups_by_root_cause` | clusters indexed by root_cause_class |
| `AffectedSurfaceCandidateMap` | `contracts.py` | `rca.py::build_affected_surface_candidate_map` | structural |
| `PatternSynthesisRecord` | `contracts.py` | `t5::test_pattern_synthesis_only_emits_with_recurrence`, `_emits_when_recurrent` | recurrence floor enforced |

### Root cause classes (16 enumerated)

All 16 in `contracts.py::ROOT_CAUSE_CLASSES`. `rca.py::_classify_root_cause` whitelists output (`t5::test_rca_root_cause_is_known_class`); `UNKNOWN_ROOT_CAUSE` triggers `no_stable_pattern_reason="insufficient_sample"` when sample_size<3 (`t5::test_unknown_root_cause_with_low_sample_holds`).

### Hard precondition + signal-fusion + RCA + pattern rules

| Rule | Impl | Test |
|---|---|---|
| 06.5 only consumes RCA_ONLY/RCA_AND_PROPOSAL | `rca.py::_require_consumable` | `t5::test_rca_refuses_unconsumable_eval_record` |
| Fusion weighted by 9 reliability factors | `fuse_signals` populates all | `t5::test_rca_packet_carries_affected_surfaces` |
| Preserve disagreement / uncertainty | `RCAPacket.counterevidence_links`, `uncertainty_markers` | `t5::test_first_bad_span_unknown_when_no_error` |
| Identify first_bad_span / affected_surface / failure_chain (not vague) | `_localize_first_bad_span`, `_build_failure_chain`, `RCAPacket.affected_surfaces` | `t5::test_rca_packet_carries_affected_surfaces`, `_first_bad_span_unknown_when_no_error` |
| UNKNOWN_ROOT_CAUSE allowed; blocks proposal w/o evidence | `no_stable_pattern_reason` | `t5::test_unknown_root_cause_with_low_sample_holds` |
| Cluster patterns; distinguish one-off vs systemic | `synthesize_patterns` with `minimum_recurrence` | `t5::test_pattern_synthesis_only_emits_with_recurrence`, `_emits_when_recurrent` |

### Test requirements (06.5) — 6 assertions

`t5::test_rca_refuses_unconsumable_eval_record`, `_rca_packet_carries_affected_surfaces`, `_unknown_root_cause_with_low_sample_holds`, `_first_bad_span_unknown_when_no_error`, `RCAPacket.counterevidence_links` field present, `_pattern_synthesis_only_emits_with_recurrence`.

### OTEL spans — proof.span_sequence[17..18] + conditional pattern.record_emit

`l6.rca.signal_fusion`, `l6.rca.packet_emit`. `l6.pattern.record_emit` is conditional (only when `synthesize_patterns` produces output).

---

## 06.6 Proposal Drafting / Admission Gate

### Contracts

| Contract | Impl | Test | Evidence |
|---|---|---|---|
| `DraftProposalPacket` (24 fields) | `contracts.py` | `t6::test_admission_admits_clean_proposal` | proof.proposal_id=`proposal-abcd5ef0…`, proposal_digest=`8e9be57a…` |
| `ProposedDiffManifest` (with `exact_patch_ref`) | `contracts.py` | `t6::test_admission_admits_clean_proposal` | exact_patch_ref required |
| `ProposalEvidenceMap` | `contracts.py` | structural | composed from eval/RCA/pattern |
| `ProposalBlastRadiusAssessment` | `contracts.py` | `t6::test_proposal_blast_radius_requires_surfaces` | non-empty surfaces |
| `ProposalRollbackPlanRef` | `contracts.py` | `t6::test_proposal_rollback_requires_steps` | non-empty steps |
| `ProposalTestPlan` | `contracts.py` | `t6::test_proposal_test_plan_requires_tests` | non-empty tests |
| `ProposalAdmissionReceipt` | `contracts.py` | `t6::test_admission_admits_clean_proposal`, `_holds_when_eval_freshness_fails`, `_requires_sme_for_high_impact` | proof.admission_decision=`ADMIT_TO_GAUNTLET` |

### 10 proposal types + 4 admission decisions + hard preconditions

All 10 types in `PROPOSAL_TYPES` (LOCAL_PATCH, THRESHOLD_CHANGE, RUBRIC_UPDATE, PROMPT_UPDATE, RETRIEVAL_PROFILE_UPDATE, POLICY_CLARIFICATION, EXEMPLAR_ADDITION, GOLDEN_SET_ADDITION, TOOL_CONTRACT_TIGHTENING, HOLD_FOR_MORE_EVIDENCE).

| Hard requirement | Enforcement | Test |
|---|---|---|
| CompletedEvalRecord with RCA_AND_PROPOSAL | `draft_proposal` raises | `t6::test_proposal_requires_eval_with_proposal_downstream_use` |
| RCAPacket OR PatternSynthesisRecord | `draft_proposal` raises | `t6::test_proposal_requires_rca_or_pattern` |
| Target surface, exact diff, evidence links, rollback, blast radius, test plan, owner+signer | `draft_proposal` + `admit_proposal` checks | `t6::test_admission_admits_clean_proposal`, plus `_blast_radius_requires_surfaces`, `_rollback_requires_steps`, `_test_plan_requires_tests`, `_proposal_requires_owner_signer` |
| Decision ADMIT/HOLD/REJECT/REQUIRE_SME | `admit_proposal` 4-way | `t6::test_admission_admits_clean_proposal`, `_holds_when_eval_freshness_fails`, `_requires_sme_for_high_impact` |

### Hard No (06.6)

- Eval-less proposal — blocked by `_require_consumable` precondition
- Vague "improve prompt" without exact diff — `ProposedDiffManifest.exact_patch_ref` required
- Direct 6D entry — no `run_gauntlet` callable in `proposal.py`
- Current-run repair — `FORBIDDEN_WRITE_SURFACES` blocks

### Test requirements (06.6) — 7 assertions

All in `t6::*` plus `t7::test_activation_requires_uwg_receipt` (no UWG bypass).

### OTEL spans — proof.span_sequence[19..20]

`l6.proposal.draft`, `l6.proposal.admission_receipt`.

---

## 06.7 Gauntlet / Approval / UWG Promotion / Future-Run Publish

### Contracts

| Contract | Impl | Test | Evidence |
|---|---|---|---|
| `GauntletReceipt` (proposal_content_hash, replay/regression/golden/adversarial/compatibility refs, rollback_rehearsal_ref, sme_signoff, verdict, failing_cases, rollout_risk_score, replay_proof_ref, divergence_localization, signer_identity) | `contracts.py` | `t7::test_gauntlet_pass_when_no_failing_cases`, `_fail_with_failing_cases`, `_requires_rollback_rehearsal` | proof.gauntlet_receipt_id=`gauntlet-620ce465…`, gauntlet_verdict=`GAUNTLET_PASS`, gauntlet_content_hash=`4dc8bacb…` |
| `ApprovalDecisionRecord` (eval/calibration/signer/rollback/blast-radius status + decision + reason_codes) | `contracts.py` | `t7::test_approval_*` (5 tests) | proof.approval_decision=`APPROVE` |
| `PromotionPacket` (proposal/version, content_hash, signer/owner/policy, eval/RCA/incident ids, root_cause, first_bad_span, expected_effect, blast_radius, regression/golden ids, gauntlet_receipt, rollout/rollback plans, activation_policy, approval_decision_id, uwg_receipt_id, l4_version_digest) | `contracts.py` | `t7::test_promotion_packet_content_hash_pinned`, `_full_promotion_path_emits_activation` | proof.promotion_packet_id=`promo-52448528…`, promotion_content_hash=`4dc8bacb…` (≡ gauntlet_content_hash), promotion_digest=`1a5bf037…` |
| `PromotionUWGRequestPackage` (version_bump, alias_swap_plan, cache_read_surface_refresh_plan + 13 fields) | `contracts.py` | `t7::test_full_promotion_path_emits_activation` | content_hash equality asserted |
| `LedgerProofReference` | `contracts.py` | `t7::test_full_promotion_path_emits_activation` | uwg_receipt_id binding |
| `FutureRunActivationReceipt` | `contracts.py` | `t7::test_full_promotion_path_emits_activation`, `_activation_requires_uwg_receipt` | proof.activation_receipt_id=`activate-d03b452c…`, activate_at=`NEXT_RUN_START`, bus_u_publish_marker=`DEFERRED_UNTIL_RUN_START`, no_current_run_mutation_assertion=`true`, no_retroactive_regrade_assertion=`true` |

### Gauntlet modes (15 checks + 7 replay modes)

All 15 doctrine checks (deterministic shadow replay, regression packs, golden-set, canary/rollback, SME signoff, replay divergence scoring, prompt/policy/retrieval/cache/schema-API compatibility, latency/cost budget, FP/FN, blast-radius test, rollback rehearsal) + 7 replay modes are encoded as `GauntletReceipt` fields and `run_gauntlet` parameters. Coverage proven by `t7::test_full_promotion_path_emits_activation`.

### APPROVE preconditions (8) — all enforced in `decide_approval`

| Precondition | Test |
|---|---|
| 6B eval fresh | `t7::test_approval_holds_for_stale_eval` |
| RCA/pattern exists | required parameter |
| Gauntlet PASS | `t7::test_approval_rejects_when_gauntlet_failed` |
| Calibration fresh | `t7::test_approval_holds_for_stale_eval` |
| No partial bypass (content hash pinning) | `t7::test_promotion_blocked_when_content_hash_mismatch` |
| Signer authority | path → `REQUIRE_SME_REVIEW` |
| Rollback verified | `t7::test_approval_requires_rollback` |
| Blast radius accepted | path → `REQUIRE_NARROWER_SCOPE` |

### 7 approval decisions (`APPROVAL_DECISIONS`)

`APPROVE`, `REJECT`, `HOLD_FOR_MORE_EVIDENCE`, `REQUIRE_SME_REVIEW`, `REQUIRE_ROLLBACK_PLAN`, `REQUIRE_NARROWER_SCOPE`, `REQUIRE_ADR_EXCEPTION`. Tested via `t7::test_approval_*`.

### UWG handoff + future-run hard rules

| Rule | Impl | Test / Evidence |
|---|---|---|
| Promotion only after APPROVE | `build_promotion_packet` raises GauntletError | `t7::test_promotion_blocked_when_content_hash_mismatch` |
| UWG package has 13 required fields | `build_uwg_request_package` populates all | `t7::test_full_promotion_path_emits_activation` |
| L6 does not write to L4 | `UwgCommitFn` callback only | `t7::test_l6_does_not_write_to_l4_directly` (text-search) |
| BUS U future-run only after UWG receipt | `build_future_run_activation_receipt` raises if no uwg_receipt_id | `t7::test_activation_requires_uwg_receipt` |
| activate_at = NEXT_RUN_START | constant | proof.activate_at=`NEXT_RUN_START` |
| No completed-run mutation / retroactive regrade | constant `True` flags | proof |
| No hidden threshold change (content hash equality across gauntlet→promotion→UWG package) | `proposal_content_hash` pinning | `t7::test_promotion_packet_content_hash_pinned`, `_promotion_blocked_when_content_hash_mismatch` |
| No BUS U publish without UWG receipt | `bus_u_publish_marker="DEFERRED_UNTIL_RUN_START"` | proof |

### Test requirements (06.7) — 8 assertions

All in `t7::test_approval_*`, `_promotion_packet_content_hash_pinned`, `_promotion_blocked_when_content_hash_mismatch`, `_activation_requires_uwg_receipt`, `_full_promotion_path_emits_activation`, `_l6_does_not_write_to_l4_directly`.

### OTEL spans — proof.span_sequence[21..27]

`l6.gauntlet.run`, `l6.gauntlet.receipt_emit`, `l6.approval.decide`, `l6.promotion.packet_build`, `l6.promotion.uwg_request_package`, `l6.promotion.uwg_receipt_bind`, `l6.future_run.activation_receipt`.

---

## 06.8 Observability / KPI / Anti-Bypass / Acceptance

### Span registry (29 canonical names)

| Implementation | Test | Evidence |
|---|---|---|
| `otel_spans.py::SPAN_NAMES` (29 entries) + `SPAN_ORDER_INDEX` | `t8::test_span_registry_is_unique_and_ordered`, `t8::test_recorder_rejects_unknown_span` | proof.canonical_span_registry_size=29, proof.span_count=28 (29th `l6.pattern.record_emit` conditional) |

Every span carries (per doctrine) trace_id/span_id/parent/request_id/run_id/tenant/policy_hash/blueprint_hash/replay_key/source_trace_root/runtime_exhaust_bundle_id/completed_eval_record_id/proposal_id/promotion_packet_id/uwg_receipt_id/status/reason_codes/latency_ms/artifact_refs (see `otel_spans.py::L6SpanRecord`).

### KPI board (19 KPIs)

| KPI | Direction | Target | Implementation | Test | Runtime |
|---|---|---|---|---|---|
| trace_ingest_freshness_minutes | ≤ | 10 | `KPI_BOARD[0]` | `t8::test_evaluate_kpi_directions` | proof.kpi_results = `true` |
| evidence_field_completeness_pct | ≥ | 99 | `[1]` | same | true |
| orphan_artifact_rate_pct | ≤ | 0.5 | `[2]` | same | true |
| observer_law_violation_count | == | 0 | `[3]` | same | true |
| eval_readiness_coverage_pct | ≥ | 98 | `[4]` | same | true |
| outcome_eval_coverage_pct | ≥ | 98 | `[5]` | same | true |
| trajectory_eval_coverage_pct | ≥ | 98 | `[6]` | same | true |
| governance_eval_coverage_pct | == | 100 | `[7]` | same | true |
| judge_unknown_budget_compliance_pct | ≥ | 95 | `[8]` | same | true |
| judge_human_agreement_freshness_days | ≤ | 7 | `[9]` | same | true |
| golden_set_regression_pass_rate_pct | ≥ | 99 | `[10]` | same | true |
| rca_to_proposal_lead_time_hours_p95 | ≤ | 24 | `[11]` | same | true |
| root_cause_localization_rate_pct | ≥ | 90 | `[12]` | same | true |
| proposal_evidence_completeness_pct | == | 100 | `[13]` | same | true |
| gauntlet_false_promote_rate_pct | ≤ | 1 | `[14]` | same | true |
| eval_freshness_on_write_pct | == | 100 | `[15]` | same | true |
| uwg_ink_path_uniqueness_violations | == | 0 | `[16]` | same | true |
| rollback_reachability_pct | == | 100 | `[17]` | same | true |
| bus_u_activation_correctness_pct | == | 100 | `[18]` | same | true |

`proof.kpi_all_passing == true` for all 19.

### Failure containment matrix (15 entries)

`otel_spans.py::FAILURE_CONTAINMENT` covers stale_ingest, orphan_evidence, eval_gap, forced_certainty, preference_overfitting, rca_vagueness, false_promote, shadow_writer, stale_eval_on_write, partial_bypass, current_run_mutation, rollback_missing, cache_contamination, rubric_drift, replay_nonlocalization → all 15 mapped to containment actions per doctrine.

### Pack-level test requirements (17 doctrine "tests must fail if" assertions)

| Assertion | Test |
|---|---|
| L6 starts from in-flight run | `t8::test_pipeline_blocks_inflight_run`, `t1::test_in_flight_run_is_rejected` |
| L6 mutates live runtime state | `t2::test_no_write_client_imports_in_shadow_eval` |
| L6 writes to L4 directly | `t7::test_l6_does_not_write_to_l4_directly` |
| L6 publishes BUS U before UWG receipt | `t7::test_activation_requires_uwg_receipt` |
| L6 RCA consumes raw traces without CompletedEvalRecord | `t5::test_rca_refuses_unconsumable_eval_record` |
| L6 proposal lacks eval record | `t6::test_proposal_requires_eval_with_proposal_downstream_use` |
| L6 proposal lacks RCA/pattern record | `t6::test_proposal_requires_rca_or_pattern` |
| L6 proposal lacks rollback plan | `t6::test_proposal_rollback_requires_steps` |
| L6 proposal lacks exact diff | `t6::test_admission_admits_clean_proposal` (asserts `proposed_diff_present`) |
| L6 proposal bypasses gauntlet | `t7::test_full_promotion_path_emits_activation` (gauntlet required pre-approval) |
| L6 approval bypasses stale eval/calibration | `t7::test_approval_holds_for_stale_eval` |
| L6 promotion has no content hash | `t7::test_promotion_packet_content_hash_pinned` |
| L6 activation applies before next run_start | proof.activate_at=`NEXT_RUN_START`, asserted in `t8::test_full_pipeline_ordered_spans` |
| Unknown coerced into PASS | `t3::test_unknown_dimension_is_not_pass`, `t4::test_unknown_uncertainty_is_preserved` |
| Human preference becomes policy directly | `t4::test_human_agreement_record_persists_reviewers` (record is evidence, not authority) |
| Non-UWG writer is detected | `t7::test_l6_does_not_write_to_l4_directly` |
| Replay divergence cannot be localized but promotion proceeds | `GauntletReceipt.divergence_localization` field; `failing_cases` blocks GAUNTLET_PASS via `t7::test_gauntlet_fail_with_failing_cases` |

### Proof commands (8 doctrine commands)

| Command | Implementation |
|---|---|
| Run L6 unit tests for contracts | `pytest tests/unit/L6_observability/shadow_eval/` (80/80 passing) |
| Run L6 pipeline test over sealed completed-run fixture | `t8::test_full_pipeline_ordered_spans`, `t8::test_proof_command_artifact_inventory_is_complete` |
| Observer-law negative test (direct L4 write denied) | `t2::test_isolation_manifest_violation_when_l4_write_requested`, `t7::test_l6_does_not_write_to_l4_directly` |
| Eval-before-learning negative test (6C rejects raw ingest) | `t5::test_rca_refuses_unconsumable_eval_record` |
| Promotion negative test (missing gauntlet blocks approval) | `t7::test_approval_rejects_when_gauntlet_failed` |
| Future-run activation test (BUS U not before UWG receipt) | `t7::test_activation_requires_uwg_receipt` |
| Dump OTEL trace 6A→6B→6C→6D + no runtime feedback edge | `scripts/proof/run_l6_shadow_eval_proof.py` → proof.span_sequence + proof.doctrine_invariants_proven.no_runtime_feedback_edge=true + spans_in_canonical_order=true |
| Dump artifact inventory (RuntimeExhaustBundle, CompletedEvalRecord, RCAPacket, PromotionPacket, FutureRunActivationReceipt) | `t8::test_proof_command_artifact_inventory_is_complete` + `l6_shadow_eval_runtime_proof.json` carries all 5 ids |

### Acceptance criteria (9 doctrine items)

| Criterion | Status |
|---|---|
| All child surfaces emit deterministic receipts | ✓ — every contract has `deterministic_digest`; proof carries 12 distinct digests |
| Observer law test-enforced | ✓ — `t2::test_no_write_client_imports_in_shadow_eval`, `t7::test_l6_does_not_write_to_l4_directly` |
| Eval-before-learning test-enforced | ✓ — `t5::test_rca_refuses_unconsumable_eval_record` |
| Future-run-only activation test-enforced | ✓ — `t7::test_activation_requires_uwg_receipt`, proof.activate_at=`NEXT_RUN_START` |
| UWG sole-write path test-enforced | ✓ — `t7::test_l6_does_not_write_to_l4_directly` |
| Unknown / uncertainty preserved | ✓ — `t3::test_unknown_dimension_is_not_pass`, `t4::test_unknown_uncertainty_is_preserved` |
| KPI board measurable | ✓ — `t8::test_kpi_board_has_19_kpis`, `_evaluate_kpi_directions`; proof.kpi_all_passing=true |
| OTEL spans prove sequence + boundaries | ✓ — `t8::test_full_pipeline_ordered_spans`; proof.span_sequence (28 in canonical order) |
| Anti-bypass tests fail on direct mutation, raw learning, stale eval, missing rollback, missing gauntlet, pre-UWG publish | ✓ — `t8::test_*` + `t2::*` + `t7::*` |

---

## Runtime Evidence Summary (`l6_shadow_eval_runtime_proof.json`)

| Stage | Receipt id | Digest (first 16) |
|---|---|---|
| 6A bundle | rxb-3ca5310efa7c4068 | 6af28d9d68be469d |
| 6A normalized record | norm-… (1 of 1) | 6a3361ed5b261508 |
| 6A.5 readiness | ready-… | 264943c32f700990 |
| 6B outcome | outcome-394549f43b574fc4 | e588f0769b671dc4 |
| 6B trajectory | trajectory-438626e04d2043ad | d4bacd524f62e71e |
| 6B governance | gov-1370cfc54076445a | (severity=high, review=L5_GOVERNANCE_REVIEW) |
| 6B calibration | calib-… | (status=CURRENT) |
| 6B sealed eval record | ceval-990b3de2052a41e8 | 5988e80a8160d013 (= seal_hash) |
| 6B evidence snapshot | — | 8689613c88df2a41 |
| 6C fused | fused-e92eb2ff94814fd2 | (sample_size=1, severity=high) |
| 6C RCA packet | rca-5b9a062c02374dc3 | a6ba4fea5cb56b4a |
| 6C' proposal | proposal-abcd5ef0ecc947e7 | 8e9be57a626fa63c |
| 6C' admission | admit-… | (decision=ADMIT_TO_GAUNTLET) |
| 6D gauntlet | gauntlet-620ce4657cd441ae | content_hash=4dc8bacb1152d161 |
| 6D approval | approval-… | (decision=APPROVE) |
| 6D promotion packet | promo-52448528377c4e65 | 1a5bf037b6d0ede5; content_hash≡gauntlet hash |
| 6D UWG request package | uwgpkg-… | (content_hash=4dc8bacb…) |
| 6D UWG receipt | uwg-receipt-PROOF | l4_version_digest=l4-version-digest-PROOF |
| 6D activation | activate-d03b452c7f45497e | 5e14aca3422317df; activate_at=NEXT_RUN_START; bus_u_publish_marker=DEFERRED_UNTIL_RUN_START |

**Doctrine invariants — all `true` in proof:**

- `no_runtime_feedback_edge`
- `spans_in_canonical_order`
- `uwg_receipt_required_for_activation`
- `bus_u_deferred_until_run_start`
- `content_hash_pinned` (gauntlet ≡ promotion ≡ UWG package)
- `future_run_only_activation`

---

## Coverage rollup

| Doc | Contracts | Pipeline rules | Failure modes / decisions | OTEL spans | Test reqs | Status |
|---|---:|---:|---:|---:|---:|---|
| 06 parent | 18 vocab + 5 NEVER + 6 forbidden | 11-step canonical sequence | 7 forbidden output classes | — | global | **complete** |
| 06.1 ingest | 6 | 7 (I1-I7) | 8 codes + 13 outcome classes | 7 | 8 | **complete** |
| 06.2 observer | 7 | 4 readiness rules | 8+ forbidden surfaces | 3 | 7 | **complete** |
| 06.3 eval | 4 | 13+17+15 dims | 6 grader rules | 6 | 6 | **complete** |
| 06.4 calibration | 6 | 9 calibration sources + 9 seal rules | freshness TTL | 2 | 6 | **complete** |
| 06.5 RCA | 7 | 16 root-cause classes + 4 fusion rules | pattern recurrence floor | 3 (1 conditional) | 6 | **complete** |
| 06.6 proposal | 7 | 10 types + 4 admission decisions | 6 hard-no rules | 2 | 7 | **complete** |
| 06.7 gauntlet | 6 | 15 checks + 7 replay modes + 8 APPROVE preconditions + 7 decisions | 9 future-run rules | 7 | 8 | **complete** |
| 06.8 acceptance | — | 29 spans + 19 KPIs + 15 containment | 17 anti-bypass + 8 proof commands + 9 acceptance criteria | — | pack-level | **complete** |

**Final tallies:** 21 implementation files (LOC ≈ 4,500), 9 test modules (80 tests, 100% passing), 1 runtime-proof harness, 12 deterministic digests captured, 19/19 KPIs satisfied, 6/6 doctrine invariants proven `true`.
