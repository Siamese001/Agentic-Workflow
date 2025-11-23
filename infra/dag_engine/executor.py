from __future__ import annotations

"""DAG executor implementation.

This module provides a minimal async DAGExecutor compatible with the
original infra.dag_engine.DAGExecutor.
"""

from typing import Any, Dict, Iterable, Optional, Set, List

from .models import Graph


class DAGExecutor:
    """Minimal async DAG executor.

    This executor:
        • Assumes the graph is acyclic.
        • Executes nodes whose predecessors have already completed.
        • Propagates a single shared context dict through the graph.

    It does not implement retries, backpressure, or persistence. Higher
    layers (e.g., workflow_graph) can build those behaviors on top.
    """

    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    async def run(
        self,
        start_nodes: Optional[Iterable[str]] = None,
        ctx: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if ctx is None:
            ctx = {}

        # Determine which nodes must be executed.
        if start_nodes is None:
            remaining: Set[str] = set(self._graph.nodes.keys())
        else:
            remaining = set(start_nodes)

        completed: Set[str] = set()

        while remaining:
            # Pick nodes whose predecessors are all completed.
            ready: List[str] = []
            for node_id in list(remaining):
                preds = {e.source for e in self._graph.edges if e.target == node_id}
                if preds.issubset(completed):
                    ready.append(node_id)

            if not ready:
                # There is a cycle or unresolved dependency.
                raise RuntimeError("DAGExecutor detected a cycle or unresolved dependency")

            # Execute ready nodes sequentially for simplicity; higher layers
            # can wrap this in concurrency if desired.
            for node_id in ready:
                node = self._graph.nodes[node_id]
                ctx = await node.fn(ctx)
                completed.add(node_id)
                remaining.remove(node_id)

        return ctx
