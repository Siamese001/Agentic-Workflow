import copy

import pytest

from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack
from core_v10_7 import MainGraphState


@pytest.fixture
def base_state_dict() -> dict:
    state = MainGraphState()
    state.resume.master_resume = {"summary": "base"}
    state.resume.highlights = ["impact", "quality"]
    state.memory.episodic.conversation = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]
    return state.to_dict()


@pytest.mark.state
def test_apply_patch_merges_without_deleting(base_state_dict):
    adapter = StateAdapterStack(context=None)
    patch = {"resume": {"highlights": ["new"], "skills": ["python"]}}

    updated = adapter.apply_patch(copy.deepcopy(base_state_dict), patch)

    assert updated["resume"]["highlights"] == ["new"]
    assert updated["resume"]["skills"] == ["python"]
    assert updated["resume"]["master_resume"] == {"summary": "base"}
    assert updated["memory"]["episodic"]["conversation"][-1]["content"] == "hi"


@pytest.mark.state
def test_deletion_requires_explicit_flag(base_state_dict):
    adapter = StateAdapterStack(context=None)

    with pytest.raises(ValueError):
        adapter.apply_patch(copy.deepcopy(base_state_dict), {"resume": {"master_resume": None}})

    updated = adapter.apply_patch(
        copy.deepcopy(base_state_dict), {"resume": {"__delete__": True}}
    )

    assert "resume" not in updated
    assert "memory" in updated
