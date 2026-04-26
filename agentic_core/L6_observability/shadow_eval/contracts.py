"""Canonical L6 shadow-evaluation contracts (v6 06.x doctrine).

These dataclasses are the durable serialization shape for every L6 stage
record described in:

* 06.1 Runtime Exhaust Ingest and Normalization
* 06.2 Observer Law, Surface Isolation, and Eval Readiness
* 06.3 Outcome, Trajectory, and Governance Evaluation
* 06.4 Human Calibration and Eval Record Seal
* 06.5 Signal Fusion, RCA, and Pattern Synthesis
* 06.6 Proposal Drafting and Admission Gate
* 06.7 Gauntlet, Approval, UWG Promotion, and Future-Run Publish

All records are frozen and slot-based. ``deterministic_digest`` is filled by
``_digest.stamp_digest`` after construction. None of these dataclasses
perform any side effect — they are pure data carriers, in keeping with the
06.2 observer law (read-only, no L4 writes).
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Canonical L6 vocabulary
# ---------------------------------------------------------------------------

READY_FOR_EVAL = "READY_FOR_EVAL"
PARTIAL_BUT_SCORABLE = "PARTIAL_BUT_SCORABLE"
HOLD_FOR_MISSING_EVIDENCE = "HOLD_FOR_MISSING_EVIDENCE"
NON_EVALUABLE_PACKET = "NON_EVALUABLE_PACKET"
EVAL_SEALED = "EVAL_SEALED"
SIGNAL_FUSED = "SIGNAL_FUSED"
RCA_COMPLETE = "RCA_COMPLETE"
PATTERN_CONFIRMED = "PATTERN_CONFIRMED"
PROPOSAL_DRAFTED = "PROPOSAL_DRAFTED"
ADMIT_TO_GAUNTLET = "ADMIT_TO_GAUNTLET"
HOLD_FOR_MORE_EVIDENCE = "HOLD_FOR_MORE_EVIDENCE"
REJECT_WEAK_PROPOSAL = "REJECT_WEAK_PROPOSAL"
REQUIRE_SME_REVIEW = "REQUIRE_SME_REVIEW"
GAUNTLET_PASS = "GAUNTLET_PASS"
GAUNTLET_FAIL = "GAUNTLET_FAIL"
APPROVED_FOR_UWG_REQUEST = "APPROVED_FOR_UWG_REQUEST"
REJECTED_FOR_PROMOTION = "REJECTED_FOR_PROMOTION"
FUTURE_RUN_ACTIVATION_READY = "FUTURE_RUN_ACTIVATION_READY"

# Run outcome stratification (06.1 §I7)
RUN_OUTCOME_CLASSES = frozenset(
    {
        "normal_success",
        "degraded_success",
        "safe_abstain",
        "denied_unsafe_request",
        "rerouted_request",
        "hitl_escalated",
        "tool_failure",
        "model_failure",
        "grounding_failure",
        "policy_failure",
        "replay_failure",
        "schema_failure",
        "unresolved_unknown",
    }
)

# 06.5 Root cause classes
ROOT_CAUSE_CLASSES = frozenset(
    {
        "ROUTE_MISS",
        "CACHE_FALSE_HIT",
        "RETRIEVAL_RECALL_GAP",
        "RERANK_PRECISION_GAP",
        "GRAPH_CONTEXT_GAP",
        "PROMPT_SLOT_ORDER_ERROR",
        "INSTRUCTION_CONFLICT",
        "TOOL_ARG_SCHEMA_ERROR",
        "PROVIDER_DRIFT",
        "POLICY_THRESHOLD_ERROR",
        "RUBRIC_CALIBRATION_ERROR",
        "HITL_GATE_ERROR",
        "UWG_SCOPE_ERROR",
        "REPLAY_INTEGRITY_ERROR",
        "EVIDENCE_LINEAGE_LOSS",
        "UNKNOWN_ROOT_CAUSE",
    }
)

# 06.6 Proposal types
PROPOSAL_TYPES = frozenset(
    {
        "LOCAL_PATCH",
        "THRESHOLD_CHANGE",
        "RUBRIC_UPDATE",
        "PROMPT_UPDATE",
        "RETRIEVAL_PROFILE_UPDATE",
        "POLICY_CLARIFICATION",
        "EXEMPLAR_ADDITION",
        "GOLDEN_SET_ADDITION",
        "TOOL_CONTRACT_TIGHTENING",
        "HOLD_FOR_MORE_EVIDENCE",
    }
)

# 06.7 Approval decisions
APPROVAL_DECISIONS = frozenset(
    {
        "APPROVE",
        "REJECT",
        "HOLD_FOR_MORE_EVIDENCE",
        "REQUIRE_SME_REVIEW",
        "REQUIRE_ROLLBACK_PLAN",
        "REQUIRE_NARROWER_SCOPE",
        "REQUIRE_ADR_EXCEPTION",
    }
)

# 06.4 Allowed downstream use scopes
ALLOWED_DOWNSTREAM_USE = frozenset({"RCA_ONLY", "RCA_AND_PROPOSAL", "HOLD_ONLY", "NON_EVALUABLE"})

# Eval dimension result vocabulary
EVAL_DIMENSION_RESULTS = frozenset({"PASS", "FAIL", "WARN", "UNKNOWN", "NOT_APPLICABLE"})

GRADER_TYPES = frozenset({"code", "llm_judge", "hybrid", "human_calibrated_reference"})


# ---------------------------------------------------------------------------
# 06.1 — Ingest / Normalization contracts
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class ExhaustSourceManifest:
    manifest_id: str
    source_type: str
    source_ref: str
    source_hash: str
    source_schema_version: str
    observed_stage: str
    expected_stage_order: int
    lineage_parent_refs: list[str] = field(default_factory=list)
    lineage_child_refs: list[str] = field(default_factory=list)
    completeness_status: str = "UNKNOWN"
    trust_status: str = "UNKNOWN"
    gap_codes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class StageMap:
    stage_map_id: str
    observed_stages: list[str] = field(default_factory=list)
    expected_stages: list[str] = field(default_factory=list)
    missing_stages: list[str] = field(default_factory=list)
    impossible_order_flags: list[str] = field(default_factory=list)
    orphan_stage_refs: list[str] = field(default_factory=list)
    cross_stage_join_keys: dict[str, str] = field(default_factory=dict)
    route_id: str | None = None
    execution_form: str | None = None
    terminal_class: str | None = None
    exit_disposition: str | None = None
    uwg_commit_status: str | None = None


@dataclass(slots=True)
class ArtifactInventory:
    inventory_id: str
    generated_artifacts: list[str] = field(default_factory=list)
    sealed_artifacts: list[str] = field(default_factory=list)
    quarantined_artifacts: list[str] = field(default_factory=list)
    proposed_state_diffs: list[str] = field(default_factory=list)
    committed_state_refs: list[str] = field(default_factory=list)
    stdout_stderr_refs: list[str] = field(default_factory=list)
    file_hashes: dict[str, str] = field(default_factory=dict)
    artifact_lineage: dict[str, list[str]] = field(default_factory=dict)
    missing_artifact_refs: list[str] = field(default_factory=list)
    orphan_artifact_refs: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ExhaustGapReport:
    gap_report_id: str
    runtime_exhaust_bundle_id: str
    gap_codes: list[str] = field(default_factory=list)
    missing_evidence_refs: list[str] = field(default_factory=list)
    orphan_artifact_refs: list[str] = field(default_factory=list)
    impossible_order_flags: list[str] = field(default_factory=list)
    repair_required: bool = False
    notes: str = ""


@dataclass(slots=True)
class RuntimeExhaustBundle:
    runtime_exhaust_bundle_id: str
    request_id: str
    run_id: str
    session_id: str
    tenant_id: str
    trace_root: str
    completed_at: str
    runtime_boundary_crossed: bool
    source_exhaust_refs: list[str] = field(default_factory=list)
    route_contract_ref: str | None = None
    l1_plan_ref: str | None = None
    c0_evidence_contract_refs: list[str] = field(default_factory=list)
    prompt_envelope_refs: list[str] = field(default_factory=list)
    l2_artifact_refs: list[str] = field(default_factory=list)
    l3_workflow_package_ref: str | None = None
    exit_disposition_ref: str | None = None
    hitl_packet_refs: list[str] = field(default_factory=list)
    uwg_receipt_refs: list[str] = field(default_factory=list)
    policy_hash: str | None = None
    blueprint_hash: str | None = None
    replay_key: str | None = None
    source_lineage_manifest_ref: str | None = None
    artifact_inventory_ref: str | None = None
    ingest_gap_report_ref: str | None = None
    deterministic_digest: str = ""


@dataclass(slots=True)
class NormalizedEvidenceRecord:
    normalized_record_id: str
    runtime_exhaust_bundle_id: str
    canonical_event_type: str
    canonical_stage: str
    source_ref: str
    normalized_payload_ref: str
    trace_id: str
    span_id: str
    parent_span_id: str | None
    request_id: str
    run_id: str
    tenant_id: str
    route_id: str | None
    step_id: str | None = None
    attempt_id: str | None = None
    model_id: str | None = None
    tool_id: str | None = None
    provider_lane: str | None = None
    token_count_in: int = 0
    token_count_out: int = 0
    cost_estimate: float = 0.0
    latency_ms: float = 0.0
    retry_count: int = 0
    repair_count: int = 0
    fallback_depth: int = 0
    error_code: str | None = None
    reason_codes: list[str] = field(default_factory=list)
    policy_hash: str | None = None
    blueprint_hash: str | None = None
    replay_key: str | None = None
    prompt_hash: str | None = None
    context_hash: str | None = None
    artifact_digest: str | None = None
    eval_readiness_hint: str = "UNKNOWN"
    normalization_warnings: list[str] = field(default_factory=list)
    deterministic_digest: str = ""


# ---------------------------------------------------------------------------
# 06.2 — Observer law / readiness contracts
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class L6DeniedWriteAttemptRecord:
    denied_write_id: str
    runtime_exhaust_bundle_id: str
    target_surface: str
    operation: str
    reason_code: str
    timestamp: str
    stack_signature: str = ""


@dataclass(slots=True)
class SurfaceIsolationManifest:
    surface_isolation_manifest_id: str
    runtime_exhaust_bundle_id: str
    read_surfaces_touched: list[str] = field(default_factory=list)
    write_surfaces_requested: list[str] = field(default_factory=list)
    denied_write_attempts: list[str] = field(default_factory=list)
    credentials_scope: str = "READ_ONLY"
    token_scope: str = "READ_ONLY"
    storage_scope: str = "READ_ONLY"
    bus_publish_scope: str = "NONE"
    current_run_mutation_attempted: bool = False
    l4_write_attempted: bool = False
    bus_u_publish_attempted: bool = False
    isolation_status: str = "CLEAN"  # CLEAN | VIOLATION | UNKNOWN
    deterministic_digest: str = ""


@dataclass(slots=True)
class StageBarrierReceipt:
    stage_barrier_receipt_id: str
    current_run_closed: bool
    exit_disposition_present: bool
    uwg_status_closed_or_not_applicable: bool
    runtime_boundary_timestamp: str
    l6_start_timestamp: str
    boundary_violation_flags: list[str] = field(default_factory=list)
    barrier_status: str = "PASS"  # PASS | FAIL | UNKNOWN


@dataclass(slots=True)
class ObserverComplianceReceipt:
    observer_receipt_id: str
    runtime_exhaust_bundle_id: str
    observer_mode: str  # READ_ONLY
    read_only_credential_proof: str
    touched_surfaces: list[str] = field(default_factory=list)
    denied_write_attempt_refs: list[str] = field(default_factory=list)
    stage_barrier_status: str = "PASS"
    isolation_status: str = "CLEAN"
    no_live_feedback_assertion: bool = True
    no_bus_u_publish_assertion: bool = True
    no_l4_write_assertion: bool = True
    violation_response: str | None = None
    policy_hash: str | None = None
    blueprint_hash: str | None = None
    replay_key: str | None = None
    deterministic_digest: str = ""


@dataclass(slots=True)
class MissingEvidenceMap:
    missing_evidence_map_id: str
    runtime_exhaust_bundle_id: str
    missing_field_refs: list[str] = field(default_factory=list)
    repair_hints: dict[str, str] = field(default_factory=dict)
    blocking: bool = False


@dataclass(slots=True)
class NonEvaluablePacketRecord:
    non_evaluable_id: str
    runtime_exhaust_bundle_id: str
    reason_codes: list[str]
    excluded_from_learning_until: str | None = None


@dataclass(slots=True)
class EvalReadinessReceipt:
    eval_readiness_receipt_id: str
    runtime_exhaust_bundle_id: str
    observer_receipt_id: str
    trace_completeness_status: str
    artifact_integrity_status: str
    replay_key_status: str
    policy_hash_status: str
    route_contract_status: str
    prompt_hash_status: str
    source_lineage_status: str
    terminal_status_status: str
    evaluator_input_status: str
    readiness_decision: (
        str  # READY_FOR_6B | PARTIAL_BUT_SCORABLE | HOLD_FOR_MISSING_EVIDENCE | NON_EVALUABLE_PACKET
    )
    missing_evidence_map_ref: str | None = None
    excluded_from_learning_until: str | None = None
    reason_codes: list[str] = field(default_factory=list)
    deterministic_digest: str = ""


# ---------------------------------------------------------------------------
# 06.3 — Outcome / Trajectory / Governance Eval contracts
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class EvalDimensionScore:
    dimension_id: str
    dimension_name: str
    grader_type: str  # code | llm_judge | hybrid | human_calibrated_reference
    score: float
    threshold: float
    result: str  # PASS | FAIL | WARN | UNKNOWN | NOT_APPLICABLE
    confidence_band: str
    evidence_refs: list[str] = field(default_factory=list)
    support_rationale: str = ""
    uncertainty_markers: list[str] = field(default_factory=list)
    rubric_hash: str = ""
    grader_version: str = ""


@dataclass(slots=True)
class OutcomeEvalRecord:
    outcome_eval_id: str
    normalized_record_refs: list[str]
    completed_run_ref: str
    task_completion_score: EvalDimensionScore
    answer_correctness_score: EvalDimensionScore
    groundedness_score: EvalDimensionScore
    citation_support_score: EvalDimensionScore
    source_coverage_score: EvalDimensionScore
    evidence_sufficiency_score: EvalDimensionScore
    abstain_correctness_score: EvalDimensionScore
    refusal_correctness_score: EvalDimensionScore
    format_schema_fit_score: EvalDimensionScore
    user_constraint_adherence_score: EvalDimensionScore
    scope_discipline_score: EvalDimensionScore
    usefulness_score: EvalDimensionScore
    artifact_validity_score: EvalDimensionScore
    unsupported_claims: list[str] = field(default_factory=list)
    support_map_ref: str | None = None
    uncertainty_markers: list[str] = field(default_factory=list)
    result_summary: str = ""
    deterministic_digest: str = ""


@dataclass(slots=True)
class TrajectoryEvalRecord:
    trajectory_eval_id: str
    normalized_record_refs: list[str]
    route_fit_score: EvalDimensionScore
    tool_order_score: EvalDimensionScore
    tool_choice_score: EvalDimensionScore
    model_lane_selection_score: EvalDimensionScore
    argument_correctness_score: EvalDimensionScore
    retrieval_use_score: EvalDimensionScore
    prompt_assembly_correctness_score: EvalDimensionScore
    fallback_depth_score: EvalDimensionScore
    retry_thrash_score: EvalDimensionScore
    loop_productivity_score: EvalDimensionScore
    budget_behavior_score: EvalDimensionScore
    latency_behavior_score: EvalDimensionScore
    cost_behavior_score: EvalDimensionScore
    hitl_trigger_fit_score: EvalDimensionScore
    sandbox_scope_fit_score: EvalDimensionScore
    write_request_legitimacy_score: EvalDimensionScore
    evidence_preservation_score: EvalDimensionScore
    span_fault_candidates: list[str] = field(default_factory=list)
    trajectory_flags: list[str] = field(default_factory=list)
    deterministic_digest: str = ""


@dataclass(slots=True)
class GovernanceRegressionRecord:
    governance_regression_id: str
    exact_match_drift_flags: list[str] = field(default_factory=list)
    policy_drift_flags: list[str] = field(default_factory=list)
    schema_api_drift_flags: list[str] = field(default_factory=list)
    model_behavior_drift_flags: list[str] = field(default_factory=list)
    tool_behavior_drift_flags: list[str] = field(default_factory=list)
    provider_behavior_drift_flags: list[str] = field(default_factory=list)
    guardrail_failure_flags: list[str] = field(default_factory=list)
    refusal_abstain_drift_flags: list[str] = field(default_factory=list)
    citation_support_drift_flags: list[str] = field(default_factory=list)
    prompt_drift_flags: list[str] = field(default_factory=list)
    retrieval_profile_drift_flags: list[str] = field(default_factory=list)
    sandbox_escape_signals: list[str] = field(default_factory=list)
    hitl_threshold_drift_flags: list[str] = field(default_factory=list)
    uwg_receipt_drift_flags: list[str] = field(default_factory=list)
    replay_digest_drift_flags: list[str] = field(default_factory=list)
    impacted_surfaces: list[str] = field(default_factory=list)
    severity: str = "low"
    suspected_cause: str = "UNKNOWN"
    required_review: str = "NONE"
    policy_hash: str | None = None
    rubric_hash: str | None = None
    replay_digest: str | None = None
    deterministic_digest: str = ""


# ---------------------------------------------------------------------------
# 06.4 — Calibration / seal contracts
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class CalibrationRecord:
    calibration_record_id: str
    rubric_hash: str
    rubric_version: str
    grader_version: str
    calibration_source_refs: list[str] = field(default_factory=list)
    reviewer_refs: list[str] = field(default_factory=list)
    golden_set_refs: list[str] = field(default_factory=list)
    hitl_decision_refs: list[str] = field(default_factory=list)
    disagreement_clusters: list[str] = field(default_factory=list)
    kappa_or_agreement_score: float = 0.0
    false_positive_estimate: float = 0.0
    false_negative_estimate: float = 0.0
    unknown_budget_status: str = "WITHIN_BUDGET"
    severity_class_adjustments_proposed: list[str] = field(default_factory=list)
    escalation_threshold_updates_proposed: list[str] = field(default_factory=list)
    calibration_freshness_timestamp: str = ""
    calibration_status: str = "CURRENT"  # CURRENT | STALE | INSUFFICIENT | CONFLICTED
    deterministic_digest: str = ""


@dataclass(slots=True)
class JudgeReliabilitySignal:
    judge_reliability_signal_id: str
    grader_id: str
    task_class: str
    rubric_hash: str
    recent_agreement_score: float
    disagreement_rate: float
    unknown_rate: float
    forced_certainty_flags: list[str] = field(default_factory=list)
    bias_or_drift_flags: list[str] = field(default_factory=list)
    recommended_use: str = "ALLOW_FOR_EVAL"


@dataclass(slots=True)
class HumanAgreementRecord:
    human_agreement_id: str
    rubric_hash: str
    task_class: str
    samples: int
    agreement_rate: float
    reviewer_refs: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RubricCalibrationReceipt:
    rubric_calibration_receipt_id: str
    rubric_hash: str
    calibration_record_id: str
    receipt_status: str  # FRESH | STALE | INSUFFICIENT
    notes: str = ""


@dataclass(slots=True)
class CompletedEvalRecord:
    completed_eval_record_id: str
    runtime_exhaust_bundle_id: str
    eval_readiness_receipt_id: str
    outcome_eval_ref: str
    trajectory_eval_ref: str
    governance_regression_ref: str
    calibration_record_ref: str
    rubric_hash: str
    rubric_version: str
    grader_versions: list[str]
    evidence_snapshot_hash: str
    immutable_score_bundle: dict[str, float]
    uncertainty_markers: list[str] = field(default_factory=list)
    support_rationale_refs: list[str] = field(default_factory=list)
    reviewer_override_refs: list[str] = field(default_factory=list)
    allowed_downstream_use: str = "RCA_AND_PROPOSAL"  # see ALLOWED_DOWNSTREAM_USE
    seal_hash: str = ""
    hmac_sig: str | None = None
    deterministic_digest: str = ""


@dataclass(slots=True)
class EvalRecordSealReceipt:
    seal_receipt_id: str
    completed_eval_record_id: str
    required_eval_refs_present: bool
    calibration_status: str
    rubric_integrity_status: str
    evidence_snapshot_bound: bool
    uncertainty_preserved: bool
    downstream_use_scope: str
    seal_status: str  # SEALED | HOLD | REJECTED
    reason_codes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 06.5 — Signal fusion / RCA / pattern synthesis contracts
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class FusedSignalBundle:
    fused_signal_bundle_id: str
    completed_eval_record_refs: list[str]
    outcome_signal_refs: list[str] = field(default_factory=list)
    trajectory_signal_refs: list[str] = field(default_factory=list)
    governance_signal_refs: list[str] = field(default_factory=list)
    calibration_signal_refs: list[str] = field(default_factory=list)
    hitl_outcome_refs: list[str] = field(default_factory=list)
    denial_reroute_reason_refs: list[str] = field(default_factory=list)
    replay_failure_refs: list[str] = field(default_factory=list)
    incident_report_refs: list[str] = field(default_factory=list)
    red_team_failure_refs: list[str] = field(default_factory=list)
    support_report_refs: list[str] = field(default_factory=list)
    source_reliability_scores: dict[str, float] = field(default_factory=dict)
    evaluator_reliability_scores: dict[str, float] = field(default_factory=dict)
    sample_size: int = 0
    severity_class: str = "low"
    confidence_band: str = "low"
    recency_weight: float = 1.0
    reproducibility_score: float = 0.0
    user_impact_score: float = 0.0
    policy_criticality_score: float = 0.0
    affected_surface_candidates: list[str] = field(default_factory=list)
    recommended_investigation_type: str = "NONE"
    deterministic_digest: str = ""


@dataclass(slots=True)
class FailureChain:
    failure_chain_id: str
    steps: list[str] = field(default_factory=list)
    first_bad_stage: str | None = None
    final_observed_stage: str | None = None


@dataclass(slots=True)
class FirstBadSpanLocalization:
    localization_id: str
    span_id: str | None
    trace_id: str | None
    stage: str | None
    confidence: str = "UNKNOWN"


@dataclass(slots=True)
class RCAPacket:
    rca_packet_id: str
    fused_signal_bundle_id: str
    failure_chain: FailureChain
    first_bad_span: FirstBadSpanLocalization
    first_bad_stage: str | None
    root_cause_class: str  # see ROOT_CAUSE_CLASSES
    affected_surfaces: list[str]
    proposed_fix_surface: str | None
    evidence_links: list[str] = field(default_factory=list)
    counterevidence_links: list[str] = field(default_factory=list)
    confidence_band: str = "low"
    uncertainty_markers: list[str] = field(default_factory=list)
    incident_id: str | None = None
    no_stable_pattern_reason: str | None = None
    deterministic_digest: str = ""


@dataclass(slots=True)
class DriftClusterMap:
    drift_cluster_map_id: str
    clusters: dict[str, list[str]] = field(default_factory=dict)


@dataclass(slots=True)
class AffectedSurfaceCandidateMap:
    affected_surface_candidate_map_id: str
    candidates: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class PatternSynthesisRecord:
    pattern_id: str
    rca_packet_refs: list[str]
    examples: list[str] = field(default_factory=list)
    counterexamples: list[str] = field(default_factory=list)
    affected_surfaces: list[str] = field(default_factory=list)
    pattern_class: str = "UNKNOWN"
    recurrence_score: float = 0.0
    blast_radius_estimate: str = "UNKNOWN"
    confidence_band: str = "low"
    proposed_action_class: str = "WATCH"
    hold_watch_reason: str | None = None
    deterministic_digest: str = ""


# ---------------------------------------------------------------------------
# 06.6 — Proposal contracts
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class ProposedDiffManifest:
    proposed_diff_manifest_id: str
    target_surface: str
    operation_type: str
    before_ref: str
    after_candidate_ref: str
    diff_summary: str
    exact_patch_ref: str | None = None
    schema_ref: str | None = None
    validation_rules: list[str] = field(default_factory=list)
    affected_surfaces: list[str] = field(default_factory=list)
    compatibility_notes: str = ""
    deterministic_digest: str = ""


@dataclass(slots=True)
class ProposalEvidenceMap:
    proposal_evidence_map_id: str
    proposal_id: str
    eval_record_refs: list[str]
    rca_refs: list[str]
    pattern_refs: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ProposalBlastRadiusAssessment:
    blast_radius_id: str
    proposal_id: str
    affected_surfaces: list[str]
    affected_tests: list[str] = field(default_factory=list)
    rollout_risk_score: float = 0.0
    notes: str = ""


@dataclass(slots=True)
class ProposalRollbackPlanRef:
    rollback_plan_ref_id: str
    proposal_id: str
    rollback_steps: list[str]
    rehearsal_status: str = "UNTESTED"


@dataclass(slots=True)
class ProposalTestPlan:
    proposal_test_plan_id: str
    proposal_id: str
    affected_tests: list[str]
    regression_pack_refs: list[str] = field(default_factory=list)
    golden_set_refs: list[str] = field(default_factory=list)
    adversarial_case_refs: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DraftProposalPacket:
    proposal_id: str
    proposal_type: str  # see PROPOSAL_TYPES
    target_surface: str
    current_version_ref: str
    proposed_version_ref: str | None
    problem_statement: str
    evidence_links: list[str]
    completed_eval_record_id: str
    rca_packet_id: str | None
    pattern_id: str | None
    proposed_diff: ProposedDiffManifest
    expected_effect: str
    rollback_plan_ref: ProposalRollbackPlanRef
    blast_radius: ProposalBlastRadiusAssessment
    affected_tests: list[str]
    migration_notes: str
    owner: str
    signer_identity: str
    expiration_ttl: str
    review_ttl: str
    policy_hash: str
    deterministic_digest: str = ""


@dataclass(slots=True)
class ProposalAdmissionReceipt:
    admission_receipt_id: str
    proposal_id: str
    eval_record_present: bool
    rca_or_pattern_present: bool
    target_surface_present: bool
    proposed_diff_present: bool
    blast_radius_present: bool
    rollback_plan_present: bool
    test_plan_present: bool
    owner_signer_present: bool
    freshness_check_status: str
    open_blockers: list[str] = field(default_factory=list)
    decision: str = HOLD_FOR_MORE_EVIDENCE  # ADMIT_TO_GAUNTLET | HOLD | REJECT | REQUIRE_SME_REVIEW
    reason_codes: list[str] = field(default_factory=list)
    deterministic_digest: str = ""


# ---------------------------------------------------------------------------
# 06.7 — Gauntlet / approval / promotion / activation
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class GauntletReceipt:
    gauntlet_receipt_id: str
    proposal_id: str
    proposal_content_hash: str
    replay_case_refs: list[str] = field(default_factory=list)
    regression_pack_refs: list[str] = field(default_factory=list)
    golden_set_refs: list[str] = field(default_factory=list)
    adversarial_case_refs: list[str] = field(default_factory=list)
    compatibility_check_refs: list[str] = field(default_factory=list)
    rollback_rehearsal_ref: str = ""
    sme_signoff_ref: str | None = None
    pass_fail_hold_verdict: str = GAUNTLET_FAIL  # GAUNTLET_PASS | GAUNTLET_FAIL | HOLD_FOR_MORE_EVIDENCE
    failing_cases: list[str] = field(default_factory=list)
    rollout_risk_score: float = 0.0
    replay_proof_ref: str = ""
    divergence_localization: list[str] = field(default_factory=list)
    signer_identity: str = ""
    deterministic_digest: str = ""


@dataclass(slots=True)
class ApprovalDecisionRecord:
    approval_decision_id: str
    proposal_id: str
    gauntlet_receipt_id: str
    completed_eval_record_id: str
    rca_packet_id: str
    eval_freshness_status: str
    calibration_freshness_status: str
    signer_authority_status: str
    rollback_verified: bool
    blast_radius_accepted: bool
    decision: str  # see APPROVAL_DECISIONS
    reason_codes: list[str] = field(default_factory=list)
    deterministic_digest: str = ""


@dataclass(slots=True)
class LedgerProofReference:
    ledger_proof_id: str
    promotion_packet_id: str
    uwg_receipt_id: str
    l4_version_digest: str
    notes: str = ""


@dataclass(slots=True)
class PromotionPacket:
    promotion_packet_id: str
    proposal_id: str
    proposal_type: str
    target_surface: str
    target_version_current: str
    target_version_proposed: str
    proposed_diff: ProposedDiffManifest
    content_hash: str
    signer_identity: str
    owner: str
    policy_hash: str
    eval_record_id: str
    outcome_eval_ref: str
    trajectory_eval_ref: str
    governance_eval_ref: str
    calibration_ref: str
    rca_packet_id: str
    incident_ids: list[str] = field(default_factory=list)
    pattern_ids: list[str] = field(default_factory=list)
    evidence_links: list[str] = field(default_factory=list)
    root_cause_class: str = "UNKNOWN_ROOT_CAUSE"
    first_bad_span: str | None = None
    expected_effect: str = ""
    affected_surfaces: list[str] = field(default_factory=list)
    blast_radius: str = ""
    regression_pack_ids: list[str] = field(default_factory=list)
    golden_set_ids: list[str] = field(default_factory=list)
    gauntlet_receipt: str = ""
    rollout_plan: str = ""
    rollback_plan: str = ""
    activation_policy: str = "NEXT_RUN_START"
    approval_decision_id: str = ""
    uwg_receipt_id: str | None = None
    l4_version_digest: str | None = None
    bus_u_activation_receipt: str | None = None
    deterministic_digest: str = ""


@dataclass(slots=True)
class PromotionUWGRequestPackage:
    package_id: str
    promotion_packet_id: str
    proposal_id: str
    approval_decision_id: str
    gauntlet_receipt_id: str
    content_hash: str
    signer_identity: str
    policy_hash: str
    target_surface: str
    blast_radius: str
    rollback_plan: str
    version_bump: str
    alias_swap_plan: str
    cache_read_surface_refresh_plan: str
    deterministic_digest: str = ""


@dataclass(slots=True)
class FutureRunActivationReceipt:
    activation_receipt_id: str
    promotion_packet_id: str
    uwg_receipt_id: str
    l4_version_digest: str
    target_surface: str
    alias_updated: bool
    activate_at: str = "NEXT_RUN_START"
    canary_scope: str | None = None
    ttl_review_date: str | None = None
    no_current_run_mutation_assertion: bool = True
    no_retroactive_regrade_assertion: bool = True
    bus_u_publish_marker: str = "DEFERRED_UNTIL_RUN_START"
    deterministic_digest: str = ""


# ---------------------------------------------------------------------------
# Public re-export contract list (for static references / pack acceptance)
# ---------------------------------------------------------------------------

__all__ = [
    # 06.1
    "ExhaustSourceManifest",
    "StageMap",
    "ArtifactInventory",
    "ExhaustGapReport",
    "RuntimeExhaustBundle",
    "NormalizedEvidenceRecord",
    # 06.2
    "L6DeniedWriteAttemptRecord",
    "SurfaceIsolationManifest",
    "StageBarrierReceipt",
    "ObserverComplianceReceipt",
    "MissingEvidenceMap",
    "NonEvaluablePacketRecord",
    "EvalReadinessReceipt",
    # 06.3
    "EvalDimensionScore",
    "OutcomeEvalRecord",
    "TrajectoryEvalRecord",
    "GovernanceRegressionRecord",
    # 06.4
    "CalibrationRecord",
    "JudgeReliabilitySignal",
    "HumanAgreementRecord",
    "RubricCalibrationReceipt",
    "CompletedEvalRecord",
    "EvalRecordSealReceipt",
    # 06.5
    "FusedSignalBundle",
    "FailureChain",
    "FirstBadSpanLocalization",
    "RCAPacket",
    "DriftClusterMap",
    "AffectedSurfaceCandidateMap",
    "PatternSynthesisRecord",
    # 06.6
    "ProposedDiffManifest",
    "ProposalEvidenceMap",
    "ProposalBlastRadiusAssessment",
    "ProposalRollbackPlanRef",
    "ProposalTestPlan",
    "DraftProposalPacket",
    "ProposalAdmissionReceipt",
    # 06.7
    "GauntletReceipt",
    "ApprovalDecisionRecord",
    "LedgerProofReference",
    "PromotionPacket",
    "PromotionUWGRequestPackage",
    "FutureRunActivationReceipt",
    # Vocabulary
    "READY_FOR_EVAL",
    "PARTIAL_BUT_SCORABLE",
    "HOLD_FOR_MISSING_EVIDENCE",
    "NON_EVALUABLE_PACKET",
    "EVAL_SEALED",
    "SIGNAL_FUSED",
    "RCA_COMPLETE",
    "PATTERN_CONFIRMED",
    "PROPOSAL_DRAFTED",
    "ADMIT_TO_GAUNTLET",
    "HOLD_FOR_MORE_EVIDENCE",
    "REJECT_WEAK_PROPOSAL",
    "REQUIRE_SME_REVIEW",
    "GAUNTLET_PASS",
    "GAUNTLET_FAIL",
    "APPROVED_FOR_UWG_REQUEST",
    "REJECTED_FOR_PROMOTION",
    "FUTURE_RUN_ACTIVATION_READY",
    "RUN_OUTCOME_CLASSES",
    "ROOT_CAUSE_CLASSES",
    "PROPOSAL_TYPES",
    "APPROVAL_DECISIONS",
    "ALLOWED_DOWNSTREAM_USE",
    "EVAL_DIMENSION_RESULTS",
    "GRADER_TYPES",
]
