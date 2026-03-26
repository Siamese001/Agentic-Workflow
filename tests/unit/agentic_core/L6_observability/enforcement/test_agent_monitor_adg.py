"""ADG-driven tests for agentic_core/L6_observability/enforcement/agent_monitor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L6_observability.enforcement.agent_monitor  # noqa: F401


def test_module_importable():
        import agentic_core.L6_observability.enforcement.agent_monitor  # noqa: F401
        """Module agent_monitor must be importable."""
        assert agentic_core.L6_observability.enforcement.agent_monitor is not None

    assert agentic_core.L6_observability.enforcement.agent_monitor is not None
