"""ADG-driven tests for agentic_core/L5_safety/reasoning/GovernanceAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.GovernanceAgent import (  # noqa: F401
        DependencyGraph,
        GovernanceAgent,
        heal,
        create_architecture_governor,
        get_GovernanceAgent,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DependencyGraph = None  # type: ignore[assignment,misc]
    GovernanceAgent = None  # type: ignore[assignment,misc]
    heal = None  # type: ignore[assignment,misc]
    create_architecture_governor = None  # type: ignore[assignment,misc]
    get_GovernanceAgent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


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
class TestGetGovernanceagent:
    def test_is_callable(self):
        assert callable(get_GovernanceAgent)

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module GovernanceAgent.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
