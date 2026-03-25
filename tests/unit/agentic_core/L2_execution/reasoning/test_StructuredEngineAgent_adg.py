"""ADG-driven tests for agentic_core/L2_execution/reasoning/StructuredEngineAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.reasoning.StructuredEngineAgent  # noqa: F401


def test_module_importable():
    """Module StructuredEngineAgent must be importable."""
    assert agentic_core.L2_execution.reasoning.StructuredEngineAgent is not None
