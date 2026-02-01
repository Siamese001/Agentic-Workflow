"""
Meta-Learning Module - L1 Cognition Layer

Provides Meta-Learning capabilities for the Sovereign Architecture:
- MetaLearningClient: Unified Redis/Pinecone wrapper for healing pattern memory
- HealingMemoryEmbedder: Convert violation signatures to embeddings
- CacheStrategyManager: TTL and similarity threshold guardrails
- DomainContextManager: Handle apps_* domain-specific contexts

[PHASE 1] Core Infrastructure Implementation
"""

from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
    MetaLearningClient,
    get_meta_learning_client,
)
from agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder import (
    HealingMemoryEmbedder,
)
from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
    CacheStrategyManager,
)

__all__ = [
    "MetaLearningClient",
    "get_meta_learning_client",
    "HealingMemoryEmbedder",
    "CacheStrategyManager",
]
