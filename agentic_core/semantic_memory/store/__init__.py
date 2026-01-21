from __future__ import annotations

"""
Vector Stores Module - Sovereign Primary
Provides vector database implementations for semantic memory operations.
"""

# This package must remain safe to import even when optional providers
# (Pinecone SDK, credentials, etc.) are not available.

try:
    from .pinecone_sync import SovereignPineconeStoreAgent
except Exception:
    SovereignPineconeStoreAgent = None

try:
    from .pinecone_store import PineconeVectorStore
except Exception:
    PineconeVectorStore = None

try:
    from .bm25_store import Bm25Store, get_bm25_store
except Exception:
    Bm25Store = None
    get_bm25_store = None

__all__ = [
    "SovereignPineconeStoreAgent",
    "PineconeVectorStore",
    "Bm25Store",
    "get_bm25_store",
]
