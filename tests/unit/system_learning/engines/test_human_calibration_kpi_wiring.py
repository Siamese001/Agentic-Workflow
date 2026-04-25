"""W12 wiring test: HumanCalibrationEngine v6 KPI publication.

Covers JUDGE_HUMAN_KAPPA_FRESHNESS (worst-case rubric age) and
JUDGE_UNKNOWN_BUDGET_COMPLIANCE (compliant_judges / total_judges).
"""

from __future__ import annotations

import pytest

from system_learning.engines.human_calibration_engine import HumanCalibrationEngine
from system_learning.engines.v6_kpi_board import V6KPIBoard, V6KPIName


def test_initial_state_clean():
    engine = HumanCalibrationEngine()
    rubrics, compliant, total = engine.calibration_state
    assert rubrics == {}
    assert compliant == 0
    assert total == 0


def test_mark_calibration_records_per_rubric():
    engine = HumanCalibrationEngine()
    engine.mark_calibration(rubric_id="r1", epoch=100.0)
    engine.mark_calibration(rubric_id="r2", epoch=200.0)
    rubrics, _, _ = engine.calibration_state
    assert rubrics == {"r1": 100.0, "r2": 200.0}


def test_mark_calibration_keeps_newest_per_rubric():
    engine = HumanCalibrationEngine()
    engine.mark_calibration(rubric_id="r1", epoch=100.0)
    engine.mark_calibration(rubric_id="r1", epoch=50.0)  # older — ignored
    engine.mark_calibration(rubric_id="r1", epoch=300.0)  # newer — kept
    rubrics, _, _ = engine.calibration_state
    assert rubrics == {"r1": 300.0}


def test_mark_judge_scored_counters():
    engine = HumanCalibrationEngine()
    engine.mark_judge_scored(compliant=True)
    engine.mark_judge_scored(compliant=True)
    engine.mark_judge_scored(compliant=False)
    _, compliant, total = engine.calibration_state
    assert compliant == 2
    assert total == 3


def test_reset_clears_all_state():
    engine = HumanCalibrationEngine()
    engine.mark_calibration(rubric_id="r1", epoch=1.0)
    engine.mark_judge_scored(compliant=True)
    engine.reset_calibration_state()
    rubrics, compliant, total = engine.calibration_state
    assert rubrics == {}
    assert compliant == 0
    assert total == 0


def test_publish_freshness_uses_oldest_rubric():
    engine = HumanCalibrationEngine()
    board = V6KPIBoard()
    engine.mark_calibration(rubric_id="r_new", epoch=1000.0)
    engine.mark_calibration(rubric_id="r_old", epoch=100.0)
    engine.publish_kpi_sample(board, now=1500.0)
    sample = board.latest(V6KPIName.JUDGE_HUMAN_KAPPA_FRESHNESS)
    assert sample is not None
    # age = now - oldest_epoch = 1500 - 100 = 1400
    assert sample.value == 1400.0
    assert sample.metadata["rubric_id"] == "r_old"


def test_publish_skips_freshness_with_no_calibrations():
    engine = HumanCalibrationEngine()
    board = V6KPIBoard()
    engine.publish_kpi_sample(board, now=1000.0)
    # No rubrics calibrated — sample MUST be skipped (no spurious zero).
    assert board.latest(V6KPIName.JUDGE_HUMAN_KAPPA_FRESHNESS) is None


def test_publish_compliance_ratio():
    engine = HumanCalibrationEngine()
    board = V6KPIBoard()
    for _ in range(95):
        engine.mark_judge_scored(compliant=True)
    for _ in range(5):
        engine.mark_judge_scored(compliant=False)
    engine.publish_kpi_sample(board)
    sample = board.latest(V6KPIName.JUDGE_UNKNOWN_BUDGET_COMPLIANCE)
    assert sample is not None
    assert sample.value == pytest.approx(0.95)
    assert sample.source == "human_calibration_engine"


def test_publish_compliance_zero_total():
    engine = HumanCalibrationEngine()
    board = V6KPIBoard()
    engine.publish_kpi_sample(board)
    sample = board.latest(V6KPIName.JUDGE_UNKNOWN_BUDGET_COMPLIANCE)
    # zero-total compliance reports 0.0 (red — explicit "we have no data")
    assert sample.value == 0.0


def test_publish_does_not_raise_on_invalid_board():
    engine = HumanCalibrationEngine()
    engine.mark_calibration(rubric_id="r", epoch=1.0)
    engine.publish_kpi_sample(object())  # must not raise
