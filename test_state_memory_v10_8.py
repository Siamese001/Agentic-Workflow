"""
Test Suite — State & Memory v10.8

Validates memory budgeting, state validation, and world-model normalization.
"""
from l4_state_adapter import StateAdapter
from state_validation import validate
from utils_types import StatePatch
from world_model_contracts import normalize_world_facts


def test_high_volume_messages_pruned_to_budget():
    adapter = StateAdapter()
    patch = StatePatch({"messages": [{"role": "user", "content": f"m{i}"} for i in range(500)]})

    state = adapter.apply_patch(patch)

    assert len(state["messages"]) == adapter.memory_manager.context_budget.config.max_messages
    assert state["messages"][-1]["content"] == "m499"


def test_validation_flags_missing_keys():
    result = validate({"messages": [], "summary": ""})

    assert "rag_history" in result["missing"]
    assert "world" in result["missing"]
    assert "phase" in result["missing"]


def test_validation_warns_on_inconsistent_fields():
    state = {
        "messages": [],
        "rag_history": [],
        "summary": "",
        "world": [],
        "session": {},
        "metadata": {},
        "phase": "init",
        "phase_metadata": {},
        "draft": "draft text",
        "qa_report": {"issues": []},
    }

    result = validate(state)

    assert any("draft" in warning for warning in result["cross_field_warnings"])
    assert any("qa_report" in warning for warning in result["cross_field_warnings"])


def test_world_model_normalization():
    facts = [
        {"category": "event", "content": "incident", "origin": "user"},
        {"content": 123, "origin": "unknown", "category": "unknown"},
        "string_fact",
    ]

    normalized = normalize_world_facts(facts)

    assert normalized[0] == {"category": "event", "content": "incident", "origin": "user"}
    assert normalized[1]["category"] == "entity"
    assert normalized[1]["origin"] == "system"
    assert normalized[1]["content"] == "123"
    assert normalized[2]["content"] == "string_fact"
