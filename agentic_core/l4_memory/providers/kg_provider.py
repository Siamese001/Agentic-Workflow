"""
Knowledge Graph Provider Module
LEVEL 5 - Knowledge Graph provider for structured memory operations
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
from enum import Enum

class RelationshipType(Enum):
    IS_A = "is_a"
    PART_OF = "part_of"
    RELATED_TO = "related_to"
    WORKS_FOR = "works_for"
    SKILLED_IN = "skilled_in"
    LOCATED_IN = "located_in"
    COLLABORATES_WITH = "collaborates_with"

@dataclass
class KGNode:
    """Represents a node in the knowledge graph"""
    node_id: str
    node_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class KGEdge:
    """Represents an edge in the knowledge graph"""
    edge_id: str
    source_node: str
    target_node: str
    relationship: RelationshipType
    properties: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class KGQueryResult:
    """Result of a knowledge graph query"""
    nodes: List[KGNode]
    edges: List[KGEdge]
    query_time: float
    total_results: int

@dataclass
class KGConfig:
    """Configuration for KG provider"""
    enable_caching: bool = True
    cache_ttl_seconds: int = 1800
    max_query_depth: int = 5
    enable_inference: bool = True
    confidence_threshold: float = 0.7

class KGProvider:
    """Knowledge Graph provider for structured memory operations"""

    def __init__(self, config: KGConfig = None):
        self.config = config or KGConfig()
        self.logger = logging.getLogger(__name__)
        self.nodes: Dict[str, KGNode] = {}
        self.edges: Dict[str, KGEdge] = {}
        self.adjacency_list: Dict[str, List[str]] = {}
        self.query_cache: Dict[str, KGQueryResult] = {}

    async def add_node(self, node: KGNode) -> str:
        """Add a node to the knowledge graph"""
        try:
            self.nodes[node.node_id] = node

            # Initialize adjacency list entry
            if node.node_id not in self.adjacency_list:
                self.adjacency_list[node.node_id] = []

            # Clear cache
            self._clear_query_cache()

            self.logger.info(f"Added node {node.node_id} of type {node.node_type}")
            return node.node_id

        except Exception as e:
            self.logger.error(f"Failed to add node: {str(e)}")
            raise e

    async def add_edge(self, edge: KGEdge) -> str:
        """Add an edge to the knowledge graph"""
        try:
            # Validate nodes exist
            if edge.source_node not in self.nodes or edge.target_node not in self.nodes:
                raise ValueError("Source or target node does not exist")

            self.edges[edge.edge_id] = edge

            # Update adjacency list
            if edge.source_node not in self.adjacency_list:
                self.adjacency_list[edge.source_node] = []
            self.adjacency_list[edge.source_node].append(edge.target_node)

            # Clear cache
            self._clear_query_cache()

            self.logger.info(f"Added edge {edge.edge_id}: {edge.source_node} -> {edge.target_node}")
            return edge.edge_id

        except Exception as e:
            self.logger.error(f"Failed to add edge: {str(e)}")
            raise e

    async def query_nodes(
        self,
        node_type: str = None,
        properties: Dict[str, Any] = None,
        limit: int = 100
    ) -> List[KGNode]:
        """Query nodes based on type and properties"""
        try:
            start_time = datetime.utcnow()

            # Check cache
            cache_key = f"nodes_{node_type}_{str(properties)}_{limit}"
            if self.config.enable_caching and cache_key in self.query_cache:
                cached_result = self.query_cache[cache_key]
                return cached_result.nodes

            results = []

            for node in self.nodes.values():
                # Filter by type
                if node_type and node.node_type != node_type:
                    continue

                # Filter by properties
                if properties:
                    match = True
                    for key, value in properties.items():
                        if key not in node.properties or node.properties[key] != value:
                            match = False
                            break
                    if not match:
                        continue

                results.append(node)

                # Check limit
                if len(results) >= limit:
                    break

            query_time = (datetime.utcnow() - start_time).total_seconds()

            # Cache result
            if self.config.enable_caching:
                cached_result = KGQueryResult(
                    nodes=results,
                    edges=[],
                    query_time=query_time,
                    total_results=len(results)
                )
                self.query_cache[cache_key] = cached_result

            self.logger.info(f"Found {len(results)} nodes in {query_time:.3f}s")
            return results

        except Exception as e:
            self.logger.error(f"Node query failed: {str(e)}")
            raise e

    async def query_neighbors(
        self,
        node_id: str,
        relationship_type: RelationshipType = None,
        max_depth: int = 1
    ) -> KGQueryResult:
        """Query neighboring nodes"""
        try:
            start_time = datetime.utcnow()

            if node_id not in self.nodes:
                return KGQueryResult(nodes=[], edges=[], query_time=0.0, total_results=0)

            visited_nodes = set()
            visited_edges = set()
            result_nodes = []
            result_edges = []

            # BFS traversal
            queue = [(node_id, 0)]

            while queue and len(visited_nodes) < 100:  # Prevent infinite loops
                current_id, depth = queue.pop(0)

                if depth > max_depth or current_id in visited_nodes:
                    continue

                visited_nodes.add(current_id)

                # Get all edges from current node
                for edge in self.edges.values():
                    if edge.source_node == current_id:
                        # Filter by relationship type
                        if relationship_type and edge.relationship != relationship_type:
                            continue

                        if edge.target_node not in visited_nodes:
                            result_nodes.append(self.nodes[edge.target_node])
                            result_edges.append(edge)
                            visited_edges.add(edge.edge_id)
                            queue.append((edge.target_node, depth + 1))

            query_time = (datetime.utcnow() - start_time).total_seconds()

            result = KGQueryResult(
                nodes=result_nodes,
                edges=result_edges,
                query_time=query_time,
                total_results=len(result_nodes)
            )

            self.logger.info(f"Found {len(result_nodes)} neighbors in {query_time:.3f}s")
            return result

        except Exception as e:
            self.logger.error(f"Neighbor query failed: {str(e)}")
            raise e

    async def find_path(
        self,
        source_node: str,
        target_node: str,
        max_depth: int = 5
    ) -> List[str]:
        """Find shortest path between two nodes"""
        try:
            if source_node not in self.nodes or target_node not in self.nodes:
                return []

            # BFS for shortest path
            queue = [(source_node, [source_node])]
            visited = {source_node}

            while queue:
                current, path = queue.pop(0)

                if current == target_node:
                    return path

                if len(path) > max_depth:
                    continue

                # Get neighbors
                if current in self.adjacency_list:
                    for neighbor in self.adjacency_list[current]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append((neighbor, path + [neighbor]))

            return []  # No path found

        except Exception as e:
            self.logger.error(f"Path finding failed: {str(e)}")
            return []

    async def infer_relationships(self, node_id: str) -> List[KGEdge]:
        """Infer new relationships for a node"""
        try:
            if not self.config.enable_inference or node_id not in self.nodes:
                return []

            inferred_edges = []
            node = self.nodes[node_id]

            # Simple inference rules
            if node.node_type == "person":
                # Infer skill relationships from work experience
                if "skills" in node.properties:
                    for skill in node.properties["skills"]:
                        skill_node_id = f"skill_{skill.lower()}"

                        # Create skill node if it doesn't exist
                        if skill_node_id not in self.nodes:
                            skill_node = KGNode(
                                node_id=skill_node_id,
                                node_type="skill",
                                properties={"name": skill}
                            )
                            await self.add_node(skill_node)

                        # Create relationship edge
                        edge_id = f"{node_id}_skilled_in_{skill_node_id}"
                        if edge_id not in self.edges:
                            edge = KGEdge(
                                edge_id=edge_id,
                                source_node=node_id,
                                target_node=skill_node_id,
                                relationship=RelationshipType.SKILLED_IN,
                                weight=0.8
                            )
                            inferred_edges.append(edge)

            return inferred_edges

        except Exception as e:
            self.logger.error(f"Relationship inference failed: {str(e)}")
            return []

    async def update_node(self, node_id: str, updates: Dict[str, Any]) -> bool:
        """Update a node"""
        try:
            if node_id not in self.nodes:
                return False

            node = self.nodes[node_id]
            node.properties.update(updates)
            node.updated_at = datetime.utcnow()

            # Clear cache
            self._clear_query_cache()

            self.logger.info(f"Updated node {node_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update node: {str(e)}")
            return False

    async def delete_node(self, node_id: str) -> bool:
        """Delete a node and its edges"""
        try:
            if node_id not in self.nodes:
                return False

            # Delete node
            del self.nodes[node_id]

            # Delete related edges
            edges_to_delete = []
            for edge_id, edge in self.edges.items():
                if edge.source_node == node_id or edge.target_node == node_id:
                    edges_to_delete.append(edge_id)

            for edge_id in edges_to_delete:
                del self.edges[edge_id]

            # Update adjacency list
            if node_id in self.adjacency_list:
                del self.adjacency_list[node_id]

            # Remove from other adjacency lists
            for neighbors in self.adjacency_list.values():
                if node_id in neighbors:
                    neighbors.remove(node_id)

            # Clear cache
            self._clear_query_cache()

            self.logger.info(f"Deleted node {node_id} and {len(edges_to_delete)} edges")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete node: {str(e)}")
            return False

    def _clear_query_cache(self) -> None:
        """Clear query cache"""
        self.query_cache.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        node_types = {}
        relationship_types = {}

        for node in self.nodes.values():
            node_types[node.node_type] = node_types.get(node.node_type, 0) + 1

        for edge in self.edges.values():
            rel_type = edge.relationship.value
            relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": node_types,
            "relationship_types": relationship_types,
            "cached_queries": len(self.query_cache),
            "config": {
                "enable_caching": self.config.enable_caching,
                "max_query_depth": self.config.max_query_depth,
                "enable_inference": self.config.enable_inference
            }
        }

    def clear_cache(self) -> None:
        """Clear all caches"""
        self.query_cache.clear()
        self.logger.info("Cleared knowledge graph cache")

__all__ = [
    "KGProvider", "KGNode", "KGEdge", "KGQueryResult",
    "KGConfig", "RelationshipType"
]
