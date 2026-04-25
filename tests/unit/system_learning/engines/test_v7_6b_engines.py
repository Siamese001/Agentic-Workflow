"""W3 tests for v7 6B engines: trajectory_evaluator, governance_regression_checker,
eval_record_signer."""

from __future__ import annotations

import pytest

from system_learning.engines.eval_record_signer import (
    CompletedEvalRecord,
    EvalRecordSigner,
)
from system_learning.engines.governance_regression_checker import (
    GovernanceRegressionChecker,
)
from system_learning.engines.trajectory_evaluator import TrajectoryEvaluator
from system_learning.engines.v7_kpi_board import (
    UnifiedKPIBoard,
    V7KPIName,
)


# ---- trajectory_evaluator -------------------------------------------------


def test_trajectory_clean_run_high_score():
    ev = TrajectoryEvaluator()
    rec = ev.evaluate(
        trace_id="t1", run_id="r1",
        path_features={
            "route_quality": 1.0, "tool_quality": 1.0, "retry_quality": 1.0,
            "cost_quality": 1.0, "budget_quality": 1.0,
            "evidence_path_integrity": 1.0,
        },
    )
    assert rec.path_score == 1.0
    assert rec.detected_defects == ()


def test_trajectory_defects_discount_path_score():
    ev = TrajectoryEvaluator()
    rec = ev.evaluate(
        trace_id="t1", run_id="r1",
        path_features={
            "route_quality": 1.0, "tool_quality": 1.0,
            "defects": ["route_thrash", "silent_fallback"],
        },
    )
    # 2 defects = 10% discount
    assert rec.path_score == pytest.approx(0.9)
    assert "route_thrash" in rec.detected_defects
    assert "silent_fallback" in rec.detected_defects


def test_trajectory_unknown_defects_dropped():
    ev = TrajectoryEvaluator()
    rec = ev.evaluate(
        trace_id="t1", run_id="r1",
        path_features={"defects": ["bogus_defect", "tool_misuse"]},
    )
    assert "bogus_defect" not in rec.detected_defects
    assert "tool_misuse" in rec.detected_defects


def test_trajectory_subscore_clamped_to_01_range():
    ev = TrajectoryEvaluator()
    rec = ev.evaluate(
        trace_id="t1", run_id="r1",
        path_features={"route_quality": -5.0, "tool_quality": 99.0},
    )
    assert rec.route_quality == 0.0
    assert rec.tool_quality == 1.0


def test_trajectory_ret_runs_skip_counter():
    ev = TrajectoryEvaluator()
    ev.evaluate(trace_id="t1", run_id="r1", path_features={}, is_retrieval_only=True)
    ev.evaluate(trace_id="t2", run_id="r2", path_features={})
    graded, total_non_ret = ev.counters
    assert graded == 1 and total_non_ret == 1


def test_trajectory_publishes_coverage_kpi():
    ev = TrajectoryEvaluator()
    board = UnifiedKPIBoard()
    for i in range(5):
        ev.evaluate(trace_id=f"t{i}", run_id=f"r{i}", path_features={})
    ev.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.TRAJECTORY_EVAL_COVERAGE)  # type: ignore[arg-type]
    assert sample.value == 1.0


# ---- governance_regression_checker ----------------------------------------


def test_governance_known_drift_kept():
    g = GovernanceRegressionChecker()
    rec = g.check(
        trace_id="t1", run_id="r1",
        drift_flags=("policy_drift", "rubric_calibration_error"),
        impacted_surfaces=("L5",),
        severity="high", suspected_cause="rubric not recalibrated",
        is_high_risk=True,
    )
    assert "policy_drift" in rec.drift_flags
    # rubric_calibration_error is NOT in v7 S2C list — expect it dropped
    assert "rubric_calibration_error" not in rec.drift_flags


def test_governance_unknown_severity_normalized():
    g = GovernanceRegressionChecker()
    rec = g.check(
        trace_id="t1", run_id="r1",
        drift_flags=(), impacted_surfaces=(),
        severity="catastrophic", suspected_cause="",
        is_high_risk=False,
    )
    assert rec.severity == "medium"


def test_governance_required_review_only_when_high_severity_and_flags():
    g = GovernanceRegressionChecker()
    rec = g.check(
        trace_id="t1", run_id="r1",
        drift_flags=("prompt_drift",), impacted_surfaces=(),
        severity="critical", suspected_cause="",
        is_high_risk=True,
    )
    assert rec.required_review is True
    rec_low = g.check(
        trace_id="t2", run_id="r2",
        drift_flags=("prompt_drift",), impacted_surfaces=(),
        severity="low", suspected_cause="",
        is_high_risk=False,
    )
    assert rec_low.required_review is False


def test_governance_publishes_coverage_kpi():
    g = GovernanceRegressionChecker()
    board = UnifiedKPIBoard()
    for i in range(8):
        g.check(
            trace_id=f"t{i}", run_id=f"r{i}",
            drift_flags=(), impacted_surfaces=(),
            severity="low", suspected_cause="",
            is_high_risk=True,
        )
    g.mark_high_risk_observed_unchecked()
    g.mark_high_risk_observed_unchecked()
    g.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.GOVERNANCE_EVAL_COVERAGE)  # type: ignore[arg-type]
    assert sample.value == pytest.approx(0.8)


def test_governance_publishes_zero_kpi_with_no_high_risk():
    g = GovernanceRegressionChecker()
    board = UnifiedKPIBoard()
    g.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.GOVERNANCE_EVAL_COVERAGE)  # type: ignore[arg-type]
    assert sample.value == 0.0


# ---- eval_record_signer ---------------------------------------------------


def _seal_args():
    return dict(
        trace_id="t1", run_id="r1",
        rubric_hash="rh", grader_version="g1",
        evidence_snapshot_hash="ev",
        outcome_eval_ref="o", trajectory_eval_ref="tr",
        governance_eval_ref="g", calibration_ref="c",
        score_bundle={"task_completion": 1.0, "groundedness": 0.9},
    )


def test_seal_produces_completed_record():
    s = EvalRecordSigner()
    rec = s.seal(**_seal_args(), signed_at=1000.0)
    assert isinstance(rec, CompletedEvalRecord)
    assert rec.signed_at == 1000.0
    assert rec.score_bundle == {"task_completion": 1.0, "groundedness": 0.9}


def test_seal_eval_record_id_is_content_addressed():
    s = EvalRecordSigner()
    a = s.seal(**_seal_args(), signed_at=1000.0)
    b = s.seal(**_seal_args(), signed_at=2000.0)
    # signed_at differs but content hash is computed from payload only
    assert a.eval_record_id == b.eval_record_id


def test_seal_id_changes_when_payload_changes():
    s = EvalRecordSigner()
    a = s.seal(**_seal_args(), signed_at=1000.0)
    args = _seal_args()
    args["score_bundle"] = {"task_completion": 0.5}
    b = s.seal(**args, signed_at=1000.0)
    assert a.eval_record_id != b.eval_record_id


def test_seal_default_uncertainty_and_overrides():
    s = EvalRecordSigner()
    rec = s.seal(**_seal_args())
    assert rec.uncertainty_markers == ()
    assert rec.reviewer_overrides == ()
