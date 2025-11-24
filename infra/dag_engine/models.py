from __future__ import annotations

"""DAG engine models for workflow orchestration.

This module is intentionally generic and does not depend on L1–L5, META,
providers, or runtime utilities. It provides a minimal typed surface for
constructing directed acyclic graphs (DAGs).
"""

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List


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



