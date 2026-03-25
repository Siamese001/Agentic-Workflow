"""ADG-driven tests for agentic_core/L6_observability/engines/PerformanceAnalystAgentSimple.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L6_observability.engines.PerformanceAnalystAgentSimple  # noqa: F401


def test_module_importable():
    """Module PerformanceAnalystAgentSimple must be importable."""
    assert agentic_core.L6_observability.engines.PerformanceAnalystAgentSimple is not None
