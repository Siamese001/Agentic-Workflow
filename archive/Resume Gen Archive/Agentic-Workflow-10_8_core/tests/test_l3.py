"""Grouped L3 orchestration tests."""
import math

from l3_orchestration import DAGExecutor
from l3_orchestration import DAG, DAGNode
from node_result import NodeResult, NodeStatus
from l3_orchestration import BulletOrchestrator
from l3_orchestration import DraftOrchestrator
from l3_orchestration import GraphOrchestrator
from l3_orchestration import QAOrchestrator
from l3_orchestration import RAGOrchestrator


def test_dag_sequencing_basic():
    sequence = []

    def make_node(label):
        def runner(context):
            sequence.append(label)
            payload = {"path": (context.get("path", []) + [label])}
            return NodeResult(NodeStatus.SUCCESS, payload)

        return runner

    dag = DAG(
        nodes={
            "A": DAGNode(name="A", run=make_node("A")),
            "B": DAGNode(name="B", run=make_node("B")),
            "C": DAGNode(name="C", run=make_node("C")),
        },
        edges={"A": ["B"], "B": ["C"], "C": []},
    )

    context = DAGExecutor().run(dag, {})

    assert sequence == ["A", "B", "C"]
    assert context["path"] == ["A", "B", "C"]


def test_dag_conditional_edges():
    traversed = []

    def start(context):
        traversed.append("start")
        return NodeResult(NodeStatus.SUCCESS, {})

    def conditional(context):
        traversed.append("conditional")
        return NodeResult(NodeStatus.SUCCESS, {"hit": True})

    def default(context):
        traversed.append("default")
        return NodeResult(NodeStatus.SUCCESS, {"hit": False})

    dag = DAG(
        nodes={
            "start": DAGNode(
                name="start",
                run=start,
                condition=lambda ctx: ctx.get("flag", False),
                conditional_edges={"condition_true": ["conditional"]},
            ),
            "conditional": DAGNode(name="conditional", run=conditional),
            "default": DAGNode(name="default", run=default),
        },
        edges={"start": ["default"], "conditional": [], "default": []},
    )

    true_context = DAGExecutor().run(dag, {"flag": True})
    false_context = DAGExecutor().run(dag, {"flag": False})

    assert true_context.get("hit") is True
    assert false_context.get("hit") is False
    assert traversed[0:2] == ["start", "conditional"]


def test_dag_retries_and_fallback():
    attempts = {"unstable": 0}

    def unstable(context):
        attempts["unstable"] += 1
        return NodeResult(NodeStatus.FAILURE, {"attempts": attempts["unstable"]})

    def fallback(context):
        return NodeResult(NodeStatus.SUCCESS, {"recovered": True})

    dag = DAG(
        nodes={
            "unstable": DAGNode(name="unstable", run=unstable, retries=1, fallback_edge="fallback"),
            "fallback": DAGNode(name="fallback", run=fallback),
        },
        edges={"unstable": [], "fallback": []},
    )

    context = DAGExecutor().run(dag, {})

    assert attempts["unstable"] == 2
    assert context.get("recovered") is True


def test_dag_parallel_branches():
    def root(context):
        return NodeResult(NodeStatus.SUCCESS, {"value": "root"})

    def parallel_one(context):
        return NodeResult(NodeStatus.SUCCESS, {"value": "one", "order": ["one"]})

    def parallel_two(context):
        return NodeResult(NodeStatus.SUCCESS, {"value": "two", "order": ["two"]})

    dag = DAG(
        nodes={
            "root": DAGNode(name="root", run=root, parallel=["p1", "p2"]),
            "p1": DAGNode(name="p1", run=parallel_one),
            "p2": DAGNode(name="p2", run=parallel_two),
        },
        edges={"root": [], "p1": [], "p2": []},
    )

    context = DAGExecutor().run(dag, {})

    assert context["value"] == "two"
    assert context["order"] == ["two"]


def test_orchestrators_end_to_end():
    orchestrators = [
        GraphOrchestrator(),
        RAGOrchestrator(),
        DraftOrchestrator(),
        BulletOrchestrator(),
        QAOrchestrator(),
    ]

    for orchestrator in orchestrators:
        result = orchestrator.orchestrate({"objective": "x", "audience": "y"})
        assert result.plan
        assert result.execution_patch
        assert result.safety_patch
        assert result.state
        spans = result.state.get("telemetry", {}).get("spans", [])
        assert isinstance(spans, list)
        for span in spans:
            assert math.isfinite(span.get("duration_ms", 0.0))
