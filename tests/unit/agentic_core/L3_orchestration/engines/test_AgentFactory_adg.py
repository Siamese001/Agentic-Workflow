"""ADG-driven tests for agentic_core/L3_orchestration/engines/AgentFactory.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L3_orchestration.engines.AgentFactory  # noqa: F401


def test_module_importable():
    import agentic_core.L3_orchestration.engines.AgentFactory  # noqa: F401
    """Module AgentFactory must be importable."""
    assert agentic_core.L3_orchestration.engines.AgentFactory is not None
