"""ADG-driven tests for agentic_core/L5_safety/runners/agent_roster_runner.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.runners.agent_roster_runner  # noqa: F401


def test_module_importable():
    """Module agent_roster_runner must be importable."""
    assert agentic_core.L5_safety.runners.agent_roster_runner is not None
