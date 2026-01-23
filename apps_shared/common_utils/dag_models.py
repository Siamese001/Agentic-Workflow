import asyncio

# from archives.legacy_root_folders.core.dag.engine import Graph, Node, Edge, DAGExecutor  # DEPRECATED: Archive import removed to protect archives from validation edits


async def _noop_node(ctx: dict[str, object]) -> dict[str, object]:
    ctx = dict(ctx)
    ctx.setdefault("steps", []).append("noop")
    return ctx


async def _set_value(ctx: dict[str, object]) -> dict[str, object]:
    ctx = dict(ctx)
    ctx["value"] = 42
    return ctx


def test_graph_successors_and_predecessors() -> None:
    """Test graph successor and predecessor relationships."""
    nodes = {
        "a": Node(id="a", fn=_noop_node, metadata={}),
        "b": Node(id="b", fn=_set_value, metadata={}),
    }
    edges = [Edge(source="a", target="b")]
    graph = Graph(nodes=nodes, edges=edges)

    succ = [n.id for n in graph.successors("a")]
    preds = [n.id for n in graph.predecessors("b")]

    assert succ == ["b"]
    assert preds == ["a"]


def test_dag_executor_linear_graph() -> None:
    """Test DAG executor with linear graph structure."""
    nodes = {
        "a": Node(id="a", fn=_noop_node, metadata={}),
        "b": Node(id="b", fn=_set_value, metadata={}),
    }
    edges = [Edge(source="a", target="b")]
    graph = Graph(nodes=nodes, edges=edges)

    executor = DAGExecutor(graph)
    result = asyncio.run(executor.run())

    assert result.get("value") == 42
    assert result.get("steps") == ["noop"]
