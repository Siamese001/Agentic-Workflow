from __future__ import annotations
"""
Semantic Memory Module - Sovereign Primary
Provides vector storage, embedding logic, and semantic search capabilities.
"""

from .embedding_logic import CoreEmbedder, get_embedding
from .vector_stores import SovereignPineconeStoreAgent

__all__ = ["SovereignPineconeStoreAgent", "CoreEmbedder", "get_embedding"]
