#!/usr/bin/env python3
"""
KG Traversal Tool
Section 5: Tool Contracts - KG tool family
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class KGTraversalTool:
    """Controlled multi-hop traversal in knowledge graph"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.max_depth = self.config.get("max_depth", 3)
        self.max_nodes = self.config.get("max_nodes", 100)
    
    def traverse_from_node(self, start_node: str, relation_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Traverse KG starting from a node"""
        try:
            # Simulate KG edges
            kg_edges = [
                {"from": "person_1", "to": "company_1", "relation": "works_at"},
                {"from": "person_1", "to": "skill_1", "relation": "has_skill"},
                {"from": "company_1", "to": "industry_1", "relation": "belongs_to"},
                {"from": "skill_1", "to": "tool_1", "relation": "implemented_with"}
            ]
            
            # Filter by relation types if specified
            if relation_types:
                kg_edges = [edge for edge in kg_edges if edge["relation"] in relation_types]
            
            # Perform traversal
            traversal_path = self._perform_traversal(start_node, kg_edges)
            
            logger.info(f"Traversal from {start_node} visited {len(traversal_path)} nodes")
            return traversal_path
            
        except Exception as e:
            logger.error(f"KG traversal failed: {e}")
            return []
    
    def _perform_traversal(self, start_node: str, edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform actual traversal logic"""
        visited = set()
        queue = [(start_node, 0, [])]  # (node, depth, path)
        results = []
        
        while queue and len(results) < self.max_nodes:
            current_node, depth, path = queue.pop(0)
            
            if current_node in visited or depth > self.max_depth:
                continue
            
            visited.add(current_node)
            results.append({
                "node": current_node,
                "depth": depth,
                "path": path + [current_node]
            })
            
            # Find neighbors
            for edge in edges:
                if edge["from"] == current_node:
                    neighbor = edge["to"]
                    if neighbor not in visited:
                        queue.append((neighbor, depth + 1, path + [current_node]))
        
        return results
    
    def find_path(self, start_node: str, end_node: str) -> Optional[List[str]]:
        """Find path between two nodes"""
        try:
            kg_edges = [
                {"from": "person_1", "to": "company_1", "relation": "works_at"},
                {"from": "company_1", "to": "industry_1", "relation": "belongs_to"},
                {"from": "person_1", "to": "skill_1", "relation": "has_skill"}
            ]
            
            # Build adjacency list
            adjacency = {}
            for edge in kg_edges:
                if edge["from"] not in adjacency:
                    adjacency[edge["from"]] = []
                adjacency[edge["from"]].append(edge["to"])
            
            # BFS to find path
            from collections import deque
            queue = deque([(start_node, [start_node])])
            visited = set()
            
            while queue:
                current, path = queue.popleft()
                
                if current == end_node:
                    return path
                
                if current in visited:
                    continue
                
                visited.add(current)
                
                for neighbor in adjacency.get(current, []):
                    if neighbor not in visited:
                        queue.append((neighbor, path + [neighbor]))
            
            return None
            
        except Exception as e:
            logger.error(f"Path finding failed: {e}")
            return None

def create_kg_traversal_tool(config: Optional[Dict[str, Any]] = None) -> KGTraversalTool:
    """Factory function to create KG traversal tool instance"""
    return KGTraversalTool(config)

# Re-export components
__all__ = [
    'KGTraversalTool', 'create_kg_traversal_tool'
]
