from __future__ import annotations

"""DAG executor implementation (flat module).

Provides DAGExecutor compatible with the original infra.dag_engine.DAGExecutor.
"""

from typing import Any, Dict, Iterable, Optional, Set, List

from .dag_models import Graph


class DAGExecutor:
    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    async def run(
        self,
        start_nodes: Optional[Iterable[str]] = None,
        ctx: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if ctx is None:
            ctx = {}

        if start_nodes is None:
            remaining: Set[str] = set(self._graph.nodes.keys())
        else:
            remaining = set(start_nodes)

        completed: Set[str] = set()

        while remaining:
            ready: List[str] = []
            for node_id in list(remaining):
                preds = {e.source for e in self._graph.edges if e.target == node_id}
                if preds.issubset(completed):
                    ready.append(node_id)

            if not ready:
                raise RuntimeError("DAGExecutor detected a cycle or unresolved dependency")

            for node_id in ready:
                node = self._graph.nodes[node_id]
                ctx = await node.fn(ctx)
                completed.add(node_id)
                remaining.remove(node_id)

        return ctx



