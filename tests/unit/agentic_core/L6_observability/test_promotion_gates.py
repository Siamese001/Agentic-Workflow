"""Unit tests for ``agentic_core.L6_observability.promotion_gates``.

Plan: ``.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`` W12.
"""

from __future__ import annotations

import pytest

from agentic_core.L6_observability.promotion_gates import (
    MetricSample,
    auto_rollback_trigger,
    counterfactual_uplift,
    promotion_decision,
    wilson_interval,
)


def test_wilson_zero_sample_returns_full_interval() -> None:
    ci = wilson_interval(0, 0)
    assert ci.lower == 0.0
    assert ci.upper == 1.0
    assert ci.n == 0


def test_wilson_perfect_record_tight_upper() -> None:
    ci = wilson_interval(100, 100)
    assert ci.point == 1.0
    # Wilson upper for 100/100 at z=1.96 → ≈1.0 (floating-point ε permitted)
    assert ci.upper == pytest.approx(1.0, abs=1e-9)
    assert ci.lower < 1.0  # never claims certainty


def test_wilson_50_50_centered() -> None:
    ci = wilson_interval(50, 100)
    assert ci.point == 0.5
    assert ci.lower < 0.5 < ci.upper
    # Sanity — 95% CI around 0.5 with n=100 is roughly [0.40, 0.60]
    assert 0.39 < ci.lower < 0.41
    assert 0.59 < ci.upper < 0.61


def test_wilson_invalid_inputs_raise() -> None:
    with pytest.raises(ValueError):
        wilson_interval(-1, 10)
    with pytest.raises(ValueError):
        wilson_interval(11, 10)
    with pytest.raises(ValueError):
        wilson_interval(5, -1)


def test_promotion_blocked_when_insufficient_samples() -> None:
    v = promotion_decision(
        candidate_successes=10,
        candidate_n=10,
        baseline_successes=5,
        baseline_n=10,
        min_n_each_arm=30,
    )
    assert v.promote is False
    assert "insufficient" in v.reason


def test_promotion_blocked_when_cis_overlap() -> None:
    v = promotion_decision(
        candidate_successes=85,
        candidate_n=100,
        baseline_successes=80,
        baseline_n=100,
        min_n_each_arm=30,
    )
    # CIs likely overlap at 95% on n=100; promote=False expected
    assert v.promote is False


def test_promotion_succeeds_with_strong_uplift() -> None:
    v = promotion_decision(
        candidate_successes=99,
        candidate_n=100,
        baseline_successes=50,
        baseline_n=100,
        min_n_each_arm=30,
    )
    assert v.promote is True
    assert v.candidate.lower > v.baseline.upper


def test_metric_sample_regression_sigma_zero_stddev() -> None:
    s = MetricSample(
        metric_name="m",
        canary_mean=0.9,
        canary_stddev=0.0,
        baseline_mean=0.95,
        baseline_stddev=0.0,
        n=100,
    )
    # Zero baseline stddev + canary < baseline → infinite regression
    assert s.regression_sigma == float("inf")


def test_metric_sample_regression_sigma_normal() -> None:
    s = MetricSample(
        metric_name="m",
        canary_mean=0.80,
        canary_stddev=0.05,
        baseline_mean=0.90,
        baseline_stddev=0.05,
        n=100,
    )
    # (0.90 - 0.80) / 0.05 = 2.0
    assert s.regression_sigma == pytest.approx(2.0)


def test_auto_rollback_triggers_on_regression() -> None:
    samples = [
        MetricSample("hit_ratio", 0.40, 0.05, 0.50, 0.05, 100),  # regressed 2σ
        MetricSample("brier", 0.20, 0.02, 0.18, 0.02, 100),  # not a regression (lower brier=better in their convention)
    ]
    rollback, regressed = auto_rollback_trigger(samples, sigma_threshold=1.5)
    assert rollback is True
    assert "hit_ratio" in regressed


def test_auto_rollback_skips_undersized_samples() -> None:
    samples = [
        MetricSample("m", 0.1, 0.05, 0.9, 0.05, 5),  # huge regression but n<20
    ]
    rollback, regressed = auto_rollback_trigger(samples, sigma_threshold=1.5, min_n=20)
    assert rollback is False
    assert regressed == []


def test_auto_rollback_no_regression_no_trigger() -> None:
    samples = [
        MetricSample("hit_ratio", 0.55, 0.05, 0.50, 0.05, 100),  # canary BETTER
        MetricSample("brier", 0.18, 0.02, 0.20, 0.02, 100),
    ]
    rollback, regressed = auto_rollback_trigger(samples, sigma_threshold=1.5)
    assert rollback is False
    assert regressed == []


def test_auto_rollback_invalid_inputs_raise() -> None:
    with pytest.raises(ValueError):
        auto_rollback_trigger([], sigma_threshold=-1.0)
    with pytest.raises(ValueError):
        auto_rollback_trigger([], min_n=0)


def test_counterfactual_uplift_zero_when_empty() -> None:
    assert counterfactual_uplift([], []) == 0.0


def test_counterfactual_uplift_positive_when_shadow_better() -> None:
    shadow = [True] * 80 + [False] * 20
    prod = [True] * 50 + [False] * 50
    assert counterfactual_uplift(shadow, prod) == pytest.approx(0.30)


def test_counterfactual_uplift_negative_when_shadow_worse() -> None:
    shadow = [True] * 30 + [False] * 70
    prod = [True] * 60 + [False] * 40
    assert counterfactual_uplift(shadow, prod) == pytest.approx(-0.30)


def test_counterfactual_uplift_length_mismatch_raises() -> None:
    with pytest.raises(ValueError):
        counterfactual_uplift([True], [True, False])
