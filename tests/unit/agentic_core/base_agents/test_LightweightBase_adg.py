"""ADG-driven tests for agentic_core/base_agents/LightweightBase.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.base_agents.LightweightBase  # noqa: F401


def test_module_importable():
    """Module LightweightBase must be importable."""
    assert agentic_core.base_agents.LightweightBase is not None
