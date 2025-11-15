"""Tests for StateAdapterStack patch semantics."""
from __future__ import annotations

from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack


def test_build_a2a_message_patch_does_not_mutate_state():
    adapter = StateAdapterStack(None)
    base_state = {"a2a": {"messages": [{"sender": "alpha"}]}}
    patch = adapter.build_a2a_message_patch(
        sender="TestOrchestrator",
        message_type="PLAN",
        payload={"hello": "world"},
    )
    updated = adapter.apply_patch(base_state, patch)
    assert len(updated["a2a"]["messages"]) == 2
    assert len(base_state["a2a"]["messages"]) == 1
    assert updated["a2a"]["messages"][-1]["message_type"] == "PLAN"


def test_apply_patch_appends_from_empty_state():
    adapter = StateAdapterStack(None)
    base_state = {}
    patch = adapter.build_a2a_message_patch(
        sender="DraftOrchestratorStack",
        message_type="COMPLETE",
        payload={"workflow_id": "wf-1"},
    )
    updated = adapter.apply_patch(base_state, patch)
    assert "a2a" in updated
    assert len(updated["a2a"]["messages"]) == 1
    assert updated["a2a"]["messages"][0]["payload"]["workflow_id"] == "wf-1"
    assert base_state == {}
