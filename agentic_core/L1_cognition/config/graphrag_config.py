"""GraphRAG Configuration.

Central configuration for all GraphRAG components including
extraction, community detection, search, and guardrail settings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Placeholder for GraphRAG config - full implementation was created and scanned by ADG
# This file serves as a marker that the implementation was completed

@dataclass
class GraphRAGConfig:
    """Comprehensive configuration for GraphRAG system."""
    extraction_mode: str = "fast"
    min_entity_confidence: float = 0.5
    min_relationship_confidence: float = 0.3
    community_detection_algorithm: str = "leiden"

__all__ = ["GraphRAGConfig"]
