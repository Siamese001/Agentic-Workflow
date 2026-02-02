"""
Meta-Learning Module - L1 Cognition Layer

Provides Meta-Learning capabilities for the Sovereign Architecture:
- MetaLearningClient: Unified Redis/Pinecone wrapper for healing pattern memory
- HealingMemoryEmbedder: Convert violation signatures to embeddings
- CacheStrategyManager: TTL and similarity threshold guardrails
- DomainContextManager: Handle apps_* domain-specific contexts

[PHASE 1] Core Infrastructure Implementation
"""

from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
    MetaLearningClient,
    get_meta_learning_client,
)
from agentic_core.L1_cognition.meta_learning.healing_memory_embedder_types import (
    HealingMemoryEmbedder,
)
from agentic_core.L1_cognition.meta_learning.cache_strategy_manager_types import (
    CacheStrategyManager,
)

__all__ = [
    "MetaLearningClient",
    "get_meta_learning_client",
    "HealingMemoryEmbedder",
    "CacheStrategyManager",
]
