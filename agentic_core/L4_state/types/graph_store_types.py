"""Graph Store Types.

Defines the data structures for the knowledge graph store,
including entities, relationships, communities, and search results.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


class IGraphStore(ABC):
    """Interface for knowledge graph store implementations."""

    @abstractmethod
    def add_entity(self, entity: GraphEntity) -> None:
        """Add an entity to the graph store."""
        pass

    @abstractmethod
    def get_entity(self, entity_id: str) -> GraphEntity | None:
        """Get an entity by ID."""
        pass

    @abstractmethod
    def search_entities(self, query: str, limit: int = 10) -> list[GraphEntity]:
        """Search for entities."""
        pass

    @abstractmethod
    def get_relationships(
        self, entity_id: str, direction: str = "both"
    ) -> list[GraphRelationship]:
        """Get relationships for an entity.

        Args:
            entity_id: The ID of the entity.
            direction: "outgoing", "incoming", or "both" (default: "both").

        Returns:
            List of relationships connected to the entity.
        """
        pass

    @abstractmethod
    def traverse(
        self,
        start_id: str,
        max_depth: int = 2,
        relation_types: list[str] | None = None,
    ) -> list[GraphPath]:
        """Traverse the graph from a starting entity.

        Args:
            start_id: The ID of the starting entity.
            max_depth: Maximum traversal depth (default: 2).
            relation_types: Optional list of relation types to filter by.

        Returns:
            List of paths discovered during traversal.
        """
        pass

    @abstractmethod
    def get_neighbors(self, entity_id: str, max_hops: int = 1) -> list[GraphEntity]:
        """Get neighboring entities within a specified hop distance.

        Args:
            entity_id: The ID of the entity.
            max_hops: Maximum number of hops (default: 1).

        Returns:
            List of neighboring entities.
        """
        pass

    @abstractmethod
    def get_centrality(self, entity_id: str) -> float:
        """Get the centrality score of an entity.

        Args:
            entity_id: The ID of the entity.

        Returns:
            Centrality score (higher = more central).
        """
        pass

    @abstractmethod
    def find_shortest_path(self, src_id: str, dst_id: str) -> GraphPath | None:
        """Find the shortest path between two entities.

        Args:
            src_id: The ID of the source entity.
            dst_id: The ID of the destination entity.

        Returns:
            GraphPath representing the shortest path, or None if no path exists.
        """
        pass

    @abstractmethod
    def get_subgraph(self, center_id: str, radius: int = 2) -> GraphSubgraph:
        """Extract a subgraph around a center entity.

        Args:
            center_id: The ID of the center entity.
            radius: The radius in hops (default: 2).

        Returns:
            GraphSubgraph containing nodes and relationships within the radius.
        """
        pass

    @abstractmethod
    def detect_communities(self, algorithm: str = "leiden") -> list[GraphCommunity]:
        """Detect communities in the graph.

        Args:
            algorithm: Community detection algorithm (default: "leiden").

        Returns:
            List of detected communities.
        """
        pass


@dataclass
class GraphCommunity:
    """Represents a community in the knowledge graph."""
    id: str
    name: str
    description: str = ""
    entities: list[str] = field(default_factory=list)
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphSubgraph:
    """Represents a subgraph extracted from the knowledge graph."""
    nodes: list[GraphEntity] = field(default_factory=list)
    relationships: list[GraphRelationship] = field(default_factory=list)
    center_id: str = ""
    radius: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphPath:
    """Represents a path through the knowledge graph."""
    nodes: list[GraphEntity] = field(default_factory=list)
    relationships: list[GraphRelationship] = field(default_factory=list)
    cost: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphRelationship:
    """Represents a relationship between entities in the knowledge graph."""
    source_id: str
    target_id: str
    relation_type: str
    edge_kind: str = ""
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEntity:
    """Represents an entity in the knowledge graph."""
    id: str
    name: str
    entity_type: str
    description: str = ""
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


__all__ = ["IGraphStore", "GraphEntity", "GraphCommunity", "GraphRelationship", "GraphPath", "GraphSubgraph"]
