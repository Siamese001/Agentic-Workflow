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
class GraphEntity:
    """Represents an entity in the knowledge graph."""
    id: str
    name: str
    entity_type: str
    description: str = ""
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


__all__ = ["IGraphStore", "GraphEntity", "GraphCommunity"]
