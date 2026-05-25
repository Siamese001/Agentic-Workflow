"""W10 wiring test: DeterministicReplayEngine REPLAY_DIVERGENCE_LOCALIZATION KPI."""

from __future__ import annotations

import pytest

from agentic_core.L6_system_learning.deterministic_replay_engine import (
    DeterministicReplayEngine,
)
from agentic_core.L6_system_learning.v6_kpi_board import V6KPIBoard, V6KPIName


def test_initial_counters_zero():
    engine = DeterministicReplayEngine()
    assert engine.failure_counters == (0, 0)


def test_localized_failure_increments_both():
    engine = DeterministicReplayEngine()
    engine.mark_failure(localized=True)
    engine.mark_failure(localized=True)
    assert engine.failure_counters == (2, 2)


def test_unlocalized_failure_increments_only_total():
    engine = DeterministicReplayEngine()
    engine.mark_failure(localized=False)
    assert engine.failure_counters == (0, 1)


def test_mixed_failures():
    engine = DeterministicReplayEngine()
    for _ in range(9):
        engine.mark_failure(localized=True)
    engine.mark_failure(localized=False)
    assert engine.failure_counters == (9, 10)


def test_reset_clears_counters():
    engine = DeterministicReplayEngine()
    engine.mark_failure(localized=True)
    engine.mark_failure(localized=False)
    engine.reset_failure_counters()
    assert engine.failure_counters == (0, 0)


def test_publish_records_ratio():
    engine = DeterministicReplayEngine()
    board = V6KPIBoard()
    for _ in range(9):
        engine.mark_failure(localized=True)
    engine.mark_failure(localized=False)
    engine.publish_kpi_sample(board)
    sample = board.latest(V6KPIName.REPLAY_DIVERGENCE_LOCALIZATION)
    assert sample is not None
    assert sample.value == pytest.approx(0.9)
    assert sample.source == "deterministic_replay_engine"


def test_publish_with_no_failures_reports_perfect():
    engine = DeterministicReplayEngine()
    board = V6KPIBoard()
    engine.publish_kpi_sample(board)
    sample = board.latest(V6KPIName.REPLAY_DIVERGENCE_LOCALIZATION)
    # Quiet day convention: zero failures == 100% localization (green).
    assert sample.value == 1.0


def test_publish_does_not_raise_on_invalid_board():
    engine = DeterministicReplayEngine()
    engine.mark_failure(localized=True)
    engine.publish_kpi_sample(object())  # must not raise
