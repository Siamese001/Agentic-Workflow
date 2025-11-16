import pytest

import stacks_v10_8.draft_orchestration as orchestrator_module
from agent_stacks_v10_8.drafting_execution_stack import DraftingExecutionStack


class _DummyDraftOrchestrator:
    calls = []

    def __init__(self, context, debug_mode=False):
        self.context = context
        self.debug_mode = debug_mode

    async def run_async(self, state, workflow_id, state_snapshot=None):
        self.__class__.calls.append((state, workflow_id, state_snapshot))
        return {"draft": {"sections": {"summary": {"draft": "updated"}}}}


@pytest.mark.asyncio
async def test_run_from_state_async_routes_through_orchestrator(monkeypatch, workflow_context):
    monkeypatch.setattr(
        orchestrator_module, "DraftOrchestratorStack", _DummyDraftOrchestrator
    )
    _DummyDraftOrchestrator.calls.clear()

    stack = DraftingExecutionStack(workflow_context)
    state = {"metadata": {"workflow_id": "wf-draft"}}

    patch = await stack.run_from_state_async(state, "wf-draft")

    assert patch["draft"]["sections"]["summary"]["draft"] == "updated"
    assert _DummyDraftOrchestrator.calls, "orchestrator should receive the state"
    routed_state, routed_workflow_id, snapshot = _DummyDraftOrchestrator.calls[-1]
    assert routed_state is state
    assert snapshot is state
    assert routed_workflow_id == "wf-draft"
