"""
DAG models for résumé processing workflow orchestration.

Provides core data structures for comprehensive résumé enhancement directed acyclic graphs.
"""

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List


NodeFn = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]


@dataclass
class Node:
    """
    Represents DAG node for résumé processing workflow execution.

    Defines executable units within comprehensive résumé enhancement orchestration.
    """
    id: str
    fn: NodeFn
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    """
    Represents directed edge in résumé processing DAGs.

    Defines execution flow and dependencies for résumé improvement workflows.
    """
    source: str
    target: str


@dataclass
class Graph:
    """
    Represents directed acyclic graph for résumé processing orchestration.

    Enables structured workflow execution for comprehensive résumé enhancement operations.
    """
    nodes: Dict[str, Node]
    edges: List[Edge]

    def successors(self, node_id: str) -> List[Node]:
        """
        Retrieves successor nodes for résumé processing workflow execution.

        Enables proper dependency resolution in résumé improvement DAGs.
        """
        return [self.nodes[e.target] for e in self.edges if e.source == node_id]

    def predecessors(self, node_id: str) -> List[Node]:
        """
        Retrieves predecessor nodes for résumé processing workflow execution.

        Enables proper dependency tracking in résumé improvement DAGs.
        """
        return [self.nodes[e.source] for e in self.edges if e.target == node_id]



