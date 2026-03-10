"""
Vector Memory Store - Unified vector storage for apps_lic and apps_rg.

Provides semantic search and retrieval capabilities using an in-memory
numpy store (BGE-m3, 1024-dim). Pinecone dependency removed.
Phase 2A.2 - Missing Shared Dependencies
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


@dataclass
class VectorMemoryConfig:
    """Configuration for vector memory store."""

    index_name: str
    dimension: int = 1024  # BGE-m3 embedding dimension
    metric: str = "cosine"
    namespace: str | None = None
    top_k: int = 10
    similarity_threshold: float = 0.7


@dataclass
class VectorSearchResult:
    """Result from vector search."""

    id: str
    score: float
    metadata: dict[str, Any]
    text: str | None = None


class VectorMemoryStore:
    """
    Unified vector memory store for semantic search and retrieval.

    Supports both apps_lic and apps_rg with namespace isolation.
    Uses an in-memory numpy store backed by BGE-m3 (1024-dim) embeddings.
    """

    def __init__(self, config: VectorMemoryConfig):
        """
        Initialize vector memory store.

        Args:
            config: Vector memory configuration
        """
        self.config = config
        # namespace -> {id -> {"embedding": list[float], "metadata": dict}}
        self._store: dict[str, dict[str, dict]] = {}
        self._initialized = True

    def _ensure_initialized(self) -> None:
        """Ensure the vector store is initialized (no-op for in-memory store)."""
        pass

    def _namespace_key(self) -> str:
        """Return the active namespace key."""
        return self.config.namespace or "__default__"

    def store(
        self,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
        id: str | None = None,
    ) -> str:
        """
        Store text and embedding in vector memory.

        Args:
            text: Text content to store
            embedding: Vector embedding
            metadata: Optional metadata
            id: Optional custom ID (auto-generated if not provided)

        Returns:
            ID of stored vector
        """
        if id is None:
            id = self._generate_id(text)

        meta = metadata or {}
        meta["text"] = text

        ns = self._namespace_key()
        self._store.setdefault(ns, {})[id] = {"embedding": embedding, "metadata": meta}
        logger.debug(f"Stored vector: {id}")
        return id

    def search(
        self,
        embedding: list[float],
        top_k: int | None = None,
        filter: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """
        Search for similar vectors.

        Args:
            embedding: Query embedding
            top_k: Number of results to return
            filter: Optional metadata filter (keys matched against metadata dict)

        Returns:
            List of search results
        """
        import numpy as np

        k = top_k or self.config.top_k
        ns = self._namespace_key()
        entries = self._store.get(ns, {})

        if not entries:
            return []

        try:
            q = np.array(embedding, dtype=np.float32)
            q_norm = q / (np.linalg.norm(q) + 1e-12)

            scored: list[tuple[float, str, dict]] = []
            for vec_id, item in entries.items():
                if filter and not all(item["metadata"].get(k2) == v for k2, v in filter.items()):
                    continue
                v = np.array(item["embedding"], dtype=np.float32)
                v_norm = v / (np.linalg.norm(v) + 1e-12)
                score = float(np.dot(q_norm, v_norm))
                if score >= self.config.similarity_threshold:
                    scored.append((score, vec_id, item["metadata"]))

            scored.sort(key=lambda x: x[0], reverse=True)
            results = [
                VectorSearchResult(
                    id=vec_id,
                    score=score,
                    metadata=meta,
                    text=meta.get("text"),
                )
                for score, vec_id, meta in scored[:k]
            ]
            logger.debug(f"Found {len(results)} results above threshold")
            return results

        except Exception as e:
            logger.error(f"Failed to search vectors: {e}")
            return []

    def delete(self, ids: list[str]) -> bool:
        """
        Delete vectors by ID.

        Args:
            ids: List of vector IDs to delete

        Returns:
            True if successful
        """
        ns = self._namespace_key()
        ns_store = self._store.get(ns, {})
        for vec_id in ids:
            ns_store.pop(vec_id, None)
        logger.debug(f"Deleted {len(ids)} vectors")
        return True

    def clear_namespace(self) -> bool:
        """
        Clear all vectors in the current namespace.

        Returns:
            True if successful
        """
        ns = self._namespace_key()
        self._store[ns] = {}
        logger.info(f"Cleared namespace: {self.config.namespace}")
        return True

    def _generate_id(self, text: str) -> str:
        """Generate deterministic ID from text."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def get_stats(self) -> dict[str, Any]:
        """
        Get vector store statistics.

        Returns:
            Dictionary with stats
        """
        ns = self._namespace_key()
        ns_count = len(self._store.get(ns, {}))
        total = sum(len(v) for v in self._store.values())
        return {
            "initialized": True,
            "total_vectors": total,
            "namespace_vectors": ns_count,
            "dimension": self.config.dimension,
            "namespaces": list(self._store.keys()),
        }
