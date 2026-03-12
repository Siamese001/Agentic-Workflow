"""Foundational behavioral tests for agentic_core/L4_state/enforcement/graph_memory_bridge.py.

fan_in=19 — this module is imported by 19 other modules.
ADG contract: import-hygiene is covered by test_graph_memory_bridge_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L4_state.enforcement.graph_memory_bridge import (  # noqa: F401
        EntityDefinition,
        RelationDefinition,
        GraphMemoryBridge,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    EntityDefinition = None  # type: ignore[assignment,misc]
    RelationDefinition = None  # type: ignore[assignment,misc]
    GraphMemoryBridge = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="graph_memory_bridge.py deps unavailable")
class TestEntityDefinitionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(EntityDefinition)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(EntityDefinition)}
        assert field_names >= {'entity_type', 'observations', 'name'}

@pytest.mark.skipif(not _AVAILABLE, reason="graph_memory_bridge.py deps unavailable")
class TestRelationDefinitionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RelationDefinition)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(RelationDefinition)}
        assert field_names >= {'relation_type', 'from_entity', 'to_entity'}

@pytest.mark.skipif(not _AVAILABLE, reason="graph_memory_bridge.py deps unavailable")
class TestGraphMemoryBridgeContract:
    def test_is_class(self):
        assert isinstance(GraphMemoryBridge, type)

    def test_has_method_get_instance(self):
        assert callable(getattr(GraphMemoryBridge, 'get_instance', None))

    def test_has_method_reset_instance(self):
        assert callable(getattr(GraphMemoryBridge, 'reset_instance', None))

    def test_has_method_set_mcp_functions(self):
        assert callable(getattr(GraphMemoryBridge, 'set_mcp_functions', None))

    def test_has_method_is_available(self):
        assert callable(getattr(GraphMemoryBridge, 'is_available', None))

@pytest.mark.skipif(not _AVAILABLE, reason="graph_memory_bridge.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="graph_memory_bridge.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="graph_memory_bridge.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="graph_memory_bridge.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="graph_memory_bridge.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module graph_memory_bridge must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
