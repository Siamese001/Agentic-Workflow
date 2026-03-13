"""Global Semantic cache - Unified caching layer for all engines.

This module provides a unified caching layer shared between the Resume and
Outreach engines, ensuring expensive operations are done once and reused
everywhere through semantic similarity matching.
"""

import hashlib
import logging
import time
from collections import OrderedDict
from typing import Any, Callable

from agentic_core.L0_routing.config.path_constants import THRESHOLD

try:
    import numpy as np
except ImportError as _err:
    raise ImportError("numpy is required for this module. Install with: pip install -e '.[infra]'") from _err
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CacheEntry(BaseModel):
    """cache entry with metadata."""

    key_hash: str
    value: Any
    embedding: list[float] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)
    ttl: int = Field(default=3600)
    source_engine: str = Field(default="UNKNOWN")
    hit_count: int = Field(default=0)
    last_accessed: float = Field(default_factory=time.time)

    def is_expired(self) -> bool:
        """Check if entry is expired.

        Returns:
            True if expired
        """
        return time.time() > self.created_at + self.ttl

    def touch(self) -> None:
        """Update last accessed time."""
        self.last_accessed = time.time()
        self.hit_count += 1


class L1MemoryCache:
    """L1 cache - LRU memory cache for exact matches."""

    # guardian: allow-magic-config
    def __init__(self, max_size: int = 1000):
        """Initialize L1 cache.

        Args:
            max_size: Maximum number of entries
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._hits = 0
        self._misses = 0
        logger.debug(f"Initialized L1 cache with max_size={max_size}")

    def get(self, key_hash: str) -> CacheEntry | None:
        """Get entry from cache.

        Args:
            key_hash: Hash of the key

        Returns:
            cache entry if found and not expired
        """
        if key_hash in self.cache:
            entry = self.cache[key_hash]
            if entry.is_expired():
                del self.cache[key_hash]
                self._misses += 1
                return None
            self.cache.move_to_end(key_hash)
            entry.touch()
            self._hits += 1
            return entry
        self._misses += 1
        return None

    def put(self, key_hash: str, entry: CacheEntry) -> None:
        """Put entry in cache.

        Args:
            key_hash: Hash of the key
            entry: cache entry
        """
        if key_hash in self.cache:
            del self.cache[key_hash]
        self.cache[key_hash] = entry
        while len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def clear(self) -> None:
        """Clear all entries."""
        self.cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Statistics dictionary
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
        }


class L2VectorStore:
    """L2 cache - Vector store for semantic matches."""

    # guardian: allow-magic-config
    def __init__(self, max_size: int = 10000):
        """Initialize L2 vector store.

        Args:
            max_size: Maximum number of entries
        """
        self.max_size = max_size
        self.entries: list[CacheEntry] = []
        self.embeddings: np.ndarray = np.array([]).reshape(0, 0)
        self._hits = 0
        self._misses = 0
        logger.debug(f"Initialized L2 vector store with max_size={max_size}")

    def add(self, entry: CacheEntry) -> None:
        """Add entry to vector store.

        Args:
            entry: cache entry with embedding
        """
        if not entry.embedding:
            return
        for i, existing in enumerate(self.entries):
            if existing.key_hash == entry.key_hash:
                self.entries[i] = entry
                if self.embeddings.shape[0] > 0:
                    self.embeddings[i] = np.array(entry.embedding)
                return
        self.entries.append(entry)
        if self.embeddings.shape[0] == 0:
            self.embeddings = np.array([entry.embedding])
        else:
            self.embeddings = np.vstack([self.embeddings, entry.embedding])
        while len(self.entries) > self.max_size:
            self.entries.pop(0)
            self.embeddings = self.embeddings[1:]

    # guardian: allow-magic-config
    def search(
        self, query_embedding: list[float], threshold: float = 0.92, max_results: int = 5
    ) -> list[tuple[CacheEntry, float]]:
        """Search for semantically similar entries.

        Args:
            query_embedding: Query embedding vector
            threshold: Similarity threshold
            max_results: Maximum results to return

        Returns:
            List of (entry, similarity) tuples
        """
        if self.embeddings.shape[0] == 0:
            self._misses += 1
            return []
        query_vec = np.array(query_embedding)
        similarities = np.dot(self.embeddings, query_vec)
        results = []
        for i, similarity in enumerate(similarities):
            if similarity >= threshold:
                entry = self.entries[i]
                if entry.is_expired():
                    continue
                entry.touch()
                results.append((entry, float(similarity)))
        results.sort(key=lambda x: x[1], reverse=True)
        if results:
            self._hits += 1
        else:
            self._misses += 1
        return results[:max_results]

    def clear(self) -> None:
        """Clear all entries."""
        self.entries.clear()
        self.embeddings = np.array([]).reshape(0, 0)
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> dict[str, Any]:
        """Get store statistics.

        Returns:
            Statistics dictionary
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
        return {
            "size": len(self.entries),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "embedding_dim": self.embeddings.shape[1] if self.embeddings.shape[0] > 0 else 0,
        }


