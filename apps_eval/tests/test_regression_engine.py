from __future__ import annotations

from apps_eval.runner.core import compare_record_to_baseline


def test_regression_engine_passes_equal_score() -> None:
    summary = compare_record_to_baseline({"scorecard": {"score": 1.0}}, {"scorecard": {"score": 1.0}})
    assert summary.compared is True
    assert summary.delta == 0.0
    assert summary.verdict == "pass"


def test_regression_engine_detects_lower_score() -> None:
    summary = compare_record_to_baseline({"scorecard": {"score": 0.9}}, {"scorecard": {"score": 1.0}})
    assert summary.verdict == "regression"
    assert summary.delta == -0.1
