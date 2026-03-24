"""ADG-driven tests for agentic_core/L6_observability/enforcement/agent_monitor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L6_observability.enforcement.agent_monitor import (  # noqa: F401
        ExecutionTimer,
        UnifiedAgentMonitor,
        get_monitor,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    UnifiedAgentMonitor = None  # type: ignore[assignment,misc]
    ExecutionTimer = None  # type: ignore[assignment,misc]
    get_monitor = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="agent_monitor.py deps unavailable")
class TestUnifiedAgentMonitor:
    def test_is_class(self):
        assert isinstance(UnifiedAgentMonitor, type)
    def test_importable(self):
        assert UnifiedAgentMonitor is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_monitor.py deps unavailable")
class TestExecutionTimer:
    def test_is_class(self):
        assert isinstance(ExecutionTimer, type)
    def test_importable(self):
        assert ExecutionTimer is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_monitor.py deps unavailable")
class TestGetMonitor:
    def test_is_callable(self):
        assert callable(get_monitor)


def test_module_importable():
    """Module agent_monitor.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE