"""
Vector Memory Store - Unified vector storage for apps_lic and apps_rg.

Provides semantic search and retrieval capabilities using Pinecone.
Phase 2A.2 - Missing Shared Dependencies
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class VectorMemoryConfig:
    """Configuration for vector memory store."""

    index_name: str
    dimension: int = 1536  # OpenAI embedding dimension
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
    """

    def __init__(self, config: VectorMemoryConfig):
        """
        Initialize vector memory store.

        Args:
            config: Vector memory configuration
        """
        self.config = config
        self._client = None
        self._index = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Ensure the vector store is initialized."""
        if self._initialized:
            return

        try:
            from pinecone import Pinecone

            # Initialize Pinecone client
            api_key = self._get_api_key()
            self._client = Pinecone(api_key=api_key)

            # Get or create index
            if self.config.index_name not in self._client.list_indexes().names():
                logger.info(f"Creating Pinecone index: {self.config.index_name}")
                self._client.create_index(
                    name=self.config.index_name,
                    dimension=self.config.dimension,
                    metric=self.config.metric,
                )

            self._index = self._client.Index(self.config.index_name)
            self._initialized = True
            logger.info(f"Vector memory store initialized: {self.config.index_name}")

        except ImportError:
            logger.warning("Pinecone not installed, vector memory disabled")
            self._initialized = False
        except Exception as e:
            logger.error(f"Failed to initialize vector memory: {e}")
            self._initialized = False

    def _get_api_key(self) -> str:
        """Get Pinecone API key from environment."""
        import os

        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        return api_key

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
        self._ensure_initialized()

        if not self._initialized or self._index is None:
            logger.warning("Vector memory not initialized, skipping storage")
            return ""

        # Generate ID if not provided
        if id is None:
            id = self._generate_id(text)

        # Prepare metadata
        meta = metadata or {}
        meta["text"] = text

        # Store in Pinecone
        try:
            self._index.upsert(vectors=[(id, embedding, meta)], namespace=self.config.namespace)
            logger.debug(f"Stored vector: {id}")
            return id
        except Exception as e:
            logger.error(f"Failed to store vector: {e}")
            return ""

    def search(
        self, embedding: list[float], top_k: int | None = None, filter: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """
        Search for similar vectors.

        Args:
            embedding: Query embedding
            top_k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of search results
        """
        self._ensure_initialized()

        if not self._initialized or self._index is None:
            logger.warning("Vector memory not initialized, returning empty results")
            return []

        k = top_k or self.config.top_k

        try:
            response = self._index.query(
                vector=embedding,
                top_k=k,
                namespace=self.config.namespace,
                filter=filter,
                include_metadata=True,
            )

            results = []
            for match in response.matches:
                if match.score >= self.config.similarity_threshold:
                    results.append(
                        VectorSearchResult(
                            id=match.id,
                            score=match.score,
                            metadata=match.metadata,
                            text=match.metadata.get("text"),
                        ),
                    )

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
        self._ensure_initialized()

        if not self._initialized or self._index is None:
            logger.warning("Vector memory not initialized, skipping deletion")
            return False

        try:
            self._index.delete(ids=ids, namespace=self.config.namespace)
            logger.debug(f"Deleted {len(ids)} vectors")
            return True
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            return False

    def clear_namespace(self) -> bool:
        """
        Clear all vectors in the current namespace.

        Returns:
            True if successful
        """
        self._ensure_initialized()

        if not self._initialized or self._index is None:
            logger.warning("Vector memory not initialized, skipping clear")
            return False

        try:
            self._index.delete(delete_all=True, namespace=self.config.namespace)
            logger.info(f"Cleared namespace: {self.config.namespace}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear namespace: {e}")
            return False

    def _generate_id(self, text: str) -> str:
        """Generate deterministic ID from text."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def get_stats(self) -> dict[str, Any]:
        """
        Get vector store statistics.

        Returns:
            Dictionary with stats
        """
        self._ensure_initialized()

        if not self._initialized or self._index is None:
            return {"initialized": False}

        try:
            stats = self._index.describe_index_stats()
            return {
                "initialized": True,
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": stats.namespaces,
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"initialized": True, "error": str(e)}
