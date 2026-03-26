"""ADG-driven tests for agentic_core/L3_orchestration/engines/agent_gym_engine.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L3_orchestration.engines.agent_gym_engine  # noqa: F401


def test_module_importable():
    import agentic_core.L3_orchestration.engines.agent_gym_engine  # noqa: F401
    """Module agent_gym_engine must be importable."""
    assert agentic_core.L3_orchestration.engines.agent_gym_engine is not None
