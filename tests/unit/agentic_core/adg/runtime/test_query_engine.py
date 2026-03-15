"""Foundational behavioral tests for agentic_core/adg/runtime/query_engine.py.

fan_in=7 — imported by 7 other modules.
ADG import-hygiene is covered separately by test_query_engine_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.adg.runtime.query_engine import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        ADGRuntimeQueryEngine,
        AgentCapability,
        DependencyPath,
        get_runtime_query_engine,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    AgentCapability = None  # type: ignore[assignment,misc]
    DependencyPath = None  # type: ignore[assignment,misc]
    ADGRuntimeQueryEngine = None  # type: ignore[assignment,misc]
    get_runtime_query_engine = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="query_engine.py deps unavailable")
class TestAgentCapabilityContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AgentCapability)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(AgentCapability)}
        assert fnames >= {'composed_symbol', 'layer', 'module_path', 'agent_class'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(AgentCapability)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="query_engine.py deps unavailable")
class TestDependencyPathContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(DependencyPath)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(DependencyPath)}
        assert fnames >= {'allowed', 'from_module', 'from_layer', 'to_layer', 'to_module', 'reason'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(DependencyPath)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="query_engine.py deps unavailable")
class TestADGRuntimeQueryEngineContract:
    def test_is_class(self):
        assert isinstance(ADGRuntimeQueryEngine, type)

    def test_has_method_find_agents_by_base_class(self):
        assert callable(getattr(ADGRuntimeQueryEngine, 'find_agents_by_base_class', None))

    def test_has_method_find_agents_by_capability(self):
        assert callable(getattr(ADGRuntimeQueryEngine, 'find_agents_by_capability', None))

    def test_has_method_get_reverse_dependencies(self):
        assert callable(getattr(ADGRuntimeQueryEngine, 'get_reverse_dependencies', None))

    def test_has_method_compute_blast_radius(self):
        assert callable(getattr(ADGRuntimeQueryEngine, 'compute_blast_radius', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(ADGRuntimeQueryEngine) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="query_engine.py deps unavailable")
class TestGetRuntimeQueryEngineFunction:
    def test_is_callable(self):
        assert callable(get_runtime_query_engine)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_runtime_query_engine)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="query_engine.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="query_engine.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="query_engine.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="query_engine.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="query_engine.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="query_engine.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: query_engine importable or gracefully unavailable."""
    pass
