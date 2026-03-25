"""ADG-driven tests for agentic_core/L6_observability/golden_evaluation/injection_regression_suite.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L6_observability.golden_evaluation.injection_regression_suite  # noqa: F401


def test_module_importable():
    """Module injection_regression_suite must be importable."""
    assert agentic_core.L6_observability.golden_evaluation.injection_regression_suite is not None
