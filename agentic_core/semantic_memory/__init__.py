"""
Semantic Memory Module - Sovereign Primary
Provides vector storage, embedding logic, and semantic search capabilities.
"""

from .vector_stores import SovereignPineconeStore
from .embedding_logic import CoreEmbedder, get_embedding

__all__ = ["SovereignPineconeStore", "CoreEmbedder", "get_embedding"]