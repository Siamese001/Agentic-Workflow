import pytest

from agent_orchestration_v10_7 import (
    check_hil_reentry_allowed,
    run_prepare_hil_drafting_reentry,
    run_prepare_hil_strategy_reentry,
)


@pytest.mark.asyncio
async def test_hil_strategy_reentry_respects_loop_budget(workflow_context):
    workflow_context.config.hil_config.max_reentry_loops = 1
    state = {"metadata": {"workflow_id": "wf-hil"}}

    state = await run_prepare_hil_strategy_reentry(state, workflow_context)
    assert state["metadata"]["retries"]["hil_retries"] == 1
    assert state["hil"]["next_step"] == "STRATEGY"
    assert len(state["a2a"]["messages"]) == 1

    state = await run_prepare_hil_strategy_reentry(state, workflow_context)
    assert state["metadata"]["retries"]["hil_retries"] == 2
    assert state["hil"].get("max_reentry_reached") is True
    assert len(state["a2a"]["messages"]) == 1, "HIL loops must stop emitting events once bounded"
    assert check_hil_reentry_allowed(state, workflow_context) == "halt"


@pytest.mark.asyncio
async def test_drafting_reentry_stops_after_bound(workflow_context):
    workflow_context.config.hil_config.max_reentry_loops = 2
    state = {"metadata": {"workflow_id": "wf-hil-draft"}}

    state = await run_prepare_hil_strategy_reentry(state, workflow_context)
    state = await run_prepare_hil_drafting_reentry(state, workflow_context)
    assert state["metadata"]["retries"]["hil_retries"] == 2
    assert check_hil_reentry_allowed(state, workflow_context) == "continue"
    assert len(state["a2a"]["messages"]) == 2

    state = await run_prepare_hil_drafting_reentry(state, workflow_context)
    assert state["metadata"]["retries"]["hil_retries"] == 3
    assert state["hil"].get("max_reentry_reached") is True
    assert check_hil_reentry_allowed(state, workflow_context) == "halt"
    assert len(state["a2a"]["messages"]) == 2
