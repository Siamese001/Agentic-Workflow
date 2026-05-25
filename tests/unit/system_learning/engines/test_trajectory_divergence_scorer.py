"""Unit tests for :mod:`system_learning.engines.trajectory_divergence_scorer`."""

from __future__ import annotations

from typing import Any

from agentic_core.L6_system_learning.trajectory_divergence_scorer import (
    DivergencePoint,
    TrajectorySpan,
    localize_first_divergence,
    score_divergence,
)


def _span(index: int, **overrides: Any) -> TrajectorySpan:
    defaults: dict[str, Any] = dict(
        tool_name="search",
        tool_args={"q": "test"},
        tool_result_hash="h0",
        model_name="model-a",
        stub_id="",
    )
    defaults.update(overrides)
    return TrajectorySpan(step_index=index, **defaults)


def test_identical_trajectories_distance_zero() -> None:
    baseline = [_span(0), _span(1), _span(2)]
    replay = [_span(0), _span(1), _span(2)]
    report = score_divergence(baseline, replay)
    assert report.distance == 0.0
    assert report.divergent_span_count == 0
    assert report.total_spans == 3
    assert report.first_divergence is None


def test_tool_changed_localizes_to_correct_step() -> None:
    baseline = [_span(0), _span(1, tool_name="search"), _span(2)]
    replay = [_span(0), _span(1, tool_name="lookup"), _span(2)]
    point = localize_first_divergence(baseline, replay)
    assert point is not None
    assert point.step_index == 1
    assert point.category == "tool_changed"


def test_arg_changed_produces_arg_diff() -> None:
    baseline = [_span(0), _span(1, tool_args={"threshold": 0.7})]
    replay = [_span(0), _span(1, tool_args={"threshold": 0.9})]
    point = localize_first_divergence(baseline, replay)
    assert point is not None
    assert point.step_index == 1
    assert point.category == "arg_changed"
    assert point.arg_diff == {"threshold": (0.7, 0.9)}


def test_model_changed_detected() -> None:
    baseline = [_span(0), _span(1, model_name="claude-3-5")]
    replay = [_span(0), _span(1, model_name="claude-3-7")]
    point = localize_first_divergence(baseline, replay)
    assert point is not None
    assert point.category == "model_changed"


def test_stub_miss_detected() -> None:
    baseline = [_span(0, stub_id="")]
    replay = [_span(0, stub_id="stub-abc")]
    point = localize_first_divergence(baseline, replay)
    assert point is not None
    assert point.category == "stub_miss"


def test_result_changed_when_everything_else_matches() -> None:
    baseline = [_span(0, tool_result_hash="hash-aaa")]
    replay = [_span(0, tool_result_hash="hash-bbb")]
    point = localize_first_divergence(baseline, replay)
    assert point is not None
    assert point.category == "result_changed"


def test_missing_span_when_replay_shorter() -> None:
    baseline = [_span(0), _span(1), _span(2)]
    replay = [_span(0), _span(1)]
    report = score_divergence(baseline, replay)
    assert report.first_divergence is not None
    assert report.first_divergence.category == "missing_span"
    assert report.first_divergence.step_index == 2


def test_distance_counts_all_divergences() -> None:
    # 2 spans diverge out of 3 → distance = 2/3
    baseline = [_span(0), _span(1), _span(2)]
    replay = [_span(0, tool_name="other"), _span(1), _span(2, tool_name="other")]
    report = score_divergence(baseline, replay)
    assert report.divergent_span_count == 2
    assert report.total_spans == 3
    assert abs(report.distance - 2 / 3) < 1e-9


def test_empty_trajectories_are_identical() -> None:
    report = score_divergence([], [])
    assert report.distance == 0.0
    assert report.first_divergence is None


def test_priority_order_tool_beats_arg() -> None:
    # When both tool name and args differ, category should be tool_changed (higher priority).
    baseline = [_span(0, tool_name="a", tool_args={"x": 1})]
    replay = [_span(0, tool_name="b", tool_args={"x": 2})]
    point = localize_first_divergence(baseline, replay)
    assert point is not None
    assert point.category == "tool_changed"
    assert isinstance(point, DivergencePoint)
