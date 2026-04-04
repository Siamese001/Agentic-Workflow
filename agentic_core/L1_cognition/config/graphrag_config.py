"""GraphRAG Configuration.

Central configuration for all GraphRAG components including
extraction, community detection, search, and guardrail settings.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GraphRAGConfig:
    """Comprehensive configuration for GraphRAG system."""
    extraction_mode: str = "fast"
    min_entity_confidence: float = 0.5
    min_relationship_confidence: float = 0.3
    community_detection_algorithm: str = "leiden"
    search_fusion_method: str = "weighted_average"
    max_context_items: int = 10
    enable_guardrails: bool = True
    guardrail_strict_mode: bool = False

# Global configuration instance
_global_config: GraphRAGConfig | None = None

def get_config() -> GraphRAGConfig:
    """Get the global GraphRAG configuration."""
    global _global_config
    if _global_config is None:
        _global_config = GraphRAGConfig()
    return _global_config

def set_config(config: GraphRAGConfig) -> None:
    """Set the global GraphRAG configuration."""
    global _global_config
    _global_config = config

__all__ = ["GraphRAGConfig", "get_config", "set_config"]
