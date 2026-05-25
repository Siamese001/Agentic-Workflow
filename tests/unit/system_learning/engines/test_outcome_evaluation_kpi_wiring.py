"""W11 wiring test: OutcomeEvaluationEngine EVAL_COVERAGE_OF_RUNS KPI."""

from __future__ import annotations

import pytest

from agentic_core.L6_system_learning.outcome_evaluation_engine import OutcomeEvaluationEngine
from agentic_core.L6_system_learning.v6_kpi_board import V6KPIBoard, V6KPIName


def test_initial_counters_zero():
    engine = OutcomeEvaluationEngine()
    assert engine.coverage_counters == (0, 0)


def test_mark_run_observed_only_increments_total():
    engine = OutcomeEvaluationEngine()
    engine.mark_run_observed()
    engine.mark_run_observed()
    assert engine.coverage_counters == (0, 2)


def test_mark_run_evaluated_only_increments_eval():
    engine = OutcomeEvaluationEngine()
    engine.mark_run_evaluated()
    assert engine.coverage_counters == (1, 0)


def test_evaluate_outcome_increments_both():
    engine = OutcomeEvaluationEngine()
    engine.evaluate_outcome(
        trace_id="t1",
        execution_result={"task_completed": True, "response": "ok"},
        timestamp_utc=1000,
    )
    assert engine.coverage_counters == (1, 1)


def test_reset_clears_counters():
    engine = OutcomeEvaluationEngine()
    engine.mark_run_observed()
    engine.mark_run_evaluated()
    engine.reset_coverage_counters()
    assert engine.coverage_counters == (0, 0)


def test_publish_records_ratio():
    engine = OutcomeEvaluationEngine()
    board = V6KPIBoard()
    for _ in range(99):
        engine.mark_run_observed()
        engine.mark_run_evaluated()
    engine.mark_run_observed()  # 100th run, no eval (gap)
    engine.publish_kpi_sample(board)
    sample = board.latest(V6KPIName.EVAL_COVERAGE_OF_RUNS)
    assert sample is not None
    assert sample.value == pytest.approx(0.99)
    assert sample.source == "outcome_evaluation_engine"


def test_publish_with_zero_runs_reports_zero():
    engine = OutcomeEvaluationEngine()
    board = V6KPIBoard()
    engine.publish_kpi_sample(board)
    sample = board.latest(V6KPIName.EVAL_COVERAGE_OF_RUNS)
    assert sample.value == 0.0


def test_publish_does_not_raise_on_invalid_board():
    engine = OutcomeEvaluationEngine()
    engine.mark_run_observed()
    engine.publish_kpi_sample(object())  # must not raise
