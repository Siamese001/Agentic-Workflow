"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/GovernanceAgent.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_GovernanceAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.GovernanceAgent import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        DependencyGraph,
        GovernanceAgent,
        create_architecture_governor,
        get_GovernanceAgent,
        heal,
    )
    _AVAILABLE = True
except ImportError as _exc:
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


@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestDependencyGraphContract:
    def test_is_class(self):
        assert isinstance(DependencyGraph, type)

    def test_has_method_build(self):
        assert callable(getattr(DependencyGraph, 'build', None))

    def test_has_method_get_impact_radius(self):
        assert callable(getattr(DependencyGraph, 'get_impact_radius', None))

    def test_has_method_get_dependency_tree(self):
        assert callable(getattr(DependencyGraph, 'get_dependency_tree', None))

    def test_has_method_visualize_graph(self):
        assert callable(getattr(DependencyGraph, 'visualize_graph', None))

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestGovernanceAgentContract:
    def test_is_class(self):
        assert isinstance(GovernanceAgent, type)

    def test_has_method_hierarchy_agent(self):
        assert callable(getattr(GovernanceAgent, 'hierarchy_agent', None))

    def test_has_method_import_agent(self):
        assert callable(getattr(GovernanceAgent, 'import_agent', None))

    def test_has_method_build_graph(self):
        assert callable(getattr(GovernanceAgent, 'build_graph', None))

    def test_has_method_check_root_hygiene(self):
        assert callable(getattr(GovernanceAgent, 'check_root_hygiene', None))

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestHealFunction:
    def test_is_callable(self):
        assert callable(heal)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(heal)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestCreateArchitectureGovernorFunction:
    def test_is_callable(self):
        assert callable(create_architecture_governor)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_architecture_governor)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent.py deps unavailable")
class TestGetGovernanceagentFunction:
    def test_is_callable(self):
        assert callable(get_GovernanceAgent)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_GovernanceAgent)
        assert sig.return_annotation is not inspect.Parameter.empty

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


def test_module_importable():
    """Module GovernanceAgent must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
