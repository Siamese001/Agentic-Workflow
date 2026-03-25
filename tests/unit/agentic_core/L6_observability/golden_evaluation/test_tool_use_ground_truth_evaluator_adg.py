"""ADG-driven tests for agentic_core/L6_observability/golden_evaluation/tool_use_ground_truth_evaluator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L6_observability.golden_evaluation.tool_use_ground_truth_evaluator  # noqa: F401


def test_module_importable():
    """Module tool_use_ground_truth_evaluator must be importable."""
    assert agentic_core.L6_observability.golden_evaluation.tool_use_ground_truth_evaluator is not None
