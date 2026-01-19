from __future__ import annotations
"""
Semantic Memory Module - Sovereign Primary
Provides vector storage, embedding logic, and semantic search capabilities.
"""

try:
    from .embeddings.core_embedder import CoreEmbedder, get_embedding
except ImportError:
    CoreEmbedder = None
    get_embedding = None

try:
    from .store.pinecone_sync import SovereignPineconeStoreAgent
except ImportError:
    SovereignPineconeStoreAgent = None

__all__ = ["SovereignPineconeStoreAgent", "CoreEmbedder", "get_embedding"]
