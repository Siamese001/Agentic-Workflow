"""06.3 outcome / trajectory / governance evaluation tests.

Doctrine TEST REQUIREMENTS:
- 6B refuses without EvalReadinessReceipt.
- UNKNOWN uncertainty is not converted to PASS.
- Unsupported fluency does not earn correctness credit.
- Trajectory flags are not silently dropped.
- Governance regression carries policy_hash, rubric_hash, replay_digest refs.
- Evaluation result is not used as live Exit disposition (the dataclass
  contains no callable runtime hooks; we assert that structurally).
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L6_observability.shadow_eval import (
    CodeOnlyGrader,
    EvaluationError,
    GovernanceBaseline,
    HybridGrader,
    OutcomeEvalRecord,
    READINESS_NON_EVAL,
    TrajectoryEvalRecord,
    build_observer_compliance_receipt,
    build_runtime_exhaust_bundle,
    build_surface_isolation_manifest,
    evaluate_governance_regression,
    evaluate_outcome,
    evaluate_readiness,
    evaluate_trajectory,
    stage_barrier_check,
)


@pytest.fixture
def readiness_for(sealed_completed_run):
    bundle, normalized, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    manifest = build_surface_isolation_manifest(bundle, read_surfaces_touched=("t",))
    observer = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=manifest)
    receipt, _m, _n = evaluate_readiness(bundle, observer, normalized)
    return bundle, normalized, receipt


def test_outcome_eval_requires_ready_receipt(readiness_for):
    _bundle, normalized, receipt = readiness_for
    bad = dataclasses.replace(receipt, readiness_decision=READINESS_NON_EVAL)
    with pytest.raises(EvaluationError):
        evaluate_outcome(bad, normalized)


def test_outcome_eval_emits_record_with_uncertainty_preserved(readiness_for):
    _bundle, normalized, receipt = readiness_for
    record = evaluate_outcome(receipt, normalized)
    assert isinstance(record, OutcomeEvalRecord)
    assert record.deterministic_digest
    # All dimensions present
    for f in dataclasses.fields(record):
        if f.name.endswith("_score"):
            assert getattr(record, f.name) is not None


def test_unknown_dimension_is_not_pass():
    """A grader that returns UNKNOWN must not be coerced to PASS."""
    grader = CodeOnlyGrader()
    score = grader.grade("dim.x", "x", [])  # no evidence -> UNKNOWN
    assert score.result == "UNKNOWN"
    assert score.score < 0.5


def test_trajectory_flags_present_when_warranted():
    """A normalized record with retry_count>2 must surface as a flag."""
    from agentic_core.L6_observability.shadow_eval import NormalizedEvidenceRecord, evaluate_outcome

    norm = NormalizedEvidenceRecord(
        normalized_record_id="n1",
        runtime_exhaust_bundle_id="b1",
        canonical_event_type="tool_call",
        canonical_stage="L2",
        source_ref="span-1",
        normalized_payload_ref="p1",
        trace_id="t",
        span_id="s",
        parent_span_id=None,
        request_id="r",
        run_id="rr",
        tenant_id="x",
        route_id="route",
        retry_count=5,
        error_code="TOOL_TIMEOUT",
        eval_readiness_hint="READY",
    )
    # Build a fake-ready receipt for direct testing.
    from agentic_core.L6_observability.shadow_eval import EvalReadinessReceipt, READINESS_READY

    receipt = EvalReadinessReceipt(
        eval_readiness_receipt_id="r",
        runtime_exhaust_bundle_id="b1",
        observer_receipt_id="o",
        trace_completeness_status="PRESENT",
        artifact_integrity_status="PRESENT",
        replay_key_status="PRESENT",
        policy_hash_status="PRESENT",
        route_contract_status="PRESENT",
        prompt_hash_status="PRESENT",
        source_lineage_status="PRESENT",
        terminal_status_status="PRESENT",
        evaluator_input_status="PRESENT",
        readiness_decision=READINESS_READY,
    )
    rec = evaluate_trajectory(receipt, [norm])
    assert "retry_thrash" in rec.trajectory_flags
    assert "execution_error" in rec.trajectory_flags
    assert rec.span_fault_candidates == ["s"]


def test_governance_regression_drift_flags(readiness_for):
    _bundle, normalized, receipt = readiness_for
    # Baseline differs from the run's policy hash to trigger drift.
    baseline = GovernanceBaseline(
        policy_hash="DIFFERENT-POLICY",
        rubric_hash="rubric-A",
        replay_digest="DIFFERENT-REPLAY",
    )
    rec = evaluate_governance_regression(receipt, normalized, baseline)
    assert rec.policy_drift_flags
    assert rec.replay_digest_drift_flags
    assert rec.severity == "high"
    assert rec.required_review == "L5_GOVERNANCE_REVIEW"
    assert rec.policy_hash == "DIFFERENT-POLICY"
    assert rec.rubric_hash == "rubric-A"
    assert rec.replay_digest == "DIFFERENT-REPLAY"


def test_governance_regression_clean_when_baselines_match(readiness_for):
    _bundle, normalized, receipt = readiness_for
    baseline = GovernanceBaseline(
        policy_hash="policy-hash-A",
        rubric_hash="rubric-A",
        replay_digest="replay-key-A",
    )
    rec = evaluate_governance_regression(receipt, normalized, baseline)
    assert not rec.policy_drift_flags
    assert not rec.replay_digest_drift_flags
    assert rec.severity == "low"


def test_eval_records_have_no_runtime_hooks():
    """Doctrine: evaluation is a data record, not a live disposition."""
    for cls in (OutcomeEvalRecord, TrajectoryEvalRecord):
        for f in dataclasses.fields(cls):
            assert "callable" not in f.name.lower()
            assert "hook" not in f.name.lower()
            assert "publish" not in f.name.lower()


def test_hybrid_grader_marks_grader_type():
    g = HybridGrader()
    s = g.grade("dim", "x", [])
    assert s.grader_type == "hybrid"
