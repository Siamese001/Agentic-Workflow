"""Orchestration-level regression tests for state mutation guarantees."""

from __future__ import annotations

import copy

import pytest

from agent_orchestration_v10_7 import run_inject_hil_edit
from core_v10_7 import MainGraphState


@pytest.mark.asyncio
async def test_run_inject_hil_edit_keeps_input_state_immutable(workflow_context):
    typed_state = MainGraphState()
    typed_state.metadata.workflow_id = "wf-immutability"
    typed_state.draft.sections = {"summary": {"draft": "Original summary"}}
    state = typed_state.to_dict()
    state.setdefault("hil", {})["payload"] = "Add new summary"

    baseline = copy.deepcopy(state)
    updated = await run_inject_hil_edit(state, workflow_context)

    assert state == baseline, "Orchestration nodes must not mutate the incoming state"
    assert (
        updated["draft"]["sections"]["summary"]["draft"].startswith("[EDITED BY HUMAN]")
    )
