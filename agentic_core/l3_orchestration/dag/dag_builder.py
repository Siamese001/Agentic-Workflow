"""
DAG Builder Implementation for Orchestration
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from .node_types.plan_node import PlanNode, NodeStatus


@dataclass
class DAGMetadata:
    """Metadata for the DAG"""
    name: str
    description: str
    version: str = "1.0"
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


class DAGBuilder:
    """Builder for creating and managing execution DAGs"""

    def __init__(self, name: str, description: str = ""):
        self.metadata = DAGMetadata(name=name, description=description)
        self.nodes: Dict[str, PlanNode] = {}
        self.edges: List[tuple] = []  # List of (from_node, to_node) tuples
        self.execution_history: List[Dict[str, Any]] = []

    def add_node(self, node: PlanNode) -> 'DAGBuilder':
        """Add a node to the DAG"""
        if node.node_id in self.nodes:
            raise ValueError(f"Node with ID '{node.node_id}' already exists")

        self.nodes[node.node_id] = node
        self.metadata.updated_at = datetime.now()
        return self

    def remove_node(self, node_id: str) -> 'DAGBuilder':
        """Remove a node from the DAG"""
        if node_id not in self.nodes:
            raise ValueError(f"Node with ID '{node_id}' does not exist")

        # Remove any edges involving this node
        self.edges = [(f, t) for f, t in self.edges if f != node_id and t != node_id]

        # Remove dependencies from other nodes
        for node in self.nodes.values():
            node.remove_dependency(node_id)

        del self.nodes[node_id]
        self.metadata.updated_at = datetime.now()
        return self

    def add_edge(self, from_node: str, to_node: str) -> 'DAGBuilder':
        """Add an edge (dependency) between nodes"""
        if from_node not in self.nodes:
            raise ValueError(f"Source node '{from_node}' does not exist")
        if to_node not in self.nodes:
            raise ValueError(f"Target node '{to_node}' does not exist")

        # Check for circular dependency
        if self._would_create_cycle(from_node, to_node):
            raise ValueError(f"Adding edge {from_node} -> {to_node} would create a cycle")

        self.edges.append((from_node, to_node))
        self.nodes[to_node].add_dependency(from_node)
        self.metadata.updated_at = datetime.now()
        return self

    def remove_edge(self, from_node: str, to_node: str) -> 'DAGBuilder':
        """Remove an edge between nodes"""
        if (from_node, to_node) in self.edges:
            self.edges.remove((from_node, to_node))
            self.nodes[to_node].remove_dependency(from_node)
            self.metadata.updated_at = datetime.now()
        return self

    def _would_create_cycle(self, from_node: str, to_node: str) -> bool:
        """Check if adding an edge would create a cycle"""
        # Simple DFS to check for cycles
        visited = set()
        stack = [to_node]

        while stack:
            current = stack.pop()
            if current == from_node:
                return True
            if current in visited:
                continue
            visited.add(current)

            # Add all nodes that depend on current
            for edge_from, edge_to in self.edges:
                if edge_from == current:
                    stack.append(edge_to)

        return False

    def get_ready_nodes(self) -> List[PlanNode]:
        """Get nodes that are ready to execute"""
        completed_nodes = [
            node_id for node_id, node in self.nodes.items()
            if node.status == NodeStatus.COMPLETED
        ]

        ready_nodes = [
            node for node in self.nodes.values()
            if node.is_ready(completed_nodes)
        ]

        return ready_nodes

    def get_execution_order(self) -> List[List[str]]:
        """Get topological execution order (layers of nodes that can run in parallel)"""
        if not self.nodes:
            return []

        # Kahn's algorithm for topological sorting
        in_degree = {node_id: 0 for node_id in self.nodes}
        for from_node, to_node in self.edges:
            in_degree[to_node] += 1

        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        execution_order = []

        while queue:
            current_layer = queue.copy()
            queue.clear()
            execution_order.append(current_layer)

            for node_id in current_layer:
                for from_node, to_node in self.edges:
                    if from_node == node_id:
                        in_degree[to_node] -= 1
                        if in_degree[to_node] == 0:
                            queue.append(to_node)

        # Check if there's a cycle
        if len(execution_order[-1]) != len([n for n in in_degree.values() if n == 0]):
            raise ValueError("DAG contains cycles")

        return execution_order

    def validate(self) -> Dict[str, Any]:
        """Validate the DAG structure"""
        issues = []
        warnings = []

        # Check for empty DAG
        if not self.nodes:
            warnings.append("DAG has no nodes")

        # Check for isolated nodes
        connected_nodes = set()
        for from_node, to_node in self.edges:
            connected_nodes.add(from_node)
            connected_nodes.add(to_node)

        isolated_nodes = set(self.nodes.keys()) - connected_nodes
        if isolated_nodes:
            warnings.append(f"Isolated nodes: {list(isolated_nodes)}")

        # Check for cycles
        try:
            self.get_execution_order()
        except ValueError as e:
            issues.append(str(e))

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges)
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert DAG to dictionary representation"""
        return {
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "version": self.metadata.version,
                "created_at": self.metadata.created_at.isoformat(),
                "updated_at": self.metadata.updated_at.isoformat()
            },
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "edges": self.edges,
            "validation": self.validate()
        }

    def __str__(self):
        return f"DAGBuilder(name='{self.metadata.name}', nodes={len(self.nodes)}, edges={len(self.edges)})"

    def __repr__(self):
        return self.__str__()
