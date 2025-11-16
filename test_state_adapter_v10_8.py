"""
Test Suite — State Adapter v10.8

Responsibilities:
    • Validate the L4 state adapter interfaces across orchestrators and memory managers.
    • Ensure deterministic state mutations and compatibility with execution outputs.
    • Confirm integration points for safety and policy annotations at L5.

This test file is scaffolded for Priority 0; implementation comes later.
"""
from l4_state_adapter import StateAdapter
from utils_types import Phase, StatePatch


def test_state_adapter_applies_patch_and_phase():
    adapter = StateAdapter()
    patch = StatePatch({"messages": [{"role": "assistant", "content": "hi"}], "phase": Phase.PLANNING.value})

    state = adapter.apply_patch(patch)
    assert state["messages"][-1]["content"] == "hi"
    assert adapter.state_machine.phase == Phase.PLANNING
    assert state["phase_metadata"]["phase"] == Phase.PLANNING.value


def test_state_adapter_tracks_history_and_metadata_on_phase_changes():
    adapter = StateAdapter()

    planning_state = adapter.apply_patch(StatePatch({"phase": Phase.PLANNING.value}))
    assert planning_state["phase"] == Phase.PLANNING.value
    assert planning_state["phase_metadata"]["phase"] == Phase.PLANNING.value

    executing_state = adapter.apply_patch(StatePatch({"phase": Phase.EXECUTING.value}))
    assert executing_state["phase"] == Phase.EXECUTING.value
    assert executing_state["phase_metadata"]["phase"] == Phase.EXECUTING.value

    serialized = adapter.state_machine.serialize()
    assert serialized["phase"] == Phase.EXECUTING.value
    assert adapter.state_machine.history() == [Phase.INIT.value, Phase.PLANNING.value, Phase.EXECUTING.value]
