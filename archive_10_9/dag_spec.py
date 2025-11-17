"""Control-flow DAG specification used by orchestrators."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from errors_controlflow import DAGValidationError
from node_result import NodeResult


@dataclass
class DAGNode:
    """Structural node definition for DAG orchestration."""

    name: str
    run: Callable[[Dict[str, Any]], NodeResult]
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    conditional_edges: Dict[str, List[str]] = field(default_factory=dict)
    retries: int = 0
    fallback_edge: Optional[str] = None
    parallel: List[str] = field(default_factory=list)

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
            for target in targets:
                if target not in self.nodes:
                    raise DAGValidationError(
                        f"Edge target '{target}' from '{source}' is not a defined node."
                    )

    def topological_sort(self) -> List[str]:
        """Return a deterministic topological ordering of the DAG nodes."""

        self.validate()
        in_degree: Dict[str, int] = {name: 0 for name in self.nodes}
        for targets in self.edges.values():
            for target in targets:
                in_degree[target] += 1

        ready = sorted([name for name, degree in in_degree.items() if degree == 0])
        order: List[str] = []

        while ready:
            current = ready.pop(0)
            order.append(current)
            for neighbor in sorted(self.edges.get(current, [])):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    ready.append(neighbor)

        if len(order) != len(self.nodes):
            raise DAGValidationError("DAG contains cycles; topological sort failed.")

        return order
