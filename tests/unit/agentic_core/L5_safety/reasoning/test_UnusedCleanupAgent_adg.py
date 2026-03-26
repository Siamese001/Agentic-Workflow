"""ADG-driven tests for agentic_core/L5_safety/reasoning/UnusedCleanupAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.reasoning.UnusedCleanupAgent  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.reasoning.UnusedCleanupAgent  # noqa: F401
        """Module UnusedCleanupAgent must be importable."""
        assert agentic_core.L5_safety.reasoning.UnusedCleanupAgent is not None

    assert agentic_core.L5_safety.reasoning.UnusedCleanupAgent is not None