"""
Test Suite — Orchestrators v10.8

Responsibilities:
    • Cover orchestration logic across graph, RAG, draft, bullet, and QA orchestrators.
    • Validate intent routing between L1 reasoners and L2 execution agents.
    • Ensure state and safety integration points are respected throughout control flow.

This test file is scaffolded for Priority 0; implementation comes later.
"""
from l3_orchestration import BulletOrchestrator
from l3_orchestration import DraftOrchestrator
from l3_orchestration import QAOrchestrator
from l3_orchestration import RAGOrchestrator


def test_bullet_orchestrator_sequences_calls():
    orchestrator = BulletOrchestrator()
    result = orchestrator.orchestrate({"objective": "share highlights", "deliverables": ["alpha"]})

    assert result.plan["mode"] == "strategy"
    assert result.plan["routing"]["complexity"] == "medium"
    assert result.plan["routing"]["latency_target"] == 2.0
    assert result.plan["routing"]["cost_ceiling"] == 0.02
    assert result.plan["routing"]["risk_level"] == "normal"
    assert result.state["messages"]
    assert "safety_gateway" in result.state


def test_rag_orchestrator_runs_end_to_end():
    orchestrator = RAGOrchestrator()
    result = orchestrator.orchestrate({"objective": "collect"})

    assert result.plan["routing"]["complexity"] == "medium"
    assert result.plan["routing"]["latency_target"] == 2.0
    assert result.plan["routing"]["cost_ceiling"] == 0.02
    assert result.plan["routing"]["risk_level"] == "normal"
    assert result.execution_patch["last_retrieval"]["status"] == "completed"
    assert result.safety_patch["safety_gateway"]["status"] == "allowed"


def test_draft_orchestrator_integrates_safety():
    orchestrator = DraftOrchestrator()
    result = orchestrator.orchestrate({"objective": "compose", "tone": "warm"})

    assert result.plan["mode"] == "drafting"
    assert result.plan["routing"]["complexity"] == "medium"
    assert result.plan["routing"]["latency_target"] == 2.0
    assert result.plan["routing"]["cost_ceiling"] == 0.02
    assert result.plan["routing"]["risk_level"] == "normal"
    assert result.state.get("draft", {}).get("tone") == "warm"
    assert "safety_gateway" in result.state


def test_qa_orchestrator_validates_state():
    orchestrator = QAOrchestrator()
    result = orchestrator.orchestrate({"messages": [{"role": "assistant", "content": "draft"}]})

    assert result.plan["routing"]["complexity"] == "medium"
    assert result.plan["routing"]["latency_target"] == 2.0
    assert result.plan["routing"]["cost_ceiling"] == 0.02
    assert result.plan["routing"]["risk_level"] == "normal"
    assert result.execution_patch["qa_report"]["checks"]
    assert result.state["safety_gateway"]["status"] == "allowed"
"""
Test Suite — End-to-End v10.8

Responsibilities:
    • Provide high-level coverage across all layers in the v10.8 architecture.
    • Validate coordinated flows from reasoning through execution, state, and safety layers.
    • Ensure prompt system integration aligns with orchestration expectations.

This test file is scaffolded for Priority 0; implementation comes later.
"""
from l3_orchestration import BulletOrchestrator
from l3_orchestration import DraftOrchestrator
from l3_orchestration import RAGOrchestrator
from l3_orchestration import QAOrchestrator
from l4_state import StateAdapter


def test_end_to_end_control_flow():
    adapter = StateAdapter()

    rag = RAGOrchestrator(state_adapter=adapter)
    rag_result = rag.orchestrate({"objective": "collect research"})

    draft = DraftOrchestrator(state_adapter=adapter)
    draft_result = draft.orchestrate({"objective": "summarize research", "tone": "neutral"})

    bullets = BulletOrchestrator(state_adapter=adapter)
    bullet_result = bullets.orchestrate({"deliverables": ["summary", "actions"]})

    qa = QAOrchestrator(state_adapter=adapter)
    qa_result = qa.orchestrate(adapter.state)

    assert rag_result.state["last_retrieval"]["status"] == "completed"
    assert "draft" in draft_result.state
    assert bullet_result.state["messages"]
    assert qa_result.state["safety_gateway"]["status"] == "allowed"
