"""ADG-driven tests for agentic_core/L4_state/enforcement/graph_memory_bridge.py — fan_in=8.

Tests cover the dataclass contracts and GraphMemoryBridge interface without
requiring a live MCP server (resilient mode must work offline).
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L4_state.enforcement.graph_memory_bridge import (
    EntityDefinition,
    RelationDefinition,
)


class TestEntityDefinition:
    def test_instantiation(self):
        e = EntityDefinition(name="AgentX", entity_type="Agent")
        assert e.name == "AgentX"
        assert e.entity_type == "Agent"
        assert e.observations == []

    def test_observations_default_is_list(self):
        e = EntityDefinition(name="A", entity_type="T")
        assert isinstance(e.observations, list)

    def test_observations_provided(self):
        e = EntityDefinition(name="A", entity_type="T", observations=["obs1", "obs2"])
        assert e.observations == ["obs1", "obs2"]

    def test_independent_defaults(self):
        """Each instance must get its own observations list, not a shared default."""
        e1 = EntityDefinition(name="A", entity_type="T")
        e2 = EntityDefinition(name="B", entity_type="T")
        e1.observations.append("x")
        assert e2.observations == []


class TestRelationDefinition:
    def test_instantiation(self):
        r = RelationDefinition(from_entity="A", to_entity="B", relation_type="USES")
        assert r.from_entity == "A"
        assert r.to_entity == "B"
        assert r.relation_type == "USES"

    def test_all_fields_required(self):
        with pytest.raises(TypeError):
            RelationDefinition()  # type: ignore[call-arg]


class TestGraphMemoryBridgeImport:
    """Bridge class must be importable and instantiable in resilient mode."""

    def test_bridge_class_importable(self):
        from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
        assert callable(GraphMemoryBridge)

    def test_bridge_instantiable_without_mcp(self):
        from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
        bridge = GraphMemoryBridge()
        assert bridge is not None

    def test_create_agent_entity_method_exists(self):
        from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
        assert hasattr(GraphMemoryBridge, "create_agent_entity")

    def test_create_mastered_task_relation_method_exists(self):
        from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
        assert hasattr(GraphMemoryBridge, "create_mastered_task_relation")

    def test_get_instance_classmethod_exists(self):
        from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
        assert hasattr(GraphMemoryBridge, "get_instance")

    def test_reset_instance_classmethod_exists(self):
        from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
        assert hasattr(GraphMemoryBridge, "reset_instance")

    def test_relation_constants_defined(self):
        from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
        assert GraphMemoryBridge.RELATION_MASTERED_TASK == "MASTERED_TASK"
        assert GraphMemoryBridge.RELATION_FAILED_TASK == "FAILED_TASK"
        assert GraphMemoryBridge.RELATION_INTERACTS_WITH == "INTERACTS_WITH"

    def test_resilient_mode_create_agent_entity_does_not_raise(self):
        """In resilient mode (no MCP), create_agent_entity must log and not crash."""
        from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
        GraphMemoryBridge.reset_instance()
        bridge = GraphMemoryBridge.get_instance()
        try:
            bridge.create_agent_entity("TestAgent")
        except Exception as exc:
            pytest.fail(f"create_agent_entity raised in resilient mode: {exc}")
        finally:
            GraphMemoryBridge.reset_instance()

    def test_stats_dict_initialized(self):
        from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
        GraphMemoryBridge.reset_instance()
        bridge = GraphMemoryBridge.get_instance()
        assert isinstance(bridge.stats, dict)
        assert "entities_created" in bridge.stats
        GraphMemoryBridge.reset_instance()
