import pytest

from stacks_v10_8.rag_execution import RAGExecutionStack


@pytest.mark.asyncio
async def test_run_from_state_async_returns_patch(monkeypatch, workflow_context):
    state = {"metadata": {"workflow_id": "wf-rag"}}
    stack = RAGExecutionStack(workflow_context)

    async def fake_run_async(state_arg, workflow_id_arg):
        assert workflow_id_arg == "wf-rag"
        assert state_arg is state
        return {"resume": {"experience_bullets": ["x"]}, "rag": {"plan": {}, "metadata": {}}}

    monkeypatch.setattr(stack, "run_async", fake_run_async)  # type: ignore[arg-type]
    patch = await stack.run_from_state_async(state, None)

    assert patch["resume"]["experience_bullets"] == ["x"]
