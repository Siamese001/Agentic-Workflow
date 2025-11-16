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
