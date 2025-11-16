"""
Control-flow DAG specification used by orchestrators.

This module defines the structural components for DAG orchestration
without embedding runtime execution policies. Nodes and edges are
represented with simple data structures plus validation utilities to
ensure the graph is well-formed and acyclic.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Callable, Deque, Dict, List, Optional, Set

from errors_controlflow import DAGValidationError
from node_result import NodeResult


@dataclass
class DAGNode:
    """Structural node definition for DAG orchestration."""

    name: str
    run: Callable[[Dict[str, Any]], NodeResult]
    retry_policy: Optional[Dict[str, Any]] = field(default=None)
    conditional_edges: Optional[Dict[str, List[str]]] = field(default=None)

    def __post_init__(self) -> None:
        if not self.name:
            raise DAGValidationError("DAG nodes require a non-empty name.")


@dataclass
class DAG:
    """A directed acyclic graph of orchestration steps."""

    nodes: Dict[str, DAGNode]
    edges: Dict[str, List[str]]

    def validate(self) -> None:
        """Validate the DAG is well-formed and acyclic."""

        if not self.nodes:
            raise DAGValidationError("DAG must define at least one node.")

        for node_name, node in self.nodes.items():
            if node_name != node.name:
                raise DAGValidationError(
                    f"Node key '{node_name}' does not match node name '{node.name}'."
                )

        for source, targets in self.edges.items():
            if source not in self.nodes:
                raise DAGValidationError(f"Edge source '{source}' is not a defined node.")
            if not isinstance(targets, list):
                raise DAGValidationError(
                    f"Edges for '{source}' must be provided as a list of target names."
                )
            for target in targets:
                if target not in self.nodes:
                    raise DAGValidationError(
                        f"Edge target '{target}' from '{source}' is not a defined node."
                    )

        self._ensure_acyclic()

    def topological_sort(self) -> List[str]:
        """Return a deterministic topological ordering of the DAG nodes."""

        self.validate()
        in_degree = self._calculate_in_degree()

        ready: List[str] = sorted([name for name, degree in in_degree.items() if degree == 0])
        queue: Deque[str] = deque(ready)
        order: List[str] = []

        adjacency = defaultdict(list)
        for source, targets in self.edges.items():
            adjacency[source].extend(targets)

        while queue:
            current = queue.popleft()
            order.append(current)

            for neighbor in sorted(adjacency.get(current, [])):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.nodes):
            raise DAGValidationError("DAG contains cycles; topological sort failed.")

        return order

    def _calculate_in_degree(self) -> Dict[str, int]:
        in_degree: Dict[str, int] = {name: 0 for name in self.nodes}
        for targets in self.edges.values():
            for target in targets:
                in_degree[target] += 1
        return in_degree

    def _ensure_acyclic(self) -> None:
        visited: Set[str] = set()
        recursion_stack: Set[str] = set()

        def visit(node_name: str) -> None:
            if node_name in recursion_stack:
                raise DAGValidationError("Cycle detected in DAG.")
            if node_name in visited:
                return

            visited.add(node_name)
            recursion_stack.add(node_name)

            for neighbor in self.edges.get(node_name, []):
                visit(neighbor)

            recursion_stack.remove(node_name)

        for node_name in self.nodes:
            visit(node_name)
