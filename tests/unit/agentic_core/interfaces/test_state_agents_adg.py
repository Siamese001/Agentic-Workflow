"""ADG-driven tests for agentic_core/interfaces/state_agents.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.interfaces.state_agents  # noqa: F401


def test_module_importable():
    """Module state_agents must be importable."""
    assert agentic_core.interfaces.state_agents is not None
