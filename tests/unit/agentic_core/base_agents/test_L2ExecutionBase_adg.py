"""ADG-driven tests for agentic_core/base_agents/L2ExecutionBase.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.base_agents.L2ExecutionBase  # noqa: F401


def test_module_importable():
    """Module L2ExecutionBase must be importable."""
    assert agentic_core.base_agents.L2ExecutionBase is not None
