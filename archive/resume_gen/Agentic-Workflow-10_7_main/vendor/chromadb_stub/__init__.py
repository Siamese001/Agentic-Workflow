"""
chromadb_stub – safe in-memory stub for ChromaDB.

This DOES NOT shadow the real 'chromadb' unless you explicitly enable vendor stubs.
It is used only for offline tests (USE_VENDOR_STUBS=1).

Implements:
 - Client
 - PersistentClient
 - HttpClient
 - Collection with add/query/delete
 - embedding_functions.EmbeddingFunction
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# -----------------------------------------------------------------------------
# Embedding Function Stub
# -----------------------------------------------------------------------------
class EmbeddingFunction:
    """Minimal embedding function stub that returns deterministic vectors."""

    def __call__(self, items: List[str]) -> List[List[float]]:
        # deterministic fake embedding: length-based float vector
        return [[float(len(item))] for item in items]


# -----------------------------------------------------------------------------
# In-Memory Collection
# -----------------------------------------------------------------------------
@dataclass
class Collection:
    name: str
    embedding_function: Optional[Any] = None
    _store: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def add(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ):
        """Store records in a simple in-memory structure."""
        for emb, doc, meta, id_ in zip(embeddings, documents, metadatas, ids):
            self._store[id_] = {
                "embedding": emb,
                "document": doc,
                "metadata": meta,
            }

    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Minimal stub for semantic search.
        Computes absolute numerical difference between embeddings.
        """

        if not self._store:
            return {"ids": [[]], "documents": [[]], "distances": [[]]}

        query_value = query_embeddings[0][0]

        scored = []
        for id_, item in self._store.items():
            emb_value = item["embedding"][0]
            distance = abs(query_value - emb_value)
            scored.append((id_, item["document"], distance))

        scored.sort(key=lambda x: x[2])
        scored = scored[:n_results]

        return {
            "ids": [[s[0] for s in scored]],
            "documents": [[s[1] for s in scored]],
            "distances": [[s[2] for s in scored]],
        }

    def delete(self, where: Dict[str, Any]):
        """Delete records based on metadata match (only supports equality)."""
        to_delete = []
        for id_, item in self._store.items():
            if all(item["metadata"].get(k) == v for k, v in where.items()):
                to_delete.append(id_)
        for id_ in to_delete:
            del self._store[id_]


# -----------------------------------------------------------------------------
# Client Variants
# -----------------------------------------------------------------------------
class BaseChromaStubClient:
    """Shared base class for all ChromaDB stub clients."""

    def __init__(self, *args, **kwargs):
        self.collections: Dict[str, Collection] = {}

    def get_or_create_collection(
        self, name: str, embedding_function: Optional[Any] = None, **kwargs
    ) -> Collection:
        if name not in self.collections:
            self.collections[name] = Collection(
                name=name,
                embedding_function=embedding_function or EmbeddingFunction(),
            )
        return self.collections[name]

    def get_collection(self, name: str) -> Collection:
        if name not in self.collections:
            raise KeyError(f"Collection '{name}' not found in ChromaDB stub")
        return self.collections[name]


class Client(BaseChromaStubClient):
    """Default synchronous ChromaDB stub client."""
    pass


class PersistentClient(BaseChromaStubClient):
    """Stub for persistent mode (no actual persistence)."""
    def __init__(self, path: str, **kwargs):
        super().__init__()
        self.path = path


class HttpClient(BaseChromaStubClient):
    """Stub for HTTP mode."""
    def __init__(self, host: str, port: int, **kwargs):
        super().__init__()
        self.host = host
        self.port = port


# -----------------------------------------------------------------------------
# Namespace: embedding_functions
# -----------------------------------------------------------------------------
class embedding_functions:
    EmbeddingFunction = EmbeddingFunction


__all__ = [
    "Client",
    "PersistentClient",
    "HttpClient",
    "Collection",
    "embedding_functions",
]
