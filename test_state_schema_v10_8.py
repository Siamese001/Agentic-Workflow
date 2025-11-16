"""
Test Suite — State Schema v10.8

Validates the default shape and backward compatibility of the state
representation, ensuring new world-model fields coexist with existing
structures.
"""

from l4_state_adapter import StateAdapter
from utils_types import StatePatch


def test_state_schema_defaults_include_world_and_metadata():
    adapter = StateAdapter()
    state = adapter.state

    assert isinstance(state.get("messages"), list)
    assert isinstance(state.get("rag_history"), list)
    assert isinstance(state.get("summary"), str)
    assert isinstance(state.get("world"), list)
    assert isinstance(state.get("session"), dict)
    assert isinstance(state.get("metadata"), dict)
    assert isinstance(state.get("phase"), str)


def test_state_schema_backward_compatibility_with_message_patch():
    adapter = StateAdapter()
    patch = StatePatch({"messages": [{"role": "user", "content": "hello"}]})

    state = adapter.apply_patch(patch)

    assert state["messages"][-1]["content"] == "hello"
    assert "world" in state and isinstance(state["world"], list)
    assert "session" in state and isinstance(state["session"], dict)
    assert "metadata" in state and isinstance(state["metadata"], dict)
