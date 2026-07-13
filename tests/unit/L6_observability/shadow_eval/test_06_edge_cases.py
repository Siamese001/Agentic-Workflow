"""Exhaustive edge-case coverage for L6 shadow_eval doctrine.

Each parametrized test exercises every enumerated value or every boundary
condition declared in the v6 doctrine. The test pack is structured to fail
loudly if a doctrine enum gains/loses a value, or if a boundary moves.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timedelta, timezone

import pytest

from agentic_core.L6_observability.shadow_eval import (
    ALLOWED_DOWNSTREAM_USE,
    APPROVAL_DECISIONS,
    EVAL_DIMENSION_RESULTS,
    GRADER_TYPES,
    KPI_BOARD,
    PROPOSAL_TYPES,
    ROOT_CAUSE_CLASSES,
    RUN_OUTCOME_CLASSES,
    SPAN_NAMES,
    GovernanceBaseline,
    GauntletReceipt,
    L6PipelineState,
    L6SpanRecord,
    L6SpanRecorder,
    ObserverViolation,
    bind_uwg_receipt,
    build_calibration_record,
    build_completed_eval_record,
    build_observer_compliance_receipt,
    build_promotion_packet,
    build_runtime_exhaust_bundle,
    build_surface_isolation_manifest,
    build_uwg_request_package,
    decide_approval,
    deny_if_forbidden,
    evaluate_governance_regression,
    evaluate_kpi,
    evaluate_outcome,
    evaluate_readiness,
    evaluate_trajectory,
    proposal_content_hash,
    run_6a,
    run_6b,
    run_6c,
    run_observer,
    run_proposal,
    stage_barrier_check,
    stratify_outcome,
)
from agentic_core.L6_observability.shadow_eval.observer import (
    FORBIDDEN_WRITE_SURFACES,
)
from agentic_core.L6_observability.shadow_eval.otel_spans import (
    FAILURE_CONTAINMENT,
)


# ---------------------------------------------------------------------------
# Vocabulary cardinality and stability — one test per doctrine enum
# ---------------------------------------------------------------------------


def test_run_outcome_classes_doctrine_cardinality():
    """06.1 §I7 declares 13 outcome classes."""
    assert len(RUN_OUTCOME_CLASSES) == 13


def test_root_cause_classes_doctrine_cardinality():
    """06.5 declares 16 root-cause classes."""
    assert len(ROOT_CAUSE_CLASSES) == 16


def test_proposal_types_doctrine_cardinality():
    """06.6 declares 10 proposal types."""
    assert len(PROPOSAL_TYPES) == 10


def test_approval_decisions_doctrine_cardinality():
    """06.7 declares 7 approval decisions."""
    assert len(APPROVAL_DECISIONS) == 7
    for required in (
        "APPROVE",
        "REJECT",
        "HOLD_FOR_MORE_EVIDENCE",
        "REQUIRE_SME_REVIEW",
        "REQUIRE_ROLLBACK_PLAN",
        "REQUIRE_NARROWER_SCOPE",
        "REQUIRE_ADR_EXCEPTION",
    ):
        assert required in APPROVAL_DECISIONS


def test_allowed_downstream_use_doctrine_cardinality():
    """06.4 declares 4 downstream use scopes."""
    assert ALLOWED_DOWNSTREAM_USE == frozenset(
        {"RCA_ONLY", "RCA_AND_PROPOSAL", "HOLD_ONLY", "NON_EVALUABLE"}
    )


def test_eval_dimension_results_doctrine_cardinality():
    """06.3 declares 5 dimension results (PASS/FAIL/WARN/UNKNOWN/NOT_APPLICABLE)."""
    assert EVAL_DIMENSION_RESULTS == frozenset(
        {"PASS", "FAIL", "WARN", "UNKNOWN", "NOT_APPLICABLE"}
    )


def test_grader_types_doctrine_cardinality():
    """06.3 declares 4 grader types."""
    assert GRADER_TYPES == frozenset(
        {"code", "llm_judge", "hybrid", "human_calibrated_reference"}
    )


def test_span_registry_doctrine_cardinality():
    """06.8 canonical span surface includes the five calibration spans."""
    assert len(SPAN_NAMES) == 37
    assert len(set(SPAN_NAMES)) == 37  # uniqueness


def test_kpi_board_cardinality():
    """06.8 KPI board has 19 KPIs."""
    assert len(KPI_BOARD) == 19


def test_failure_containment_matrix_completeness():
    """06.8 declares 15 failure containment entries."""
    assert len(FAILURE_CONTAINMENT) == 15


# ---------------------------------------------------------------------------
# Outcome stratification — every class round-trips cleanly
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", sorted(RUN_OUTCOME_CLASSES))
def test_stratify_outcome_each_class_roundtrips(cls):
    raw = {"outcome_class": cls}
    assert stratify_outcome(raw) == cls


@pytest.mark.parametrize(
    "garbage",
    ["", "made_up_class", "NORMAL_SUCCESS", " normal_success ", "null"],
)
def test_stratify_outcome_unknown_collapses_to_unresolved(garbage):
    """Unknown outcome strings must not be silently accepted."""
    raw = {"outcome_class": garbage}
    assert stratify_outcome(raw) == "unresolved_unknown"


# ---------------------------------------------------------------------------
# Proposal types — each value accepted by draft_proposal
# ---------------------------------------------------------------------------


def _proposal_kit(sealed_completed_run, *, target_surface: str = "prompt"):
    """Run 6A→6B→6C and return state + kwargs needed for run_proposal."""
    state = L6PipelineState()
    run_6a(state, sealed_completed_run)
    readiness = run_observer(state)
    baseline = GovernanceBaseline(
        policy_hash="DIFF-POL", rubric_hash="rh",
        replay_digest=state.ingest.bundle.replay_key,
    )
    run_6b(state, readiness, governance_baseline=baseline)
    run_6c(state)
    return state


@pytest.mark.parametrize("proposal_type", sorted(PROPOSAL_TYPES))
def test_every_proposal_type_is_acceptable(sealed_completed_run, proposal_type):
    state = _proposal_kit(sealed_completed_run)
    res = run_proposal(
        state,
        proposal_type=proposal_type,
        target_surface="prompt",
        current_version_ref="v1",
        proposed_version_ref="v2",
        problem_statement="problem",
        expected_effect="effect",
        rollback_steps=["step"],
        affected_surfaces=["prompt"],
        affected_tests=["t"],
        owner="alice",
        signer_identity="alice",
        policy_hash="policy-hash-A",
    )
    assert res.proposal.proposal_type == proposal_type


# ---------------------------------------------------------------------------
# Admission decisions — every value reachable
# ---------------------------------------------------------------------------


def test_admission_admit_path(sealed_completed_run):
    state = _proposal_kit(sealed_completed_run)
    res = run_proposal(
        state, proposal_type="LOCAL_PATCH", target_surface="prompt",
        current_version_ref="v1", proposed_version_ref="v2",
        problem_statement="x", expected_effect="y",
        rollback_steps=["s"], affected_surfaces=["prompt"],
        affected_tests=["t"], owner="o", signer_identity="o",
        policy_hash="policy-hash-A",
    )
    assert res.admission.decision == "ADMIT_TO_GAUNTLET"


def test_admission_require_sme_high_impact_type(sealed_completed_run):
    state = _proposal_kit(sealed_completed_run)
    res = run_proposal(
        state, proposal_type="POLICY_CLARIFICATION", target_surface="policy",
        current_version_ref="v1", proposed_version_ref="v2",
        problem_statement="x", expected_effect="y",
        rollback_steps=["s"], affected_surfaces=["policy"],
        affected_tests=["t"], owner="o", signer_identity="o",
        policy_hash="policy-hash-A",
    )
    assert res.admission.decision == "REQUIRE_SME_REVIEW"


def test_admission_require_sme_high_rollout_risk(sealed_completed_run):
    state = _proposal_kit(sealed_completed_run)
    res = run_proposal(
        state, proposal_type="LOCAL_PATCH", target_surface="prompt",
        current_version_ref="v1", proposed_version_ref="v2",
        problem_statement="x", expected_effect="y",
        rollback_steps=["s"], affected_surfaces=["prompt"],
        affected_tests=["t"], owner="o", signer_identity="o",
        policy_hash="policy-hash-A", rollout_risk_score=0.7,
    )
    assert res.admission.decision == "REQUIRE_SME_REVIEW"


def test_admission_rollout_risk_just_below_threshold_admits(sealed_completed_run):
    """Boundary: rollout_risk_score=0.69 must NOT trigger REQUIRE_SME_REVIEW."""
    state = _proposal_kit(sealed_completed_run)
    res = run_proposal(
        state, proposal_type="LOCAL_PATCH", target_surface="prompt",
        current_version_ref="v1", proposed_version_ref="v2",
        problem_statement="x", expected_effect="y",
        rollback_steps=["s"], affected_surfaces=["prompt"],
        affected_tests=["t"], owner="o", signer_identity="o",
        policy_hash="policy-hash-A", rollout_risk_score=0.69,
    )
    assert res.admission.decision == "ADMIT_TO_GAUNTLET"


# ---------------------------------------------------------------------------
# Approval decisions — all 7 reachable, including REQUIRE_ADR_EXCEPTION
# ---------------------------------------------------------------------------


def _approval_kit(sealed_completed_run):
    """Run all stages up through gauntlet; return parts needed for decide_approval."""
    from agentic_core.L6_observability.shadow_eval import run_gauntlet

    state = _proposal_kit(sealed_completed_run)
    res = run_proposal(
        state, proposal_type="LOCAL_PATCH", target_surface="prompt",
        current_version_ref="v1", proposed_version_ref="v2",
        problem_statement="x", expected_effect="y",
        rollback_steps=["s"], affected_surfaces=["prompt"],
        affected_tests=["t"], owner="o", signer_identity="o",
        policy_hash="policy-hash-A",
    )
    gauntlet = run_gauntlet(res.proposal, rollback_rehearsal_ref="rehearse-1")
    return state, res, gauntlet


def _approve_kwargs(state, res, gauntlet):
    return dict(
        admission=res.admission,
        gauntlet=gauntlet,
        completed_eval_record=state.eval.completed,
        rca_packet=state.rca.rca,
        eval_freshness_ok=True,
        calibration_freshness_ok=True,
        signer_authority_ok=True,
        rollback_verified=True,
        blast_radius_accepted=True,
    )


def test_approval_approve_clean_path(sealed_completed_run):
    state, res, gauntlet = _approval_kit(sealed_completed_run)
    decision = decide_approval(res.proposal, **_approve_kwargs(state, res, gauntlet))
    assert decision.decision == "APPROVE"
    assert decision.reason_codes == []


def test_approval_reject_when_gauntlet_fails(sealed_completed_run):
    state, res, gauntlet = _approval_kit(sealed_completed_run)
    failed = dataclasses.replace(gauntlet, pass_fail_hold_verdict="GAUNTLET_FAIL")
    decision = decide_approval(res.proposal, **{**_approve_kwargs(state, res, gauntlet), "gauntlet": failed})
    assert decision.decision == "REJECT"
    assert "GAUNTLET_FAIL" in decision.reason_codes


def test_approval_hold_when_eval_stale(sealed_completed_run):
    state, res, gauntlet = _approval_kit(sealed_completed_run)
    decision = decide_approval(res.proposal, **{**_approve_kwargs(state, res, gauntlet), "eval_freshness_ok": False})
    assert decision.decision == "HOLD_FOR_MORE_EVIDENCE"
    assert "STALE_EVAL" in decision.reason_codes


def test_approval_hold_when_calibration_stale(sealed_completed_run):
    state, res, gauntlet = _approval_kit(sealed_completed_run)
    decision = decide_approval(res.proposal, **{**_approve_kwargs(state, res, gauntlet), "calibration_freshness_ok": False})
    assert decision.decision == "HOLD_FOR_MORE_EVIDENCE"
    assert "STALE_CALIBRATION" in decision.reason_codes


def test_approval_require_sme_when_signer_invalid(sealed_completed_run):
    state, res, gauntlet = _approval_kit(sealed_completed_run)
    decision = decide_approval(res.proposal, **{**_approve_kwargs(state, res, gauntlet), "signer_authority_ok": False})
    assert decision.decision == "REQUIRE_SME_REVIEW"
    assert "INSUFFICIENT_SIGNER_AUTHORITY" in decision.reason_codes


def test_approval_require_rollback_when_unverified(sealed_completed_run):
    state, res, gauntlet = _approval_kit(sealed_completed_run)
    decision = decide_approval(res.proposal, **{**_approve_kwargs(state, res, gauntlet), "rollback_verified": False})
    assert decision.decision == "REQUIRE_ROLLBACK_PLAN"
    assert "ROLLBACK_NOT_VERIFIED" in decision.reason_codes


def test_approval_require_narrower_scope_when_blast_rejected(sealed_completed_run):
    state, res, gauntlet = _approval_kit(sealed_completed_run)
    decision = decide_approval(res.proposal, **{**_approve_kwargs(state, res, gauntlet), "blast_radius_accepted": False})
    assert decision.decision == "REQUIRE_NARROWER_SCOPE"
    assert "BLAST_RADIUS_NOT_ACCEPTED" in decision.reason_codes


def test_approval_require_adr_exception_when_missing(sealed_completed_run):
    """REQUIRE_ADR_EXCEPTION fires when proposal asks for ADR but ref is missing."""
    state, res, gauntlet = _approval_kit(sealed_completed_run)
    decision = decide_approval(
        res.proposal,
        **_approve_kwargs(state, res, gauntlet),
        adr_required=True,
        adr_ref=None,
    )
    assert decision.decision == "REQUIRE_ADR_EXCEPTION"
    assert "ADR_EXCEPTION_REQUIRED" in decision.reason_codes


def test_approval_adr_required_with_ref_still_approves(sealed_completed_run):
    """When ADR ref is supplied, REQUIRE_ADR_EXCEPTION must NOT fire."""
    state, res, gauntlet = _approval_kit(sealed_completed_run)
    decision = decide_approval(
        res.proposal,
        **_approve_kwargs(state, res, gauntlet),
        adr_required=True,
        adr_ref="ADR-042",
    )
    assert decision.decision == "APPROVE"


def test_approval_priority_reject_beats_hold(sealed_completed_run):
    """Doctrine 06.7: REJECT terminal beats HOLD when both fire."""
    state, res, gauntlet = _approval_kit(sealed_completed_run)
    failed = dataclasses.replace(gauntlet, pass_fail_hold_verdict="GAUNTLET_FAIL")
    decision = decide_approval(
        res.proposal,
        **{
            **_approve_kwargs(state, res, gauntlet),
            "gauntlet": failed,
            "eval_freshness_ok": False,  # would trigger HOLD
        },
    )
    assert decision.decision == "REJECT"
    assert {"GAUNTLET_FAIL", "STALE_EVAL"}.issubset(set(decision.reason_codes))


def test_approval_priority_hold_beats_require_sme(sealed_completed_run):
    """Doctrine 06.7: HOLD blocks until evidence; beats actionable REQUIRE_*."""
    state, res, gauntlet = _approval_kit(sealed_completed_run)
    decision = decide_approval(
        res.proposal,
        **{
            **_approve_kwargs(state, res, gauntlet),
            "eval_freshness_ok": False,  # HOLD
            "signer_authority_ok": False,  # REQUIRE_SME
        },
    )
    assert decision.decision == "HOLD_FOR_MORE_EVIDENCE"


def test_approval_content_hash_mismatch_forces_reject(sealed_completed_run):
    state, res, gauntlet = _approval_kit(sealed_completed_run)
    tampered = dataclasses.replace(res.proposal, current_version_ref="v1-DIFFERENT")
    decision = decide_approval(tampered, **{**_approve_kwargs(state, res, gauntlet)})
    assert decision.decision == "REJECT"
    assert "CONTENT_HASH_MISMATCH" in decision.reason_codes


# ---------------------------------------------------------------------------
# Forbidden write surfaces — every entry triggers ObserverViolation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("surface", sorted(FORBIDDEN_WRITE_SURFACES))
def test_every_forbidden_surface_raises(surface):
    with pytest.raises(ObserverViolation):
        deny_if_forbidden(surface)


def test_observer_violation_is_l6_observer_fail():
    """Doctrine 06.2: violation response is the L6_OBSERVER_FAIL classification."""
    try:
        deny_if_forbidden("L4")
    except ObserverViolation as exc:
        assert "L4" in str(exc)


# ---------------------------------------------------------------------------
# Calibration TTL boundary — exact-day boundary behavior
# ---------------------------------------------------------------------------


def _ts_days_ago(d: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=d)).isoformat()


def test_calibration_fresh_at_one_day():
    rec = build_calibration_record(
        rubric_hash="r", rubric_version="1", grader_version="g",
        calibration_freshness_timestamp=_ts_days_ago(1), ttl_days=7,
        calibration_source_refs=("test:calibration-source",),
        calibration_result_ref="test:calibration-result",
        dataset_id="test-dataset", dataset_version="v1",
        sample_size=1, minimum_sample_size=1,
        label_source="deterministic_code_reference", result_valid=True,
    )
    assert rec.calibration_status == "CURRENT"


def test_calibration_fresh_just_under_ttl():
    """Boundary: 6 days < 7-day TTL — still CURRENT."""
    rec = build_calibration_record(
        rubric_hash="r", rubric_version="1", grader_version="g",
        calibration_freshness_timestamp=_ts_days_ago(6), ttl_days=7,
        calibration_source_refs=("test:calibration-source",),
        calibration_result_ref="test:calibration-result",
        dataset_id="test-dataset", dataset_version="v1",
        sample_size=1, minimum_sample_size=1,
        label_source="deterministic_code_reference", result_valid=True,
    )
    assert rec.calibration_status == "CURRENT"


def test_calibration_stale_just_over_ttl():
    """Boundary: 8 days > 7-day TTL — STALE."""
    rec = build_calibration_record(
        rubric_hash="r", rubric_version="1", grader_version="g",
        calibration_freshness_timestamp=_ts_days_ago(8), ttl_days=7,
        calibration_source_refs=("test:calibration-source",),
        calibration_result_ref="test:calibration-result",
        dataset_id="test-dataset", dataset_version="v1",
        sample_size=1, minimum_sample_size=1,
        label_source="deterministic_code_reference", result_valid=True,
    )
    assert rec.calibration_status == "STALE"


# ---------------------------------------------------------------------------
# KPI evaluation — every direction at boundary
# ---------------------------------------------------------------------------


def _kpi(name):
    for k in KPI_BOARD:
        if k.name == name:
            return k
    raise AssertionError(f"unknown kpi: {name}")


def test_kpi_lte_at_target():
    """KPI direction <= : observed equal to target must pass."""
    k = _kpi("trace_ingest_freshness_minutes")
    assert k.direction == "<="
    assert evaluate_kpi(k.name, k.target) is True
    assert evaluate_kpi(k.name, k.target + 0.01) is False


def test_kpi_gte_at_target():
    """KPI direction >= : observed equal to target must pass."""
    k = _kpi("evidence_field_completeness_pct")
    assert k.direction == ">="
    assert evaluate_kpi(k.name, k.target) is True
    assert evaluate_kpi(k.name, k.target - 0.01) is False


def test_kpi_eq_at_target():
    """KPI direction == : observed must match target exactly."""
    k = _kpi("observer_law_violation_count")
    assert k.direction == "=="
    assert evaluate_kpi(k.name, k.target) is True
    assert evaluate_kpi(k.name, k.target + 1) is False


def test_kpi_unknown_name_raises():
    with pytest.raises(KeyError):
        evaluate_kpi("not-a-real-kpi", 0.0)


@pytest.mark.parametrize("kpi", [k.name for k in KPI_BOARD])
def test_every_kpi_evaluates(kpi):
    """Smoke: every KPI must return a bool when evaluated at its target."""
    target = _kpi(kpi).target
    result = evaluate_kpi(kpi, target)
    assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# Span recorder — negative paths
# ---------------------------------------------------------------------------


def _span(name, idx=0):
    return L6SpanRecord(name=name, trace_id=f"t{idx}", span_id=f"s{idx}")


def test_recorder_rejects_unknown_span_name():
    rec = L6SpanRecorder()
    with pytest.raises(ValueError):
        rec.record(_span("not.a.real.span"))


def test_recorder_assert_pipeline_order_rejects_inversion():
    rec = L6SpanRecorder()
    rec.record(_span("l6.eval_record.seal", 1))
    rec.record(_span("l6.ingest.bundle_receive", 2))
    with pytest.raises(AssertionError):
        rec.assert_pipeline_order()


def test_recorder_no_runtime_feedback_edge_passes_for_l6_only():
    rec = L6SpanRecorder()
    rec.record(_span("l6.ingest.bundle_receive"))
    rec.assert_no_runtime_feedback_edge()


# ---------------------------------------------------------------------------
# Stage barrier and observer compliance — explicit FAIL/PASS coverage
# ---------------------------------------------------------------------------


def test_stage_barrier_fails_when_run_not_closed(sealed_completed_run):
    raw = dict(sealed_completed_run)
    raw["runtime_boundary_crossed"] = False
    # ingest will reject earlier, but barrier is a pure check on the bundle
    # Emulate by building a bundle and patching field via dataclasses.replace.
    bundle, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    open_bundle = dataclasses.replace(bundle, runtime_boundary_crossed=False)
    barrier = stage_barrier_check(open_bundle)
    assert barrier.barrier_status == "FAIL"


def test_observer_compliance_fail_when_isolation_violation(sealed_completed_run):
    from agentic_core.L6_observability.shadow_eval import L6DeniedWriteAttemptRecord
    bundle, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    denied = L6DeniedWriteAttemptRecord(
        denied_write_id="dw-1",
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        target_surface="L4",
        operation="write",
        reason_code="FORBIDDEN_SURFACE",
        timestamp="2026-01-01T00:00:00Z",
    )
    iso = build_surface_isolation_manifest(
        bundle,
        read_surfaces_touched=("traces",),
        write_surfaces_requested=("L4",),
        denied_write_attempts=(denied,),
    )
    obs = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=iso)
    assert obs.violation_response == "L6_OBSERVER_FAIL"
    assert iso.isolation_status == "VIOLATION"


# ---------------------------------------------------------------------------
# Readiness decisions — all 4 explicitly triggered
# ---------------------------------------------------------------------------


def test_readiness_ready_for_clean_run(sealed_completed_run):
    bundle, normalized, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    iso = build_surface_isolation_manifest(bundle, read_surfaces_touched=("t",))
    obs = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=iso)
    receipt, _m, _n = evaluate_readiness(bundle, obs, normalized)
    assert receipt.readiness_decision == "READY_FOR_6B"


def test_readiness_hold_when_replay_key_missing(run_missing_replay_key):
    bundle, normalized, *_ = build_runtime_exhaust_bundle(run_missing_replay_key)
    barrier = stage_barrier_check(bundle)
    iso = build_surface_isolation_manifest(bundle, read_surfaces_touched=("t",))
    obs = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=iso)
    receipt, missing, _n = evaluate_readiness(bundle, obs, normalized)
    assert receipt.readiness_decision == "HOLD_FOR_MISSING_EVIDENCE"
    assert "replay_key" in missing.missing_field_refs


def test_readiness_non_evaluable_when_observer_violation(sealed_completed_run):
    from agentic_core.L6_observability.shadow_eval import L6DeniedWriteAttemptRecord
    bundle, normalized, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    denied = L6DeniedWriteAttemptRecord(
        denied_write_id="dw-1",
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        target_surface="L4",
        operation="write",
        reason_code="FORBIDDEN_SURFACE",
        timestamp="2026-01-01T00:00:00Z",
    )
    iso = build_surface_isolation_manifest(
        bundle,
        read_surfaces_touched=("traces",),
        write_surfaces_requested=("L4",),
        denied_write_attempts=(denied,),
    )
    obs = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=iso)
    receipt, _m, non_eval = evaluate_readiness(bundle, obs, normalized)
    assert receipt.readiness_decision == "NON_EVALUABLE_PACKET"
    assert non_eval is not None


# ---------------------------------------------------------------------------
# Governance — every drift category exercised
# ---------------------------------------------------------------------------


def test_governance_clean_baseline_yields_no_drift(sealed_completed_run):
    bundle, normalized, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    iso = build_surface_isolation_manifest(bundle, read_surfaces_touched=("t",))
    obs = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=iso)
    receipt, _m, _n = evaluate_readiness(bundle, obs, normalized)
    base = GovernanceBaseline(
        policy_hash=bundle.policy_hash, rubric_hash="rh", replay_digest=bundle.replay_key,
    )
    gov = evaluate_governance_regression(receipt, normalized, base)
    assert gov.severity == "low"
    assert not gov.policy_drift_flags
    assert not gov.replay_digest_drift_flags


def test_governance_policy_only_drift(sealed_completed_run):
    bundle, normalized, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    iso = build_surface_isolation_manifest(bundle, read_surfaces_touched=("t",))
    obs = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=iso)
    receipt, _m, _n = evaluate_readiness(bundle, obs, normalized)
    base = GovernanceBaseline(
        policy_hash="DIFFERENT", rubric_hash="rh", replay_digest=bundle.replay_key,
    )
    gov = evaluate_governance_regression(receipt, normalized, base)
    assert gov.policy_drift_flags
    assert not gov.replay_digest_drift_flags


def test_governance_replay_only_drift(sealed_completed_run):
    bundle, normalized, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    iso = build_surface_isolation_manifest(bundle, read_surfaces_touched=("t",))
    obs = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=iso)
    receipt, _m, _n = evaluate_readiness(bundle, obs, normalized)
    base = GovernanceBaseline(
        policy_hash=bundle.policy_hash, rubric_hash="rh", replay_digest="DIFFERENT",
    )
    gov = evaluate_governance_regression(receipt, normalized, base)
    assert not gov.policy_drift_flags
    assert gov.replay_digest_drift_flags


def test_governance_both_drifts_high_severity(sealed_completed_run):
    bundle, normalized, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    iso = build_surface_isolation_manifest(bundle, read_surfaces_touched=("t",))
    obs = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=iso)
    receipt, _m, _n = evaluate_readiness(bundle, obs, normalized)
    base = GovernanceBaseline(
        policy_hash="X", rubric_hash="rh", replay_digest="Y",
    )
    gov = evaluate_governance_regression(receipt, normalized, base)
    assert gov.severity == "high"
    assert gov.policy_drift_flags
    assert gov.replay_digest_drift_flags


# ---------------------------------------------------------------------------
# Promotion content-hash binding — exhaustive
# ---------------------------------------------------------------------------


def test_proposal_content_hash_stable_for_same_content(sealed_completed_run):
    state = _proposal_kit(sealed_completed_run)
    a = run_proposal(
        state, proposal_type="LOCAL_PATCH", target_surface="prompt",
        current_version_ref="v1", proposed_version_ref="v2",
        problem_statement="x", expected_effect="y",
        rollback_steps=["s"], affected_surfaces=["prompt"],
        affected_tests=["t"], owner="o", signer_identity="o",
        policy_hash="policy-hash-A",
    )
    h1 = proposal_content_hash(a.proposal)
    h2 = proposal_content_hash(a.proposal)
    assert h1 == h2 and len(h1) == 64


@pytest.mark.parametrize(
    "field,value",
    [
        ("current_version_ref", "v1-CHANGED"),
        ("proposed_version_ref", "v3"),
        ("target_surface", "policy"),
        ("policy_hash", "policy-hash-B"),
        ("proposal_type", "THRESHOLD_CHANGE"),
    ],
)
def test_proposal_content_hash_changes_when_canonical_field_changes(
    sealed_completed_run, field, value
):
    state = _proposal_kit(sealed_completed_run)
    a = run_proposal(
        state, proposal_type="LOCAL_PATCH", target_surface="prompt",
        current_version_ref="v1", proposed_version_ref="v2",
        problem_statement="x", expected_effect="y",
        rollback_steps=["s"], affected_surfaces=["prompt"],
        affected_tests=["t"], owner="o", signer_identity="o",
        policy_hash="policy-hash-A",
    )
    tampered = dataclasses.replace(a.proposal, **{field: value})
    assert proposal_content_hash(tampered) != proposal_content_hash(a.proposal)


# ---------------------------------------------------------------------------
# Failure containment matrix — every entry has the required shape
# ---------------------------------------------------------------------------


def test_failure_containment_entries_have_required_fields():
    """FAILURE_CONTAINMENT is dict[failure_mode -> containment_action] per 06.8."""
    for failure_mode, containment_action in FAILURE_CONTAINMENT.items():
        assert failure_mode
        assert containment_action


def test_failure_containment_modes_are_unique():
    """Dict keys are unique by definition; assert all 15 modes are covered."""
    assert len(FAILURE_CONTAINMENT) == 15


@pytest.mark.parametrize(
    "required_mode",
    [
        "stale_ingest", "orphan_evidence", "eval_gap", "forced_certainty",
        "preference_overfitting", "rca_vagueness", "false_promote",
        "shadow_writer", "stale_eval_on_write", "partial_bypass",
        "current_run_mutation", "rollback_missing", "cache_contamination",
        "rubric_drift", "replay_nonlocalization",
    ],
)
def test_every_doctrine_failure_mode_is_mapped(required_mode):
    """Doctrine 06.8 lists 15 failure modes — every one must map to an action."""
    assert required_mode in FAILURE_CONTAINMENT
    assert FAILURE_CONTAINMENT[required_mode]


# ---------------------------------------------------------------------------
# Activation receipt — invariants asserted explicitly
# ---------------------------------------------------------------------------


def _full_pipeline_to_promotion(sealed_completed_run):
    from agentic_core.L6_observability.shadow_eval import run_gauntlet
    from agentic_core.L6_observability.shadow_eval.gauntlet import (
        build_future_run_activation_receipt,
    )
    state = _proposal_kit(sealed_completed_run)
    res = run_proposal(
        state, proposal_type="LOCAL_PATCH", target_surface="prompt",
        current_version_ref="v1", proposed_version_ref="v2",
        problem_statement="x", expected_effect="y",
        rollback_steps=["s"], affected_surfaces=["prompt"],
        affected_tests=["t"], owner="o", signer_identity="o",
        policy_hash="policy-hash-A",
    )
    gauntlet = run_gauntlet(res.proposal, rollback_rehearsal_ref="rehearse-1")
    decision = decide_approval(res.proposal, **_approve_kwargs(state, res, gauntlet))
    promo = build_promotion_packet(
        res.proposal, approval=decision, completed_eval_record=state.eval.completed,
        rca_packet=state.rca.rca, gauntlet=gauntlet,
        target_version_current="v1", target_version_proposed="v2",
    )
    _pkg = build_uwg_request_package(
        promo,
        version_bump="minor",
        alias_swap_plan="swap p1 -> p2",
        cache_read_surface_refresh_plan="flush prompt cache",
    )
    bound, _proof = bind_uwg_receipt(
        promo, uwg_receipt_id="uwg-99", l4_version_digest="l4d",
    )
    activation = build_future_run_activation_receipt(bound, alias_updated=True)
    return activation


def test_activation_invariants_hold(sealed_completed_run):
    a = _full_pipeline_to_promotion(sealed_completed_run)
    assert a.activate_at == "NEXT_RUN_START"
    assert a.bus_u_publish_marker == "DEFERRED_UNTIL_RUN_START"
    assert a.no_current_run_mutation_assertion is True
    assert a.no_retroactive_regrade_assertion is True
    assert a.uwg_receipt_id == "uwg-99"


def test_activation_rejects_when_uwg_receipt_missing(sealed_completed_run):
    """Doctrine 06.7: activation MUST NOT publish without UWG receipt."""
    from agentic_core.L6_observability.shadow_eval import run_gauntlet
    from agentic_core.L6_observability.shadow_eval.gauntlet import (
        GauntletError,
        build_future_run_activation_receipt,
    )
    state = _proposal_kit(sealed_completed_run)
    res = run_proposal(
        state, proposal_type="LOCAL_PATCH", target_surface="prompt",
        current_version_ref="v1", proposed_version_ref="v2",
        problem_statement="x", expected_effect="y",
        rollback_steps=["s"], affected_surfaces=["prompt"],
        affected_tests=["t"], owner="o", signer_identity="o",
        policy_hash="policy-hash-A",
    )
    gauntlet = run_gauntlet(res.proposal, rollback_rehearsal_ref="r")
    decision = decide_approval(res.proposal, **_approve_kwargs(state, res, gauntlet))
    promo = build_promotion_packet(
        res.proposal, approval=decision, completed_eval_record=state.eval.completed,
        rca_packet=state.rca.rca, gauntlet=gauntlet,
        target_version_current="v1", target_version_proposed="v2",
    )
    # promo has no uwg_receipt_id bound yet — activation must raise.
    with pytest.raises(GauntletError):
        build_future_run_activation_receipt(promo, alias_updated=True)


# ---------------------------------------------------------------------------
# Promotion packet — guards against APPROVE-bypass
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_decision",
    ["REJECT", "HOLD_FOR_MORE_EVIDENCE", "REQUIRE_SME_REVIEW",
     "REQUIRE_ROLLBACK_PLAN", "REQUIRE_NARROWER_SCOPE", "REQUIRE_ADR_EXCEPTION"],
)
def test_promotion_packet_rejects_non_approve(sealed_completed_run, bad_decision):
    """Doctrine 06.7: only APPROVE may produce a PromotionPacket."""
    from agentic_core.L6_observability.shadow_eval import run_gauntlet
    from agentic_core.L6_observability.shadow_eval.gauntlet import GauntletError

    state = _proposal_kit(sealed_completed_run)
    res = run_proposal(
        state, proposal_type="LOCAL_PATCH", target_surface="prompt",
        current_version_ref="v1", proposed_version_ref="v2",
        problem_statement="x", expected_effect="y",
        rollback_steps=["s"], affected_surfaces=["prompt"],
        affected_tests=["t"], owner="o", signer_identity="o",
        policy_hash="policy-hash-A",
    )
    gauntlet = run_gauntlet(res.proposal, rollback_rehearsal_ref="r")
    decision = decide_approval(res.proposal, **_approve_kwargs(state, res, gauntlet))
    bad = dataclasses.replace(decision, decision=bad_decision)
    with pytest.raises(GauntletError):
        build_promotion_packet(
            res.proposal, approval=bad, completed_eval_record=state.eval.completed,
            rca_packet=state.rca.rca, gauntlet=gauntlet,
            target_version_current="v1", target_version_proposed="v2",
        )
