"""W2 tests for v7 6A engines: schema_normalizer, eval_readiness_classifier,
observer_compliance_recorder."""

from __future__ import annotations

import pytest

from agentic_core.L6_system_learning.eval_readiness_classifier import (
    EvalReadinessClassifier,
    ReadinessVerdict,
)
from agentic_core.L6_system_learning.observer_compliance_recorder import (
    ObserverComplianceRecorder,
)
from agentic_core.L6_system_learning.schema_normalizer import (
    REQUIRED_FIELDS,
    SchemaNormalizer,
)
from agentic_core.L6_system_learning.v7_kpi_board import (
    UnifiedKPIBoard,
    V7KPIName,
)


# ---- schema_normalizer ----------------------------------------------------


def _full_raw():
    return {k: f"v_{k}" for k in REQUIRED_FIELDS} | {"terminal_status": "normal_success"}


def test_normalize_complete_record():
    norm = SchemaNormalizer()
    rec = norm.normalize(_full_raw())
    assert rec.eval_ready is True
    assert rec.evidence_gaps == ()
    assert rec.normalization_warnings == ()


def test_normalize_missing_field_flags_gap():
    norm = SchemaNormalizer()
    raw = _full_raw()
    del raw["replay_key"]
    rec = norm.normalize(raw)
    assert rec.eval_ready is False
    assert "replay_key" in rec.evidence_gaps


def test_normalize_unknown_terminal_status_warns():
    norm = SchemaNormalizer()
    raw = _full_raw()
    raw["terminal_status"] = "made_up_status"
    rec = norm.normalize(raw)
    # unknown but populated; warning emitted but eval_ready unaffected
    assert any("unknown_terminal_status" in w for w in rec.normalization_warnings)


def test_normalize_publishes_completeness_kpi():
    norm = SchemaNormalizer()
    board = UnifiedKPIBoard()
    norm.normalize(_full_raw())
    norm.normalize(_full_raw())
    bad = _full_raw()
    del bad["policy_hash"]
    norm.normalize(bad)
    norm.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.EVIDENCE_FIELD_COMPLETENESS)  # type: ignore[arg-type]
    assert sample is not None
    assert sample.value == pytest.approx(2 / 3)


def test_normalize_publishes_zero_when_empty():
    norm = SchemaNormalizer()
    board = UnifiedKPIBoard()
    norm.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.EVIDENCE_FIELD_COMPLETENESS)  # type: ignore[arg-type]
    assert sample.value == 0.0


# ---- eval_readiness_classifier --------------------------------------------


def test_classify_ready():
    norm = SchemaNormalizer()
    cls = EvalReadinessClassifier()
    rec = norm.normalize(_full_raw())
    receipt = cls.classify(rec)
    assert receipt.verdict is ReadinessVerdict.READY_FOR_6B
    assert receipt.missing_fields == ()


def test_classify_partial_when_only_artifact_digest_missing():
    norm = SchemaNormalizer()
    cls = EvalReadinessClassifier()
    raw = _full_raw()
    del raw["artifact_digest"]
    rec = norm.normalize(raw)
    receipt = cls.classify(rec)
    assert receipt.verdict is ReadinessVerdict.PARTIAL_BUT_SCORABLE


def test_classify_non_evaluable_when_run_id_missing():
    norm = SchemaNormalizer()
    cls = EvalReadinessClassifier()
    raw = _full_raw()
    del raw["run_id"]
    rec = norm.normalize(raw)
    receipt = cls.classify(rec)
    assert receipt.verdict is ReadinessVerdict.NON_EVALUABLE_PACKET


def test_classify_hold_when_policy_hash_missing():
    norm = SchemaNormalizer()
    cls = EvalReadinessClassifier()
    raw = _full_raw()
    del raw["policy_hash"]
    rec = norm.normalize(raw)
    receipt = cls.classify(rec)
    assert receipt.verdict is ReadinessVerdict.HOLD_FOR_MISSING_EVIDENCE


def test_readiness_publishes_coverage_kpi():
    norm = SchemaNormalizer()
    cls = EvalReadinessClassifier()
    board = UnifiedKPIBoard()
    # 3 ready, 1 hold => 3/4 = 0.75
    for _ in range(3):
        cls.classify(norm.normalize(_full_raw()))
    bad = _full_raw()
    del bad["policy_hash"]
    cls.classify(norm.normalize(bad))
    cls.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.EVAL_READINESS_COVERAGE)  # type: ignore[arg-type]
    assert sample.value == pytest.approx(0.75)


# ---- observer_compliance_recorder -----------------------------------------


def test_clean_pass_records_zero_violations():
    rec = ObserverComplianceRecorder()
    receipt = rec.record(
        pass_id="p1",
        touched_surfaces=("traces", "artifacts"),
    )
    assert receipt.isolation_status == "clean"
    assert rec.violation_count == 0


def test_violation_increments_count():
    rec = ObserverComplianceRecorder()
    rec.record(
        pass_id="p2",
        touched_surfaces=("traces",),
        denied_write_attempts=("attempted_l4_write", "attempted_bus_u_publish"),
    )
    assert rec.violation_count == 2


def test_observer_publishes_violation_count_kpi():
    rec = ObserverComplianceRecorder()
    board = UnifiedKPIBoard()
    rec.record(pass_id="p1", touched_surfaces=("traces",))  # clean
    rec.record(
        pass_id="p2",
        touched_surfaces=("traces",),
        denied_write_attempts=("write1",),
    )
    rec.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.OBSERVER_LAW_VIOLATION_COUNT)  # type: ignore[arg-type]
    assert sample.value == 1.0


def test_observer_kpi_zero_with_no_records():
    rec = ObserverComplianceRecorder()
    board = UnifiedKPIBoard()
    rec.publish_kpi_sample(board)
    sample = board.latest(V7KPIName.OBSERVER_LAW_VIOLATION_COUNT)  # type: ignore[arg-type]
    assert sample.value == 0.0


def test_observer_publish_does_not_raise_on_invalid_board():
    rec = ObserverComplianceRecorder()
    rec.record(pass_id="p", touched_surfaces=())
    rec.publish_kpi_sample(object())  # must not raise
