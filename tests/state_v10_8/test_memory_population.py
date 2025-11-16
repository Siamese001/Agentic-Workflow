from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack
from core_v10_7 import MainGraphState


def test_memory_patch_populates_and_preserves_existing_state():
    adapter = StateAdapterStack(context=None)
    base_state = MainGraphState()
    base_state.memory.semantic.vector_store_ids = ["existing"]
    base_state.metadata.workflow_id = "wf-123"

    patch = adapter.patch_memory(
        conversation=[{"role": "user", "content": "first"}],
        agent_notes=["note-1"],
        vector_store_ids=["new"],
        tags=["core", "state"],
    )

    updated = adapter.apply_patch(base_state.to_dict(), patch)

    assert updated["memory"]["episodic"]["conversation"][0]["content"] == "first"
    assert updated["memory"]["episodic"]["agent_notes"] == ["note-1"]
    assert updated["memory"]["semantic"]["vector_store_ids"] == ["new"]
    assert updated["memory"]["semantic"]["tags"] == ["core", "state"]
    assert updated["metadata"]["workflow_id"] == "wf-123"
