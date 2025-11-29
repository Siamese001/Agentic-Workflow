#!/usr/bin/env python3
"""
Dependency Resolver
Section 4: DAG Orchestration - Resolves and manages node dependencies
"""

from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from .dag_types import NodeStatus, DependencyType

logger = logging.getLogger(__name__)

class DependencyStatus(str, Enum):
    """Dependency status enumeration"""
    UNSATISFIED = "unsatisfied"
    SATISFIED = "satisfied"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class DependencyInfo:
    """Information about a dependency"""
    node_id: str
    dependency_id: str
    dependency_type: DependencyType
    status: DependencyStatus
    required: bool = True
    satisfied_at: Optional[str] = None

class DependencyResolver:
    """Resolves and manages dependencies between DAG nodes"""
    
    def __init__(self):
        self.nodes: Dict[str, DAGNode] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        self.reverse_graph: Dict[str, List[str]] = {}
        self.dependency_info: Dict[Tuple[str, str], DependencyInfo] = {}
        
    def add_node(self, node: DAGNode) -> None:
        """Add a node to the dependency resolver"""
        self.nodes[node.config.node_id] = node
        self.dependency_graph[node.config.node_id] = node.dependencies.copy()
        
        # Update reverse graph
        for dep in node.dependencies:
            if dep not in self.reverse_graph:
                self.reverse_graph[dep] = []
            self.reverse_graph[dep].append(node.config.node_id)
        
        # Update dependency info
        for dep in node.dependencies:
            key = (node.config.node_id, dep)
            self.dependency_info[key] = DependencyInfo(
                node_id=node.config.node_id,
                dependency_id=dep,
                dependency_type=node.dependency_types.get(dep, DependencyType.DATA),
                status=DependencyStatus.UNSATISFIED
            )
    
    def remove_node(self, node_id: str) -> None:
        """Remove a node from the dependency resolver"""
        if node_id in self.nodes:
            # Remove from dependency graph
            deps = self.dependency_graph.pop(node_id, [])
            
            # Update reverse graph
            for dep in deps:
                if dep in self.reverse_graph and node_id in self.reverse_graph[dep]:
                    self.reverse_graph[dep].remove(node_id)
            
            # Remove dependent nodes
            for dependent in self.reverse_graph.get(node_id, []):
                if dependent in self.dependency_graph and node_id in self.dependency_graph[dependent]:
                    self.dependency_graph[dependent].remove(node_id)
            
            self.reverse_graph.pop(node_id, None)
            
            # Remove dependency info
            keys_to_remove = [key for key in self.dependency_info.keys() if key[0] == node_id]
            for key in keys_to_remove:
                del self.dependency_info[key]
            
            del self.nodes[node_id]
    
    def get_ready_nodes(self, node_status: Dict[str, NodeStatus]) -> List[str]:
        """Get nodes that are ready for execution"""
        ready_nodes = []
        
        for node_id, node in self.nodes.items():
            if node_status.get(node_id) == NodeStatus.PENDING:
                if self._are_dependencies_satisfied(node_id, node_status):
                    ready_nodes.append(node_id)
        
        return ready_nodes
    
    def get_dependencies(self, node_id: str) -> List[str]:
        """Get dependencies for a node"""
        return self.dependency_graph.get(node_id, []).copy()
    
    def get_dependents(self, node_id: str) -> List[str]:
        """Get nodes that depend on this node"""
        return self.reverse_graph.get(node_id, []).copy()
    
    def are_dependencies_satisfied(self, node_id: str, node_status: Dict[str, NodeStatus]) -> bool:
        """Check if all dependencies for a node are satisfied"""
        return self._are_dependencies_satisfied(node_id, node_status)
    
    def update_dependency_status(self, node_id: str, status: NodeStatus) -> None:
        """Update dependency status based on node execution"""
        for dependent_id in self.get_dependents(node_id):
            key = (dependent_id, node_id)
            if key in self.dependency_info:
                if status == NodeStatus.COMPLETED:
                    self.dependency_info[key].status = DependencyStatus.SATISFIED
                    self.dependency_info[key].satisfied_at = node_id
                elif status == NodeStatus.FAILED and self.dependency_info[key].required:
                    self.dependency_info[key].status = DependencyStatus.FAILED
                elif status == NodeStatus.SKIPPED:
                    self.dependency_info[key].status = DependencyStatus.SKIPPED
    
    def get_execution_order(self) -> List[str]:
        """Get topological order for execution"""
        return self._topological_sort()
    
    def validate_dependencies(self) -> List[str]:
        """Validate dependency configuration and return list of issues"""
        issues = []
        
        # Check for circular dependencies
        if self._has_cycles():
            issues.append("Circular dependencies detected")
        
        # Check for missing dependencies
        for node_id, deps in self.dependency_graph.items():
            for dep in deps:
                if dep not in self.nodes:
                    issues.append(f"Node {node_id} depends on non-existent node {dep}")
        
        # Check for self-dependencies
        for node_id, deps in self.dependency_graph.items():
            if node_id in deps:
                issues.append(f"Node {node_id} depends on itself")
        
        return issues
    
    def get_dependency_summary(self) -> Dict[str, Any]:
        """Get summary of all dependencies"""
        total_dependencies = sum(len(deps) for deps in self.dependency_graph.values())
        total_nodes = len(self.nodes)
        
        dependency_types = {}
        for info in self.dependency_info.values():
            dep_type = info.dependency_type
            dependency_types[dep_type] = dependency_types.get(dep_type, 0) + 1
        
        return {
            'total_nodes': total_nodes,
            'total_dependencies': total_dependencies,
            'average_dependencies_per_node': total_dependencies / total_nodes if total_nodes > 0 else 0,
            'dependency_types': dependency_types,
            'nodes_with_no_dependencies': len([node_id for node_id, deps in self.dependency_graph.items() if not deps]),
            'nodes_with_dependencies': len([node_id for node_id, deps in self.dependency_graph.items() if deps])
        }
    
    def get_critical_path(self) -> List[str]:
        """Get critical path (longest dependency chain)"""
        try:
            return self._find_longest_path()
        except Exception as e:
            logger.error(f"Failed to find critical path: {e}")
            return []
    
    def _are_dependencies_satisfied(self, node_id: str, node_status: Dict[str, NodeStatus]) -> bool:
        """Check if all dependencies for a node are satisfied"""
        deps = self.get_dependencies(node_id)
        
        for dep in deps:
            dep_status = node_status.get(dep)
            key = (node_id, dep)
            
            if key in self.dependency_info:
                dep_info = self.dependency_info[key]
                if dep_info.required and dep_status != NodeStatus.COMPLETED:
                    return False
            elif dep_status != NodeStatus.COMPLETED:
                return False
        
        return True
    
    def _topological_sort(self) -> List[str]:
        """Perform topological sort to get execution order"""
        in_degree = {node_id: 0 for node_id in self.nodes}
        
        # Calculate in-degrees
        for node_id in self.nodes:
            for dep in self.get_dependencies(node_id):
                if dep in in_degree:
                    in_degree[node_id] += 1
        
        # Queue of nodes with no dependencies
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node_id = queue.pop(0)
            result.append(node_id)
            
            # Reduce in-degree of dependent nodes
            for dependent in self.get_dependents(node_id):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # Check if topological sort was successful
        if len(result) != len(self.nodes):
            raise ValueError("Circular dependencies detected, cannot determine execution order")
        
        return result
    
    def _has_cycles(self) -> bool:
        """Check if dependency graph has cycles"""
        visited = set()
        rec_stack = set()
        
        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for neighbor in self.get_dependencies(node_id):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in self.nodes:
            if node_id not in visited:
                if has_cycle(node_id):
                    return True
        
        return False
    
    def _find_longest_path(self) -> List[str]:
        """Find longest path in dependency graph"""
        # Use dynamic programming to find longest path
        memo = {}
        
        def dfs(node_id: str) -> Tuple[int, List[str]]:
            if node_id in memo:
                return memo[node_id]
            
            max_length = 0
            best_path = [node_id]
            
            for dependent in self.get_dependents(node_id):
                length, path = dfs(dependent)
                if length + 1 > max_length:
                    max_length = length + 1
                    best_path = [node_id] + path
            
            memo[node_id] = (max_length, best_path)
            return memo[node_id]
        
        # Find longest path starting from any node
        best_overall_path = []
        max_overall_length = 0
        
        for node_id in self.nodes:
            length, path = dfs(node_id)
            if length > max_overall_length:
                max_overall_length = length
                best_overall_path = path
        
        return best_overall_path

# Utility functions for dependency resolution
def create_dependency_resolver(nodes: List[DAGNode]) -> DependencyResolver:
    """Create a dependency resolver from a list of nodes"""
    resolver = DependencyResolver()
    for node in nodes:
        resolver.add_node(node)
    return resolver

def validate_dag_dependencies(nodes: List[DAGNode]) -> List[str]:
    """Validate dependencies for a list of nodes"""
    resolver = create_dependency_resolver(nodes)
    return resolver.validate_dependencies()

# Re-export components
__all__ = [
    'DependencyResolver', 'DependencyInfo', 'DependencyStatus',
    'create_dependency_resolver', 'validate_dag_dependencies'
]





