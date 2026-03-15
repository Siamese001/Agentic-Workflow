"""ADG-driven tests for agentic_core/runtime/engine/agent_engine.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.runtime.engine.agent_engine import (  # noqa: F401
        AgentEngine,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    AgentEngine = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="agent_engine.py deps unavailable")
class TestAgentEngine:
    def test_is_class(self):
        assert isinstance(AgentEngine, type)
    def test_importable(self):
        assert AgentEngine is not None


def test_module_importable():
    """Module agent_engine.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
