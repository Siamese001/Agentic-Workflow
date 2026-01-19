"""
Dependency Graph tool for L2 Execution.

Provides dependency graph analysis utilities.
"""
from typing import Any, Dict, List, Set, Optional
import logging

logger = logging.getLogger(__name__)


class DependencyGraph:
    """Tool for analyzing dependency graphs."""
    
    def __init__(self):
        self._nodes: Set[str] = set()
        self._edges: Dict[str, Set[str]] = {}
    
    def add_node(self, node: str) -> None:
        """Add a node to the graph."""
        self._nodes.add(node)
        if node not in self._edges:
            self._edges[node] = set()
    
    def add_edge(self, from_node: str, to_node: str) -> None:
        """Add a directed edge from one node to another."""
        self.add_node(from_node)
        self.add_node(to_node)
        self._edges[from_node].add(to_node)
    
    def get_dependencies(self, node: str) -> Set[str]:
        """Get direct dependencies of a node."""
        return self._edges.get(node, set()).copy()
    
    def get_all_dependencies(self, node: str, visited: Optional[Set[str]] = None) -> Set[str]:
        """Get all transitive dependencies of a node."""
        if visited is None:
            visited = set()
        if node in visited:
            return set()
        visited.add(node)
        
        deps = self.get_dependencies(node)
        all_deps = deps.copy()
        for dep in deps:
            all_deps.update(self.get_all_dependencies(dep, visited))
        return all_deps
    
    def has_cycle(self) -> bool:
        """Check if the graph has a cycle."""
        visited = set()
        rec_stack = set()
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self._edges.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False
        
        for node in self._nodes:
            if node not in visited:
                if dfs(node):
                    return True
        return False
    
    def topological_sort(self) -> List[str]:
        """Return nodes in topological order."""
        visited = set()
        result = []
        
        def dfs(node: str):
            if node in visited:
                return
            visited.add(node)
            for neighbor in self._edges.get(node, set()):
                dfs(neighbor)
            result.append(node)
        
        for node in self._nodes:
            dfs(node)
        return result[::-1]


__all__ = ['DependencyGraph']
