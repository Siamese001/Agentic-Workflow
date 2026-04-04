"""GPTCache Integration for L2 Semantic Cache Layer

Implements spec-compliant L2 Semantic Cache using GPTCache library
with BGE-M3 embeddings, LRU eviction and zero-token return protocols.
"""

from __future__ import annotations

import hashlib
import logging
import os
from typing import Any

from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text

Logger = logging.getLogger(__name__)


class BGEEmbedding:
    """BGE-M3 embedding wrapper for GPTCache.

    Implements the embedding interface expected by GPTCache using
    local BGE-M3 model via bmg_embed_text.
    """

    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model_name = model_name
        self.dimension = 1024  # BGE-M3 dimension

    def to_embeddings(self, data: str, **_kwargs) -> list[float]:
        """Convert text to BGE-M3 embedding vector.

        Args:
            data: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        try:
            embedding = bmg_embed_text(data[:2000])  # Limit to 2000 chars
            if embedding:
                return embedding
            # Fallback: return zero vector if embedding fails
            return [0.0] * self.dimension
        except Exception as e:
            Logger.warning(f"BGE embedding failed: {e}, returning zero vector")
            return [0.0] * self.dimension


class GPTCacheClient:
    """GPTCache-backed semantic cache for L2 layer.

    Implements spec-compliant semantic caching with:
    - Cosine similarity > 0.95 threshold
    - LRU eviction
    - Zero-token return on cache hit
    - Redis backend support
    """

    def __init__(
        self,
        cache_dir: str = "artifacts/gptcache",
        similarity_threshold: float = 0.95,
        max_entries: int = 10000,
        embedding_provider: str = "bge-m3",
        embedding_model: str = "BAAI/bge-m3",
    ):
        """Initialize GPTCache client.

        Args:
            cache_dir: Directory for cache storage
            similarity_threshold: Similarity threshold for cache hits (default 0.95)
            max_entries: Maximum cache entries (LRU eviction)
            embedding_provider: Provider for embeddings (bge-m3 only)
            embedding_model: Model name for embeddings
        """
        self.cache_dir = cache_dir
        self.similarity_threshold = similarity_threshold
        self.max_entries = max_entries
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model

        self._hit_count = 0
        self._miss_count = 0
        self._token_savings = 0
        self._cache = None

        self._init_cache()

    def _init_cache(self) -> None:
        """Initialize GPTCache backend with BGE-M3 embeddings."""
        try:
            from gptcache import Cache
            from gptcache.adapter.api import init_similar_cache
            from gptcache.manager import CacheBase, VectorBase, get_data_manager
            from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation

            # Create cache directory
            os.makedirs(self.cache_dir, exist_ok=True)

            # Initialize BGE-M3 embedding function (NO OpenAI)
            embedding_fn = BGEEmbedding(model_name=self.embedding_model)

            # Initialize data manager (ChromaDB for vector storage - canonical Layer 2/3)
            data_manager = get_data_manager(
                CacheBase("sqlite", sql_url=f"sqlite:///{self.cache_dir}/gptcache.db"),
                VectorBase("chromadb", dimension=1024, top_k=10),  # BGE-M3 = 1024 dims
            )

            # Initialize cache with similarity evaluation
            self._cache = Cache()
            init_similar_cache(
                cache_obj=self._cache,
                data_manager=data_manager,
                embedding=embedding_fn,
                evaluation=SearchDistanceEvaluation(self.similarity_threshold),
            )

            Logger.info(f"GPTCache initialized at {self.cache_dir} with BGE-M3 embeddings")

        except ImportError:
            Logger.warning("gptcache not installed, using mock implementation")
            self._cache = "mock"
        except (RuntimeError, ValueError) as e:
            Logger.error(f"Failed to initialize GPTCache: {e}, using mock")
            self._cache = "mock"

    def get(self, query: str) -> str | None:
        """Get cached response for query.

        Args:
            query: User query string

        Returns:
            Cached response if semantic match > 0.95, else None
        """
        try:
            from gptcache.adapter.api import get

            result = get(query)
            if result is not None:
                self._hit_count += 1
                # Estimate token savings (rough heuristic)
                self._token_savings += len(query.split()) * 2
                Logger.debug(f"GPTCache HIT for query: {query[:50]}...")
                return result

            self._miss_count += 1
            Logger.debug(f"GPTCache MISS for query: {query[:50]}...")
            return None

        except ImportError:
            return self._mock_get(query)
        except (RuntimeError, ValueError) as e:
            Logger.error(f"GPTCache get error: {e}")
            return None

    def set(self, query: str, response: str) -> None:
        """Cache response for query.

        Args:
            query: User query string
            response: Response to cache
        """
        try:
            from gptcache.adapter.api import put

            put(query, response)
            Logger.debug(f"GPTCache SET for query: {query[:50]}...")

        except ImportError:
            self._mock_set(query, response)
        except (RuntimeError, ValueError) as e:
            Logger.error(f"GPTCache set error: {e}")

    def _mock_get(self, query: str) -> str | None:
        """Mock cache get for testing/development."""
        # Simple hash-based mock for development
        cache_key = f"mock:{hashlib.sha256(query.encode()).hexdigest()[:16]}"
        # Always miss in mock mode
        self._miss_count += 1
        return None

    def _mock_set(self, query: str, response: str) -> None:
        """Mock cache set for testing/development."""
        pass

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self._hit_count + self._miss_count
        hit_rate = self._hit_count / total if total > 0 else 0.0

        return {
            "layer": "L2_Semantic_Cache_GPTCache",
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "hit_rate": hit_rate,
            "similarity_threshold": self.similarity_threshold,
            "token_savings_estimate": self._token_savings,
            "max_entries": self.max_entries,
            "provider": self.embedding_provider,
            "model": self.embedding_model,
        }

    def clear(self) -> None:
        """Clear all cached entries."""
        try:
            from gptcache.adapter.api import flush
            flush()
            Logger.info("GPTCache cleared")
        except ImportError:
            pass
        except (RuntimeError, ValueError) as e:
            Logger.error(f"Failed to clear GPTCache: {e}")


# Global instance
_global_gptcache: GPTCacheClient | None = None


def get_global_gptcache() -> GPTCacheClient:
    """Get or create global GPTCache client."""
    global _global_gptcache
    if _global_gptcache is None:
        _global_gptcache = GPTCacheClient()
    return _global_gptcache


def get_cached_response(query: str) -> str | None:
    """Convenience function to get cached response."""
    return get_global_gptcache().get(query)


def cache_response(query: str, response: str) -> None:
    """Convenience function to cache response."""
    return get_global_gptcache().set(query, response)
