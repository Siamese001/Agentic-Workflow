import pytest

from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack
from core_v10_7 import MainGraphState, WorkflowPhase


@pytest.mark.state
def test_legal_transition_succeeds():
    adapter = StateAdapterStack(context=None)
    state = MainGraphState()

    updated = adapter.set_phase(state, WorkflowPhase.SAFETY)

    assert updated.phase is WorkflowPhase.SAFETY


@pytest.mark.state
def test_illegal_transition_raises():
    adapter = StateAdapterStack(context=None)
    state = MainGraphState()

    with pytest.raises(ValueError):
        adapter.set_phase(state, WorkflowPhase.QA)
