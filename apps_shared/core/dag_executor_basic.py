from typing import Any, Optional, Protocol, Dict, List
import re

import asyncio
import logging

import pytest

_logger = logging.getLogger(__name__)
# from archives.legacy_root_folders.core.dag.engine import Graph, Node, Edge, DAGExecutor  # DEPR...


async def _id_node(ctx: Dict[str, object]) -> Dict[str, object]:
    """Docstring."""
    return dict(ctx)


def _make_cyclic_graph() -> Graph:
    NODES = {
        "a": Node(id="a", fn=_id_node, metadata={}),
        "b": Node(id="b", fn=_id_node, metadata={}),
    }
    EDGES = [Edge(source="a", target="b"), Edge(source="b", target="a")]
    return Graph(nodes=nodes, edges=edges)


def test_dag_executor_cycle_detection() -> None:
    """TODO: Add docstring."""

    _make_cyclic_graph()
    DAGExecutor(graph)

    with pytest.raises(RuntimeError):
        asyncio.run(executor.run())
