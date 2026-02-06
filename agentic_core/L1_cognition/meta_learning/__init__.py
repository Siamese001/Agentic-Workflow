"""
Meta-Learning Module - L1 Cognition Layer

Provides Meta-Learning capabilities for the Sovereign Architecture:
- MetaLearningClient: Unified Redis/Pinecone wrapper for healing pattern memory
- HealingMemoryEmbedder: Convert violation signatures to embeddings
- CacheStrategyManager: TTL and similarity threshold guardrails
- DomainContextManager: Handle domain-specific contexts

V10 Standard: Files organized into engine/, validators/, types/, config/ subfolders.
"""

from agentic_core.L1_cognition.meta_learning.engine.cache_manager import (
    CacheStrategyManager,
)
from agentic_core.L1_cognition.meta_learning.engine.memory_embedder import (
    HealingMemoryEmbedder,
)
from agentic_core.L1_cognition.meta_learning.engine.meta_client import (
    MetaLearningClient,
    get_meta_learning_client,
)

__all__ = [
    "MetaLearningClient",
    "get_meta_learning_client",
    "HealingMemoryEmbedder",
    "CacheStrategyManager",
]
