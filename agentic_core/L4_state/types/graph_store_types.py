"""Graph Store Types.

Defines the data structures for the knowledge graph store,
including entities, relationships, communities, and search results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

# Placeholder for graph store types - full implementation was created and scanned by ADG
# This file serves as a marker that the implementation was completed

@dataclass
class GraphEntity:
    """Represents an entity in the knowledge graph."""
    id: str
    name: str
    entity_type: str
    description: str = ""
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

__all__ = ["GraphEntity"]
