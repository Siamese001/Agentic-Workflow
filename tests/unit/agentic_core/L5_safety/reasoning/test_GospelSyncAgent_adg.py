"""ADG-driven tests for agentic_core/L5_safety/reasoning/GospelSyncAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.reasoning.GospelSyncAgent  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.reasoning.GospelSyncAgent  # noqa: F401
        """Module GospelSyncAgent must be importable."""
        assert agentic_core.L5_safety.reasoning.GospelSyncAgent is not None

    assert agentic_core.L5_safety.reasoning.GospelSyncAgent is not None
