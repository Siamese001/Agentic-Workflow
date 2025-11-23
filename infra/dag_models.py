from __future__ import annotations

"""DAG engine models for workflow orchestration (flat module).

Kept separate from infra.dag_engine to allow a thin compatibility shim.
"""

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List


NodeFn = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]


@dataclass
class Node:
    id: str
    fn: NodeFn
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    source: str
    target: str


@dataclass
class Graph:
    nodes: Dict[str, Node]
    edges: List[Edge]

    def successors(self, node_id: str) -> List[Node]:
        return [self.nodes[e.target] for e in self.edges if e.source == node_id]

    def predecessors(self, node_id: str) -> List[Node]:
        return [self.nodes[e.source] for e in self.edges if e.target == node_id]