class SimpleEmbedder:
    """Simple local embedding generator."""

    def __init__(self, model_name: str = "BAAI/bge-m3"):
        """Initialize embedder.

        Args:
            model_name: Name of sentence transformer model
        """
        self.model_name = model_name
        self._model = None
        self._embedding_dim = 1024
        logger.debug(f"Initialized SimpleEmbedder with model: {model_name}")

    def _load_model(self) -> None:
        """Load the embedding model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded embedding model: {self.model_name}")
            except ImportError:
                logger.warning("sentence_transformers not available, using dummy embeddings")
                self._model = "dummy"

    def embed(self, text: str) -> list[float]:
        """Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        self._load_model()
        if self._model == "dummy":
            hash_obj = hashlib.md5(text.encode())
            hash_hex = hash_obj.hexdigest()
            embedding = []
            for i in range(0, len(hash_hex), 2):
                val = int(hash_hex[i : i + 2], 16) / 255.0 - 0.5
                embedding.append(val)
            while len(embedding) < self._embedding_dim:
                embedding.append(0.0)
            return embedding[: self._embedding_dim]
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()


class GlobalCache:
    """Global semantic cache with L1/L2 storage.

    L1: in-process LRU (exact key hash, O(1))
    L2: delegates to SemanticCacheManager singleton (BGE vector store, Redis working memory)
    """

    _HIVE_NAMESPACE = "GlobalCache"

    # guardian: allow-magic-config
    def __init__(self, l1_size: int = 1000, l2_size: int = 10000, semantic_threshold: float = 0.92):
        """Initialize global cache.

        Args:
            l1_size: L1 cache size
            l2_size: L2 cache size (kept for API compat; L2 is now SSOT-backed)
            semantic_threshold: Semantic similarity threshold
        """
        self.l1 = L1MemoryCache(l1_size)
        self.l2 = L2VectorStore(l2_size)
        self.embedder = SimpleEmbedder()
        self.semantic_threshold = semantic_threshold
        self._hive: Any = None
        self._stats = {"total_requests": 0, "l1_hits": 0, "l2_hits": 0, "total_misses": 0}
        logger.info(
            f"Initialized GlobalCache (L1: {l1_size}, L2: SSOT-backed, threshold: {semantic_threshold})"
        )

    def get_hive_mind(self):
        """Lazy-load SemanticCacheManager singleton for L2 delegation."""
        if self._hive is None:
            try:
                from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

                self._hive = SemanticCacheManager.get_instance()
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.warning(f"[GlobalCache] SemanticCacheManager unavailable, L2 disabled: {e}")
                self._hive = False
        return self._hive if self._hive is not False else None

    def get(self, key: str) -> Any | None:
        """Get value by exact key.

        Args:
            key: Lookup key

        Returns:
            Cached value if found
        """
        self._stats["total_requests"] += 1
        key_hash = self._hash_key(key)
        entry = self.l1.get(key_hash)
        if entry:
            self._stats["l1_hits"] += 1
            return entry.value
        results = self.l2.search(self.embedder.embed(key), threshold=THRESHOLD, max_results=1)
        if results:
            entry, _ = results[0]
            self._stats["l2_hits"] += 1
            self.l1.put(key_hash, entry)
            return entry.value
        self._stats["total_misses"] += 1
        return None

    def get_semantic(
        self, query_text: str, threshold: float | None = None, max_results: int = 1
    ) -> list[Any]:
        """Get values by semantic similarity.

        Checks SemanticCacheManager (SSOT L2) first, then falls back to
        local L2VectorStore for entries stored before SSOT delegation.

        Args:
            query_text: Query text
            threshold: Similarity threshold (uses default if None)
            max_results: Maximum results

        Returns:
            List of cached values
        """
        self._stats["total_requests"] += 1
        if threshold is None:
            threshold = self.semantic_threshold
        hive = self.get_hive_mind()
        if hive is not None:
            try:
                recalled = hive.recall(query_text, self._HIVE_NAMESPACE)
                if recalled is not None:
                    self._stats["l2_hits"] += 1
                    value = recalled.get("value", recalled)
                    return [value] if max_results >= 1 else []
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.debug(f"[GlobalCache] Hive recall failed: {e}")
        query_embedding = self.embedder.embed(query_text)
        results = self.l2.search(query_embedding, threshold, max_results)
        if results:
            self._stats["l2_hits"] += 1
            best_entry, _ = results[0]
            key_hash = self._hash_key(query_text)
            self.l1.put(key_hash, best_entry)
            return [entry.value for entry, _ in results]
        self._stats["total_misses"] += 1
        return []

    def put(
        self,
        key: str,
        value: Any,
        text_for_embedding: str | None = None,
        ttl: int = 3600,
        source_engine: str = "UNKNOWN",
    ) -> None:
        """Put value in cache.

        Stores in L1 LRU and, when text_for_embedding is provided, also
        delegates to SemanticCacheManager.learn() for SSOT L2 persistence.

        Args:
            key: cache key
            value: Value to cache
            text_for_embedding: Text for semantic indexing
            ttl: Time to live in seconds
            source_engine: Source engine identifier
        """
        key_hash = self._hash_key(key)
        embedding = []
        if text_for_embedding:
            embedding = self.embedder.embed(text_for_embedding)
        entry = CacheEntry(
            key_hash=key_hash, value=value, embedding=embedding, ttl=ttl, source_engine=source_engine
        )
        self.l1.put(key_hash, entry)
        if embedding:
            self.l2.add(entry)
        if text_for_embedding:
            hive = self.get_hive_mind()
            if hive is not None:
                try:
                    hive.learn(
                        text_for_embedding,
                        self._HIVE_NAMESPACE,
                        {"value": value, "key": key, "source_engine": source_engine},
                    )
                # guardian: allow-silent-swallow
                except Exception as e:
                    logger.debug(f"[GlobalCache] Hive learn failed: {e}")

    def _hash_key(self, key: str) -> str:
        """Generate hash for key.

        Args:
            key: Key to hash

        Returns:
            Hash string
        """
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def clear(self) -> None:
        """Clear all cache entries."""
        self.l1.clear()
        self.l2.clear()
        self._stats = {"total_requests": 0, "l1_hits": 0, "l2_hits": 0, "total_misses": 0}
        logger.info("Cleared global cache")

    def cleanup_expired(self) -> int:
        """Remove expired entries.

        Returns:
            Number of entries cleaned up
        """
        cleaned = 0
        l1_keys = list(self.l1.cache.keys())
        for key_hash in l1_keys:
            entry = self.l1.cache[key_hash]
            if entry.is_expired():
                del self.l1.cache[key_hash]
                cleaned += 1
        self.l2.entries = [e for e in self.l2.entries if not e.is_expired()]
        if self.l2.entries:
            self.l2.embeddings = np.array([e.embedding for e in self.l2.entries])
        else:
            self.l2.embeddings = np.array([]).reshape(0, 0)
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} expired cache entries")
        return cleaned

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        stats["l1"] = self.l1.get_stats()
        stats["l2"] = self.l2.get_stats()
        if stats["total_requests"] > 0:
            stats["overall_hit_rate"] = (stats["l1_hits"] + stats["l2_hits"]) / stats["total_requests"]
        else:
            stats["overall_hit_rate"] = 0.0
        return stats


