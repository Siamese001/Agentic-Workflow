"""Contrastive Semantic cache - SOTA Layer for Instant Response Retrieval.

This component uses embedding similarity to recognize semantically similar
queries and serve cached responses instantly.
"""

import json
import logging
import time
from typing import Any

import numpy as np
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class CacheEntry(BaseModel):
    """Entry in the semantic cache."""

    query_text: str = Field(..., description="Original query text")
    response_text: str = Field(..., description="Cached response")
    embedding: list[float] = Field(..., description="Query embedding vector")
    timestamp: float = Field(..., description="Creation timestamp")
    access_count: int = Field(default=0, description="Number of times accessed")
    last_accessed: float = Field(default_factory=time.time, description="Last access timestamp")

    @validator("embedding")
    def validate_embedding(cls, v):
        """Ensure embedding is a list of floats."""
        if not isinstance(v, list):
            raise ValueError("Embedding must be a list")
        if len(v) == 0:
            raise ValueError("Embedding cannot be empty")
        return v


class ContrastiveSemanticCache:
    """Semantic cache that uses embedding similarity for query matching.

    Uses a bi-encoder to embed queries and cosine similarity to find
    semantically similar cached queries, enabling instant responses
    for recurring questions even if phrased differently.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.92,
        max_entries: int = 1000,
        lazy_load: bool = True,
        ttl_seconds: int | None = None,
    ):
        """Initialize the Contrastive Semantic cache.

        Args:
            model_name: Name of the sentence transformer model
            similarity_threshold: Minimum similarity for cache hit (0.0-1.0)
            max_entries: Maximum number of entries to store
            lazy_load: Whether to load model on first use
            ttl_seconds: Time-to-live for cache entries (None for no expiry)
        """
        self.model_name = model_name
        self.similarity_threshold = max(0.0, min(1.0, similarity_threshold))
        self.max_entries = max_entries
        self.lazy_load = lazy_load
        self.ttl_seconds = ttl_seconds

        # Storage
        self._cache: list[CacheEntry] = []
        self._embedding_matrix: np.ndarray | None = None

        # Model state
        self._model = None
        self._model_loaded = False
        self._fallback_mode = False

        # Statistics
        self._stats = {"hits": 0, "misses": 0, "puts": 0, "evictions": 0}

        logger.info(
            f"Initialized ContrastiveSemanticCache: model={model_name}, "
            f"threshold={similarity_threshold}, max_entries={max_entries}",
        )

    @property
    def is_available(self) -> bool:
        """Check if the cache is available (model loaded or can be loaded)."""
        if self._model_loaded:
            return not self._fallback_mode
        if self._fallback_mode:
            return False
        # Try to check availability without loading
        try:
            return True
        except ImportError:
            logger.warning(
                "sentence_transformers or numpy not available, cache will be in fallback mode",
            )
            return False

    def _load_model(self) -> bool:
        """Load the sentence transformer model.

        Returns:
            True if model loaded successfully, False if in fallback mode
        """
        if self._model_loaded:
            return not self._fallback_mode

        try:
            # Import required libraries

            logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            start_time = time.time()

            # Load the model
            self._model = SentenceTransformer(self.model_name)

            load_time = time.time() - start_time
            logger.info(f"Model loaded in {load_time:.2f}s")

            self._model_loaded = True
            self._fallback_mode = False
            return True

        except ImportError as e:
            logger.error(f"Failed to import required libraries: {e}")
            logger.warning("cache will operate in fallback mode (no caching)")
            self._fallback_mode = True
            self._model_loaded = True
            return False
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            logger.warning("cache will operate in fallback mode (no caching)")
            self._fallback_mode = True
            self._model_loaded = True
            return False

    def _encode_query(self, query: str) -> np.ndarray | None:
        """Encode a query into an embedding vector.

        Args:
            query: Query string to encode

        Returns:
            Embedding vector or None if encoding failed
        """
        if not query:
            return None

        # Load model if needed
        if not self._model_loaded:
            if not self._load_model():
                return None

        # Fallback mode check
        if self._fallback_mode:
            return None

        try:
            # Encode the query
            embedding = self._model.encode(query, convert_to_numpy=True, show_progress_bar=False)

            return embedding

        except Exception as e:
            logger.error(f"Failed to encode query: {e}")
            return None

    def _update_embedding_matrix(self):
        """Update the embedding matrix from cache entries."""
        if not self._cache:
            self._embedding_matrix = None
            return

        try:
            embeddings = [np.array(entry.embedding) for entry in self._cache]
            self._embedding_matrix = np.vstack(embeddings)
        except Exception as e:
            logger.error(f"Failed to update embedding matrix: {e}")
            self._embedding_matrix = None

    def _calculate_similarity(self, query_embedding: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between query and all cached embeddings.

        Args:
            query_embedding: Query embedding vector

        Returns:
            Array of similarity scores
        """
        if self._embedding_matrix is None:
            return np.array([])

        try:
            # Normalize vectors
            query_norm = query_embedding / np.linalg.norm(query_embedding)
            cache_norm = self._embedding_matrix / np.linalg.norm(
                self._embedding_matrix,
                axis=1,
                keepdims=True,
            )

            # Calculate cosine similarity
            similarities = np.dot(cache_norm, query_norm)

            return similarities

        except Exception as e:
            logger.error(f"Failed to calculate similarities: {e}")
            return np.array([])

    def _evict_if_needed(self):
        """Evict entries if cache exceeds max_entries."""
        if len(self._cache) <= self.max_entries:
            return

        # Simple eviction: remove oldest entries
        evict_count = len(self._cache) - self.max_entries
        self._cache = self._cache[evict_count:]
        self._stats["evictions"] += evict_count

        # Update embedding matrix
        self._update_embedding_matrix()

        logger.info(f"Evicted {evict_count} old cache entries")

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if a cache entry has expired.

        Args:
            entry: cache entry to check

        Returns:
            True if entry is expired
        """
        if self.ttl_seconds is None:
            return False

        age = time.time() - entry.timestamp
        return age > self.ttl_seconds

    def get(self, query: str, threshold: float | None = None) -> str | None:
        """Get cached response for a semantically similar query.

        Args:
            query: Query string to look up
            threshold: Override similarity threshold

        Returns:
            Cached response if found, None otherwise
        """
        # Validate input
        if not query:
            return None

        # Use provided threshold or default
        sim_threshold = threshold if threshold is not None else self.similarity_threshold

        # Fallback mode check
        if self._fallback_mode:
            logger.debug("cache in fallback mode, returning miss")
            self._stats["misses"] += 1
            return None

        # Encode query
        query_embedding = self._encode_query(query)
        if query_embedding is None:
            self._stats["misses"] += 1
            return None

        # Calculate similarities
        similarities = self._calculate_similarity(query_embedding)
        if len(similarities) == 0:
            self._stats["misses"] += 1
            return None

        # Find best match
        max_idx = np.argmax(similarities)
        max_similarity = float(similarities[max_idx])

        # Check threshold
        if max_similarity >= sim_threshold:
            # Check if expired
            entry = self._cache[max_idx]
            if self._is_expired(entry):
                logger.debug(f"cache hit but entry expired (similarity: {max_similarity:.3f})")
                # Remove expired entry
                self._cache.pop(max_idx)
                self._update_embedding_matrix()
                self._stats["misses"] += 1
                return None

            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = time.time()

            logger.debug(f"cache hit (similarity: {max_similarity:.3f})")
            self._stats["hits"] += 1
            return entry.response_text
        else:
            logger.debug(f"cache miss (best similarity: {max_similarity:.3f} < {sim_threshold})")
            self._stats["misses"] += 1
            return None

    def put(self, query: str, response: str, force: bool = False) -> bool:
        """Store a query-response pair in the cache.

        Args:
            query: Query string
            response: Response to cache
            force: Whether to force storage even in fallback mode

        Returns:
            True if stored successfully, False otherwise
        """
        # Validate inputs
        if not query or not response:
            return False

        # Fallback mode check
        if self._fallback_mode and not force:
            logger.debug("cache in fallback mode, skipping put")
            return False

        # Encode query
        query_embedding = self._encode_query(query)
        if query_embedding is None:
            return False

        # Create cache entry
        entry = CacheEntry(
            query_text=query,
            response_text=response,
            embedding=query_embedding.tolist(),
            timestamp=time.time(),
        )

        # Add to cache
        self._cache.append(entry)
        self._stats["puts"] += 1

        # Evict if needed
        self._evict_if_needed()

        # Update embedding matrix
        self._update_embedding_matrix()

        logger.debug(f"Cached entry for query: {query[:50]}...")
        return True

    def clear(self):
        """Clear all cache entries."""
        self._cache.clear()
        self._embedding_matrix = None
        logger.info("cache cleared")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0.0

        return {
            "entries": len(self._cache),
            "max_entries": self.max_entries,
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "puts": self._stats["puts"],
            "evictions": self._stats["evictions"],
            "hit_rate": hit_rate,
            "model_loaded": self._model_loaded,
            "fallback_mode": self._fallback_mode,
        }

    def export_cache(self, filepath: str):
        """Export cache to JSON file.

        Args:
            filepath: Path to save the cache
        """
        try:
            data = {
                "entries": [entry.dict() for entry in self._cache],
                "stats": self._stats,
                "config": {
                    "model_name": self.model_name,
                    "similarity_threshold": self.similarity_threshold,
                    "max_entries": self.max_entries,
                },
            }

            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Exported {len(self._cache)} cache entries to {filepath}")

        except Exception as e:
            logger.error(f"Failed to export cache: {e}")

    def import_cache(self, filepath: str, clear_existing: bool = False):
        """Import cache from JSON file.

        Args:
            filepath: Path to load cache from
            clear_existing: Whether to clear existing cache
        """
        try:
            with open(filepath) as f:
                data = json.load(f)

            if clear_existing:
                self.clear()

            # Load entries
            for entry_data in data.get("entries", []):
                entry = CacheEntry(**entry_data)
                self._cache.append(entry)

            # Update embedding matrix
            self._update_embedding_matrix()

            logger.info(f"Imported {len(data.get('entries', []))} cache entries from {filepath}")

        except Exception as e:
            logger.error(f"Failed to import cache: {e}")


# Convenience function for direct usage
def get_cached_response(query: str, cache: ContrastiveSemanticCache) -> str | None:
    """Get cached response for a query.

    Args:
        query: Query string
        cache: Semantic cache instance

    Returns:
        Cached response or None
    """
    return cache.get(query)


# Null cache for when dependencies are missing
class NullCache:
    """Fallback cache that never stores or retrieves anything."""

    def __init__(self, *args, **kwargs):
        """Initialize the null cache."""
        logger.warning("Using NullCache - no caching will be performed")

    def get(self, query: str, threshold: float | None = None) -> str | None:
        """Always return None (cache miss)."""
        return None

    def put(self, query: str, response: str, force: bool = False) -> bool:
        """Never store anything."""
        return False

    def clear(self):
        """No-op."""
        pass

    def get_stats(self) -> dict[str, Any]:
        """Return empty stats."""
        return {"entries": 0, "hits": 0, "misses": 0, "hit_rate": 0.0, "fallback_mode": True}
