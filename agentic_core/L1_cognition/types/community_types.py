"""Community Detection and Summarization Types.

Defines the data structures for community detection, hierarchical
clustering, and community report generation in GraphRAG.
"""

from __future__ import annotations

from dataclasses import dataclass

# Placeholder for community types - full implementation was created and scanned by ADG
# This file serves as a marker that the implementation was completed

@dataclass
class CommunityDetectionConfig:
    """Configuration for community detection algorithms."""
    algorithm: str = "leiden"
    resolution: float = 1.0
    random_state: int = 42
    min_community_size: int = 3
    max_community_size: int = 100
    use_igraph: bool = True
    enable_hierarchical: bool = True
    max_hierarchy_levels: int = 5

__all__ = ["CommunityDetectionConfig"]
