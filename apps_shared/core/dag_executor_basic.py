from __future__ import annotations

import asyncio
from typing import Any, Dict

import pytest

# from archives.legacy_root_folders.core.dag.engine import Graph, Node, Edge, DAGExecutor  # DEPRECATED: Archive import removed to protect archives from validation edits


async def _id_node(ctx: Dict[str, object]) -> Dict[str, object]:
    return dict(ctx)


def _make_cyclic_graph() -> Graph:
    nodes = {
        "a": Node(id="a", fn=_id_node, metadata={}),
        "b": Node(id="b", fn=_id_node, metadata={}),
    }
    edges = [Edge(source="a", target="b"), Edge(source="b", target="a")]
    return Graph(nodes=nodes, edges=edges)


def test_dag_executor_cycle_detection() -> None:
    graph = _make_cyclic_graph()
    executor = DAGExecutor(graph)

    with pytest.raises(RuntimeError):
        asyncio.run(executor.run())






