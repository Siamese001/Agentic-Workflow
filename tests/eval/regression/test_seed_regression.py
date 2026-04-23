"""LJH5.2 regression suite — seed test.

Enforces the LJH ``>=98% pass@1`` invariant on a deterministic set of
fake results. Real regression items replace this stub once the golden
set + judge stack produce per-task pass/fail outcomes.
"""

from __future__ import annotations

import importlib

import pytest

_stability = importlib.import_module("agentic_core.evaluation.metrics.stability")
StabilityReport = _stability.StabilityReport

# Deterministic, controlled regression fixture: 50 trials, 50 successes.
REGRESSION_FIXTURE = [True] * 50
REGRESSION_THRESHOLD = 0.98


@pytest.mark.eval_regression
def test_regression_seed_meets_threshold() -> None:
    report = StabilityReport.from_results(REGRESSION_FIXTURE, k_values=(1,))
    pak_1 = dict(report.pass_at_k_values)[1]
    assert pak_1 >= REGRESSION_THRESHOLD, (
        f"regression pass@1={pak_1:.3f} below threshold {REGRESSION_THRESHOLD}"
    )


@pytest.mark.eval_regression
def test_regression_seed_has_no_zero_pass_rate() -> None:
    report = StabilityReport.from_results(REGRESSION_FIXTURE)
    assert report.pass_rate > 0.0
