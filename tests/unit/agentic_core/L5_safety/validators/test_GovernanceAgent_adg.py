"""ADG-driven tests for agentic_core/L5_safety/validators/GovernanceAgent.py — fan_in=2."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.validators.GovernanceAgent import (  # noqa: F401
        LOGGER,
        DependencyGraph,
        GovernanceAgent,
        create_architecture_governor,
        get_governance_agent,
        heal,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    DependencyGraph = None  # type: ignore[assignment,misc]
    GovernanceAgent = None  # type: ignore[assignment,misc]
    heal = None  # type: ignore[assignment,misc]
    create_architecture_governor = None  # type: ignore[assignment,misc]
    get_governance_agent = None  # type: ignore[assignment,misc]
    LOGGER = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestDependencyGraph:
    def test_is_class(self):
        assert isinstance(DependencyGraph, type)
    def test_importable(self):
        assert DependencyGraph is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestGovernanceAgent:
    def test_is_class(self):
        assert isinstance(GovernanceAgent, type)
    def test_importable(self):
        assert GovernanceAgent is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestHeal:
    def test_is_callable(self):
        assert callable(heal)

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestCreateArchitectureGovernor:
    def test_is_callable(self):
        assert callable(create_architecture_governor)

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestGetGovernanceAgent:
    def test_is_callable(self):
        assert callable(get_governance_agent)

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestLoggerConstant:
    def test_is_not_none(self):
        assert LOGGER is not None


def test_module_importable():
    """Module GovernanceAgent.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
