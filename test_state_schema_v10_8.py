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

    expected_keys = {"messages", "rag_history", "summary", "world", "session", "metadata", "phase"}
    assert expected_keys.issubset(state.keys())

    assert isinstance(state.get("messages"), list)
    assert isinstance(state.get("rag_history"), list)
    assert isinstance(state.get("summary"), str)
    assert isinstance(state.get("world"), list)
    assert isinstance(state.get("session"), dict)
    assert isinstance(state.get("metadata"), dict)
    assert isinstance(state.get("phase"), str)


def test_apply_patch_preserves_default_fields_when_not_patched():
    adapter = StateAdapter()
    base_state = adapter.state

    patch = StatePatch({
        "summary": "updated summary",
        "messages": [{"role": "user", "content": "hello"}],
    })

    updated_state = adapter.apply_patch(patch)

    expected_keys = {"messages", "rag_history", "summary", "world", "session", "metadata", "phase"}
    assert expected_keys.issubset(updated_state.keys())

    assert updated_state["summary"] == "updated summary"
    assert updated_state["messages"][-1]["content"] == "hello"

    assert updated_state["rag_history"] == base_state["rag_history"]
    assert updated_state["world"] == base_state["world"]
    assert updated_state["session"] == base_state["session"]
    assert updated_state["metadata"] == base_state["metadata"]
    assert updated_state["phase"] == base_state["phase"]


def test_apply_patch_retains_defaults_for_new_fields():
    adapter = StateAdapter()

    patch = StatePatch({"rag_history": [{"query": "foo", "context": []}]})
    updated_state = adapter.apply_patch(patch)

    assert updated_state["rag_history"][-1]["query"] == "foo"
    assert updated_state["world"] == []
    assert updated_state["session"] == {}
    assert updated_state["metadata"] == {}
