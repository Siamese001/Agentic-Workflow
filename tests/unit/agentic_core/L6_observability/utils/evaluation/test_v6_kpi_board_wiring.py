"""W4 wiring test: ``learning_metrics_dashboard.get_v6_kpi_board`` exposes
the canonical V6 KPI Board singleton.
"""

from __future__ import annotations

from agentic_core.L6_observability.utils.evaluation.learning_metrics_dashboard import (
    get_v6_kpi_board,
    reset_v6_kpi_board,
)
from agentic_core.L6_system_learning.engines.v6_kpi_board import V6KPIBoard, V6KPIName


def setup_function(_func):
    reset_v6_kpi_board()


def teardown_function(_func):
    reset_v6_kpi_board()


def test_accessor_returns_v6kpiboard():
    board = get_v6_kpi_board()
    assert isinstance(board, V6KPIBoard)


def test_accessor_returns_singleton():
    a = get_v6_kpi_board()
    b = get_v6_kpi_board()
    assert a is b


def test_accessor_persists_recorded_samples():
    board = get_v6_kpi_board()
    board.record_value(
        V6KPIName.EVAL_COVERAGE_OF_RUNS, 0.99, source="wiring_test"
    )
    again = get_v6_kpi_board()
    sample = again.latest(V6KPIName.EVAL_COVERAGE_OF_RUNS)
    assert sample is not None
    assert sample.value == 0.99
    assert sample.source == "wiring_test"


def test_reset_drops_singleton():
    a = get_v6_kpi_board()
    a.record_value(V6KPIName.SATURATION_WATCH, 0.05, source="wiring_test")
    reset_v6_kpi_board()
    b = get_v6_kpi_board()
    assert b is not a
    assert b.latest(V6KPIName.SATURATION_WATCH) is None
