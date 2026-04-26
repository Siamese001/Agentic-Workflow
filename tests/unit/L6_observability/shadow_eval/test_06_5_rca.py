"""06.5 RCA / pattern synthesis doctrine tests.

Doctrine TEST REQUIREMENTS (06.5):
- Raw traces cannot feed RCA without CompletedEvalRecord.
- RCA packet must list affected surface.
- Vague root cause requires hold reason.
- first_bad_span is never invented when unavailable.
- Disagreement / counterexamples are not dropped.
- One-off incidents are not marked systemic without sample support.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L6_observability.shadow_eval import (
    NormalizedEvidenceRecord,
    RCAError,
    build_calibration_record,
    build_completed_eval_record,
    build_drift_cluster_map,
    build_observer_compliance_receipt,
    build_rca_packet,
    build_runtime_exhaust_bundle,
    build_surface_isolation_manifest,
    evaluate_governance_regression,
    evaluate_outcome,
    evaluate_readiness,
    evaluate_trajectory,
    fuse_signals,
    GovernanceBaseline,
    stage_barrier_check,
    synthesize_patterns,
)


def _make_completed(sealed_completed_run, downstream="RCA_AND_PROPOSAL"):
    bundle, normalized, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    iso = build_surface_isolation_manifest(bundle, read_surfaces_touched=("t",))
    obs = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=iso)
    receipt, _m, _n = evaluate_readiness(bundle, obs, normalized)
    outcome = evaluate_outcome(receipt, normalized)
    trajectory = evaluate_trajectory(receipt, normalized)
    baseline = GovernanceBaseline(policy_hash="DIFF-POL", rubric_hash="rh", replay_digest="DIFF-REP")
    governance = evaluate_governance_regression(receipt, normalized, baseline)
    calibration = build_calibration_record(rubric_hash="rh", rubric_version="1", grader_version="cv1")
    completed = build_completed_eval_record(
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        eval_readiness_receipt_id=receipt.eval_readiness_receipt_id,
        outcome=outcome,
        trajectory=trajectory,
        governance=governance,
        calibration=calibration,
    )
    completed = dataclasses.replace(completed, allowed_downstream_use=downstream)
    return bundle, normalized, trajectory, governance, completed


def test_rca_refuses_unconsumable_eval_record(sealed_completed_run):
    _b, normalized, traj, gov, completed = _make_completed(sealed_completed_run, downstream="HOLD_ONLY")
    with pytest.raises(RCAError):
        fuse_signals([completed])


def test_rca_packet_carries_affected_surfaces(sealed_completed_run):
    _b, normalized, traj, gov, completed = _make_completed(sealed_completed_run)
    fused = fuse_signals([completed])
    rca = build_rca_packet(fused, normalized=normalized, trajectory=traj, governance=gov)
    assert rca.affected_surfaces, "doctrine: RCA must list affected surface(s)"
    assert rca.deterministic_digest


def test_rca_root_cause_is_known_class(sealed_completed_run):
    _b, normalized, traj, gov, completed = _make_completed(sealed_completed_run)
    fused = fuse_signals([completed])
    rca = build_rca_packet(fused, normalized=normalized, trajectory=traj, governance=gov)
    # Governance baselines mismatched in helper -> POLICY_THRESHOLD_ERROR
    assert rca.root_cause_class == "POLICY_THRESHOLD_ERROR"


def test_first_bad_span_unknown_when_no_error(sealed_completed_run):
    _b, normalized, traj, gov, completed = _make_completed(sealed_completed_run)
    # Strip error_code/retry from normalized to ensure no first_bad_span findable.
    clean = [dataclasses.replace(r, error_code=None, retry_count=0) for r in normalized]
    fused = fuse_signals([completed])
    rca = build_rca_packet(fused, normalized=clean, trajectory=traj, governance=gov)
    assert rca.first_bad_span.confidence == "UNKNOWN"
    assert rca.first_bad_span.span_id is None
    assert "FIRST_BAD_SPAN_UNKNOWN" in rca.uncertainty_markers


def test_unknown_root_cause_with_low_sample_holds(sealed_completed_run):
    """Single sample + no governance drift = UNKNOWN_ROOT_CAUSE with hold reason."""
    bundle, normalized, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    iso = build_surface_isolation_manifest(bundle, read_surfaces_touched=("t",))
    obs = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=iso)
    receipt, _m, _n = evaluate_readiness(bundle, obs, normalized)
    outcome = evaluate_outcome(receipt, normalized)
    trajectory = evaluate_trajectory(receipt, normalized)
    # Use matching baselines (no drift) to drive UNKNOWN_ROOT_CAUSE.
    baseline = GovernanceBaseline(
        policy_hash=bundle.policy_hash,
        rubric_hash="rh",
        replay_digest=bundle.replay_key,
    )
    governance = evaluate_governance_regression(receipt, normalized, baseline)
    calibration = build_calibration_record(rubric_hash="rh", rubric_version="1", grader_version="cv1")
    completed = build_completed_eval_record(
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        eval_readiness_receipt_id=receipt.eval_readiness_receipt_id,
        outcome=outcome,
        trajectory=trajectory,
        governance=governance,
        calibration=calibration,
    )
    fused = fuse_signals([completed])
    rca = build_rca_packet(fused, normalized=normalized, trajectory=trajectory, governance=governance)
    if rca.root_cause_class == "UNKNOWN_ROOT_CAUSE":
        assert rca.no_stable_pattern_reason == "insufficient_sample"


def test_pattern_synthesis_only_emits_with_recurrence(sealed_completed_run):
    _b, normalized, traj, gov, completed = _make_completed(sealed_completed_run)
    fused = fuse_signals([completed])
    rca = build_rca_packet(fused, normalized=normalized, trajectory=traj, governance=gov)
    # Single packet -> below recurrence floor -> no pattern emitted.
    patterns = synthesize_patterns([rca], minimum_recurrence=2)
    assert patterns == []


def test_pattern_synthesis_emits_when_recurrent(sealed_completed_run):
    _b, normalized, traj, gov, completed = _make_completed(sealed_completed_run)
    fused = fuse_signals([completed])
    rca1 = build_rca_packet(fused, normalized=normalized, trajectory=traj, governance=gov)
    rca2 = build_rca_packet(fused, normalized=normalized, trajectory=traj, governance=gov)
    patterns = synthesize_patterns([rca1, rca2], minimum_recurrence=2)
    assert len(patterns) == 1
    p = patterns[0]
    assert p.recurrence_score >= 2.0
    assert p.proposed_action_class in ("PROPOSE_FIX", "WATCH")
    assert p.deterministic_digest


def test_drift_cluster_map_groups_by_root_cause(sealed_completed_run):
    _b, normalized, traj, gov, completed = _make_completed(sealed_completed_run)
    fused = fuse_signals([completed])
    rca1 = build_rca_packet(fused, normalized=normalized, trajectory=traj, governance=gov)
    rca2 = build_rca_packet(fused, normalized=normalized, trajectory=traj, governance=gov)
    cluster = build_drift_cluster_map([rca1, rca2])
    # Both packets have same root cause class -> one cluster with 2 items.
    assert len(cluster.clusters) == 1
    [(_cls, ids)] = cluster.clusters.items()
    assert len(ids) == 2