_global_cache: GlobalCache | None = None


def get_global_cache() -> GlobalCache:
    """Get global cache instance.

    Returns:
        GlobalCache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = GlobalCache()
    return _global_cache


# guardian: allow-magic-config
def cached(
    key_func: Callable[..., Any] | None = None,
    ttl: int = 3600,
    semantic: bool = False,
    threshold: float = 0.92,
):
    """Decorator for caching function results.

    Args:
        key_func: Function to generate cache key from args
        ttl: Time to live in seconds
        semantic: Use semantic caching
        threshold: Semantic similarity threshold

    Returns:
        Decorated function
    """

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            cache = get_global_cache()
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            if semantic:
                query_text = str(args[0]) if args else key
                results = cache.get_semantic(query_text, threshold=threshold)
                if results:
                    return results[0]
            else:
                result = cache.get(key)
                if result is not None:
                    return result
            result = await func(*args, **kwargs)
            if semantic:
                cache.put(
                    key,
                    result,
                    text_for_embedding=str(args[0]) if args else key,
                    ttl=ttl,
                    source_engine=func.__module__,
                )
            else:
                cache.put(key, result, ttl=ttl, source_engine=func.__module__)
            return result

        return async_wrapper

    return decorator


def cache_get(key: str) -> Any | None:
    """Get value from global cache.

    Args:
        key: cache key

    Returns:
        Cached value
    """
    cache = get_global_cache()
    return cache.get(key)


def cache_put(
    key: str,
    value: Any,
    text_for_embedding: str | None = None,
    ttl: int = 3600,
    source_engine: str = "UNKNOWN",
) -> None:
    """Put value in global cache.

    Args:
        key: cache key
        value: Value to cache
        text_for_embedding: Text for semantic indexing
        ttl: Time to live
        source_engine: Source engine
    """
    cache = get_global_cache()
    cache.put(key, value, text_for_embedding, ttl, source_engine)


def cache_search_semantic(query_text: str, threshold: float | None = None, max_results: int = 1) -> list[Any]:
    """Search cache semantically.

    Args:
        query_text: Query text
        threshold: Similarity threshold
        max_results: Maximum results

    Returns:
        List of cached values
    """
    cache = get_global_cache()
    return cache.get_semantic(query_text, threshold, max_results)
