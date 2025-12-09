import asyncio
from types import SimpleNamespace

import pytest

import agent_orchestration_v10_7 as orchestration
from agent_orchestration_v10_7 import add_node_with_policies
from core_v10_7 import WorkflowTimeoutError
from core_v10_7.models import NodeStatus
from agent_orchestration_v10_7 import node_success
from langgraph.graph import StateGraph, END


class DummyWorkflow:
    def __init__(self) -> None:
        self.nodes = {}
        self.added = []

    def add_node(self, name, func):
        self.nodes[name] = func
        self.added.append(name)


def make_context(*, wrap_mcp_nodes: bool = True, timeout: float = 0.05):
    performance_config = SimpleNamespace(workflow_node_timeout_seconds=timeout)
    config = SimpleNamespace(performance_config=performance_config)
    return SimpleNamespace(config=config, wrap_mcp_nodes=wrap_mcp_nodes)


@pytest.mark.asyncio
async def test_wrapper_applies_timeout(monkeypatch):
    workflow = DummyWorkflow()
    workflow_context = make_context(wrap_mcp_nodes=False, timeout=0.05)

    async def slow_node(state, workflow_context):
        await asyncio.sleep(0.2)
        return node_success("slow_node", {"slow": True})

    # Disable robustness to isolate timeout behavior
    monkeypatch.setattr(
        orchestration,
        "apply_robustness",
        lambda stage_name=None: (lambda fn: fn),
    )

    add_node_with_policies(workflow, "slow_node", slow_node, workflow_context)

    with pytest.raises(WorkflowTimeoutError):
        await workflow.nodes["slow_node"]({})


@pytest.mark.asyncio
async def test_wrapper_applies_robustness(monkeypatch):
    workflow = DummyWorkflow()
    workflow_context = make_context()

    stage_calls = []

    class DummyRobustness:
        async def run_with_resilience(self, stage, operation):
            stage_calls.append(stage)
            return await operation()

    dummy_stack = DummyRobustness()
    monkeypatch.setattr(orchestration, "_get_robustness_stack", lambda ctx: dummy_stack)
    monkeypatch.setattr(orchestration, "wrap_mcp", lambda fn: fn)

    async def sample_node(state, workflow_context):
        return node_success("robust_node", {"ok": True})

    add_node_with_policies(workflow, "robust_node", sample_node, workflow_context)
    result = await workflow.nodes["robust_node"]({})

    assert result["status"] == NodeStatus.SUCCESS.value
    assert result["payload"] == {"ok": True}
    assert stage_calls == ["robust_node"]


@pytest.mark.asyncio
async def test_wrapper_applies_mcp_when_enabled(monkeypatch):
    workflow = DummyWorkflow()
    workflow_context = make_context()

    mcp_called = {"count": 0}

    def tracking_wrap_mcp(fn):
        async def wrapper(*args, **kwargs):
            mcp_called["count"] += 1
            return await fn(*args, **kwargs)

        return wrapper

    monkeypatch.setattr(orchestration, "wrap_mcp", tracking_wrap_mcp)
    monkeypatch.setattr(
        orchestration,
        "apply_robustness",
        lambda stage_name=None: (lambda fn: fn),
    )

    async def sample_node(state, workflow_context):
        return node_success("mcp_node", {"wrapped": True})

    add_node_with_policies(workflow, "mcp_node", sample_node, workflow_context)
    result = await workflow.nodes["mcp_node"]({})

    assert result["status"] == NodeStatus.SUCCESS.value
    assert result["payload"] == {"wrapped": True}
    assert mcp_called["count"] == 1


@pytest.mark.asyncio
async def test_wrapper_supports_opt_out_flags(monkeypatch):
    workflow = DummyWorkflow()
    workflow_context = make_context()

    monkeypatch.setattr(
        orchestration,
        "wrap_mcp",
        lambda fn: pytest.fail("MCP should be opt-out"),
    )
    monkeypatch.setattr(
        orchestration,
        "apply_robustness",
        lambda stage_name=None: (
            lambda fn: pytest.fail("Robustness should be opt-out")
        ),
    )

    async def fast_node(state, workflow_context):
        return node_success("fast_node", {"fast": True})

    add_node_with_policies(
        workflow,
        "fast_node",
        fast_node,
        workflow_context,
        enable_timeout=False,
        enable_robustness=False,
        enable_mcp=False,
    )

    result = await workflow.nodes["fast_node"]({})
    assert result["status"] == NodeStatus.SUCCESS.value
    assert result["payload"] == {"fast": True}


def test_wrapper_preserves_node_name(monkeypatch):
    workflow = DummyWorkflow()
    workflow_context = make_context(wrap_mcp_nodes=False)
    monkeypatch.setattr(orchestration, "wrap_mcp", lambda fn: fn)
    monkeypatch.setattr(
        orchestration,
        "apply_robustness",
        lambda stage_name=None: (lambda fn: fn),
    )

    async def trivial(state, workflow_context):
        return node_success("preserved", state)

    add_node_with_policies(workflow, "preserved", trivial, workflow_context, enable_timeout=False)
    assert workflow.added == ["preserved"]


@pytest.mark.asyncio
async def test_compiled_dag_contains_wrapped_nodes(monkeypatch):
    workflow = StateGraph(dict)
    workflow_context = make_context(timeout=0.01)

    robustness_calls = []
    mcp_calls = []

    def fake_apply_robustness(stage_name):
        def decorator(fn):
            async def wrapper(*args, **kwargs):
                robustness_calls.append(stage_name)
                return await fn(*args, **kwargs)

            return wrapper

        return decorator

    def fake_wrap_mcp(fn):
        async def wrapper(*args, **kwargs):
            mcp_calls.append(True)
            return await fn(*args, **kwargs)

        return wrapper

    monkeypatch.setattr(orchestration, "apply_robustness", fake_apply_robustness)
    monkeypatch.setattr(orchestration, "wrap_mcp", fake_wrap_mcp)

    async def node_a(state, workflow_context):
        state["a"] = True
        return node_success("node_a", state)

    async def node_b(state, workflow_context):
        state["b"] = True
        return node_success("node_b", state)

    add_node_with_policies(workflow, "node_a", node_a, workflow_context)
    add_node_with_policies(workflow, "node_b", node_b, workflow_context)
    workflow.set_entry_point("node_a")
    workflow.add_edge("node_a", "node_b")
    workflow.add_edge("node_b", END)

    compiled = workflow.compile()
    graph = getattr(compiled, "_graph", workflow)

    for node in ("node_a", "node_b"):
        assert node in graph.nodes
        await graph.nodes[node]({})

    assert robustness_calls == ["node_a", "node_b"]
    assert len(mcp_calls) == 2
