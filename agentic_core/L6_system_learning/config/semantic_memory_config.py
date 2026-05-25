"""Semantic Memory Configuration — Externalized buffer size defaults.

Centralizes all magic configuration values for semantic memory embedders
to prevent hardcoded constants scattered across the codebase.

Buffer size rationale:
  - Standard embedders (incidents, mutations, healers, preferences, guardrails): 10,000
    Sufficient for typical runtime accumulation without excessive memory overhead.

  - Graph neighborhood embedder: 50,000
    Larger buffer because ADG contains many nodes and we want to capture
    a representative sample of architectural patterns across the codebase.

All values are overridable via embedder __init__ parameters for testing
and specialized use cases.
"""

from __future__ import annotations

# Standard buffer size for most embedders
DEFAULT_EMBEDDER_BUFFER_SIZE: int = 10_000

# Larger buffer for graph neighborhood embedder (more nodes in ADG)
GRAPH_NEIGHBORHOOD_BUFFER_SIZE: int = 50_000

__all__ = [
    "DEFAULT_EMBEDDER_BUFFER_SIZE",
    "GRAPH_NEIGHBORHOOD_BUFFER_SIZE",
]
