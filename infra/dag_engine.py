from __future__ import annotations

"""Generic DAG engine for workflow orchestration.

This module is intentionally generic and does not depend on L1–L5, META,
providers, or runtime utilities. It provides a minimal typed surface for
constructing and executing directed acyclic graphs (DAGs).
"""

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Set


NodeFn = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]


@dataclass
class Node:
    """Single DAG node definition.

    Attributes:
        id: Stable identifier for the node within a graph.
        fn: Async callable receiving and returning a dict-like context.
        metadata: Optional, engine-agnostic metadata for callers.
    """

    id: str
    fn: NodeFn
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    """Directed edge between two nodes in a DAG."""

    source: str
    target: str


@dataclass
class Graph:
    """In-memory representation of a directed acyclic graph."""

    nodes: Dict[str, Node]
    edges: List[Edge]

    def successors(self, node_id: str) -> List[Node]:
        return [self.nodes[e.target] for e in self.edges if e.source == node_id]

    def predecessors(self, node_id: str) -> List[Node]:
        return [self.nodes[e.source] for e in self.edges if e.target == node_id]


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

    async def run(self, start_nodes: Optional[Iterable[str]] = None, ctx: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
