"""ADG-driven tests for agentic_core/L3_orchestration/engines/bounded_task_decomposer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L3_orchestration.engines.bounded_task_decomposer  # noqa: F401


def test_module_importable():
    """Module bounded_task_decomposer must be importable."""
    assert agentic_core.L3_orchestration.engines.bounded_task_decomposer is not None
