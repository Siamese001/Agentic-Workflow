import asyncio
from types import SimpleNamespace

import pytest

import agent_orchestration_v10_7 as orchestration
from agent_orchestration_v10_7 import add_node_with_policies, get_timeout_decorator
from core_v10_7 import WorkflowTimeoutError


class DummyWorkflow:
    def __init__(self) -> None:
        self.nodes = {}

    def add_node(self, name, func):
        self.nodes[name] = func


@pytest.mark.asyncio
async def test_add_node_with_policies_invokes_mcp_and_robustness(monkeypatch):
    workflow = DummyWorkflow()
    workflow_context = SimpleNamespace()
    workflow_context.wrap_mcp_nodes = True

    class DummyRobustness:
        def __init__(self) -> None:
            self.stage = None

        async def run_with_resilience(self, stage, operation):
            self.stage = stage
            return await operation()

    robustness_stack = DummyRobustness()
    monkeypatch.setattr(
        orchestration,
        "_get_robustness_stack",
        lambda ctx: robustness_stack,
    )

    mcp_invoked = {"flag": False}

    def tracking_wrap_mcp(func=None, *, force=False):
        if func is None:
            return lambda inner: tracking_wrap_mcp(inner, force=force)

        async def wrapper(*args, **kwargs):
            mcp_invoked["flag"] = True
            return await func(*args, **kwargs)

        return wrapper

    monkeypatch.setattr(orchestration, "wrap_mcp", tracking_wrap_mcp)

    async def sample_node(state, workflow_context):
        return {"ok": True}

    add_node_with_policies(
        workflow,
        "dummy_node",
        sample_node,
        workflow_context,
        timeout_wrapper=get_timeout_decorator(1),
    )

    result = await workflow.nodes["dummy_node"]({})

    assert result == {"ok": True}
    assert robustness_stack.stage == "dummy_node"
    assert mcp_invoked["flag"] is True


@pytest.mark.asyncio
async def test_add_node_with_policies_enforces_timeout():
    workflow = DummyWorkflow()
    workflow_context = SimpleNamespace()

    async def slow_node(state, workflow_context):
        await asyncio.sleep(0.2)
        return {"slow": True}

    add_node_with_policies(
        workflow,
        "slow_node",
        slow_node,
        workflow_context,
        timeout_wrapper=get_timeout_decorator(0.05),
        enable_robustness=False,
        enable_mcp=False,
    )

    with pytest.raises(WorkflowTimeoutError):
        await workflow.nodes["slow_node"]({})
