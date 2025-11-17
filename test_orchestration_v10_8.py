import math

from dag_executor import DAGExecutor
from dag_spec import DAG, DAGNode
from node_result import NodeResult, NodeStatus
from l3_bullet_orchestrator import BulletOrchestrator
from l3_draft_orchestrator import DraftOrchestrator
from l3_graph_orchestrator import GraphOrchestrator
from l3_qa_orchestrator import QAOrchestrator
from l3_rag_orchestrator import RAGOrchestrator


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
