"""Query Vectorizer.

External embedding API integration for generating query vectors
with caching and batching support.
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


@dataclass
class QueryVector:
    """Vector representation of a query."""
    query_text: str
    vector: list[float]
    model: str
    dimension: int
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.dimension = len(self.vector) if self.vector else 0


class QueryVectorizer:
    """Generates vector embeddings for queries.

    The QueryVectorizer handles external embedding API integration
    with caching and batching to optimize performance.
    """

    def __init__(
        self,
        model_name: str = "default",
        dimension: int = 768,
        cache_size: int = 1000,
        batch_size: int = 32,
    ):
        """Initialize the query vectorizer.

        Args:
            model_name: Name of the embedding model to use
            dimension: Expected vector dimension
            cache_size: Size of the LRU cache
            batch_size: Maximum batch size for API calls
        """
        self.model_name = model_name
        self.dimension = dimension
        self.batch_size = batch_size

        # Initialize cache
        self._vector_cache: dict[str, QueryVector] = {}
        self._cache_size = cache_size

        # Mock embedding function (replace with actual API)
        self._embedding_fn = self._mock_embedding

        log.info(f"QueryVectorizer initialized (model={model_name}, dim={dimension})")

    def vectorize(
        self,
        query: str,
        use_cache: bool = True,
    ) -> QueryVector:
        """Generate vector for a single query.

        Args:
            query: Query text to vectorize
            use_cache: Whether to use caching

        Returns:
            QueryVector with embedding
        """
        trace_id = f"vec_{hashlib.sha256(query.encode()).hexdigest()[:8]}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "QueryVectorizer.vectorize"
        )

        # Check cache
        cache_key = self._get_cache_key(query)
        if use_cache and cache_key in self._vector_cache:
            cached = self._vector_cache[cache_key]
            log.debug(f"Cache hit for query vector: {query[:30]}...")
            return cached

        # Generate vector
        start_time = time.time()
        vector = self._embedding_fn(query)
        latency = time.time() - start_time

        result = QueryVector(
            query_text=query,
            vector=vector,
            model=self.model_name,
            dimension=len(vector),
            metadata={
                "latency_ms": latency * 1000,
                "cached": False,
            },
        )

        # Store in cache
        if use_cache:
            self._store_in_cache(cache_key, result)

        _emit_records_telemetry_event(
            "embedding",
            f"generated_{self.model_name}"
        )

        log.debug(f"Generated vector for query: {query[:30]}... ({len(vector)} dims)")
        return result

    def vectorize_batch(
        self,
        queries: list[str],
        use_cache: bool = True,
    ) -> list[QueryVector]:
        """Generate vectors for multiple queries.

        Args:
            queries: List of query texts
            use_cache: Whether to use caching

        Returns:
            List of QueryVector objects
        """
        trace_id = f"batch_vec_{len(queries)}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "QueryVectorizer.vectorize_batch"
        )

        results = []

        # Process in batches
        for i in range(0, len(queries), self.batch_size):
            batch = queries[i:i + self.batch_size]
            batch_results = self._process_batch(batch, use_cache)
            results.extend(batch_results)

        _emit_records_telemetry_event(
            "embedding_batch",
            f"batch_{len(queries)}"
        )

        log.info(f"Vectorized {len(queries)} queries in {len(results)} results")
        return results

    def set_embedding_function(self, fn: callable) -> None:
        """Set a custom embedding function.

        Args:
            fn: Function that takes a string and returns a list of floats
        """
        self._embedding_fn = fn
        log.info("Custom embedding function set")

    def clear_cache(self) -> int:
        """Clear the vector cache.

        Returns:
            Number of entries cleared
        """
        count = len(self._vector_cache)
        self._vector_cache.clear()
        log.info(f"Cleared {count} entries from vector cache")
        return count

    def get_cache_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        return {
            "cache_size": len(self._vector_cache),
            "max_size": self._cache_size,
        }

    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for query."""
        return hashlib.sha256(f"{self.model_name}:{query}".encode()).hexdigest()

    def _store_in_cache(self, key: str, vector: QueryVector) -> None:
        """Store vector in cache with LRU eviction."""
        # Simple LRU: if at capacity, clear half the cache
        if len(self._vector_cache) >= self._cache_size:
            # Remove oldest half
            keys = list(self._vector_cache.keys())
            for old_key in keys[:len(keys)//2]:
                del self._vector_cache[old_key]

        self._vector_cache[key] = vector

    def _process_batch(
        self,
        queries: list[str],
        use_cache: bool,
    ) -> list[QueryVector]:
        """Process a batch of queries."""
        results = []

        for query in queries:
            result = self.vectorize(query, use_cache)
            results.append(result)

        return results

    def _mock_embedding(self, text: str) -> list[float]:
        """Mock embedding function for testing.

        In production, replace with actual embedding API call.
        """
        # Generate deterministic pseudo-random vector based on text hash
        hash_val = hashlib.sha256(text.encode()).hexdigest()

        # Use hash to seed vector generation
        vector = []
        for i in range(self.dimension):
            # Deterministic pseudo-random values between -1 and 1
            hash_chunk = hash_val[i % len(hash_val)]
            val = (ord(hash_chunk) / 128.0) - 1.0
            vector.append(val)

        # Normalize
        import math
        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude > 0:
            vector = [v / magnitude for v in vector]

        return vector


# Global instance
_global_vectorizer: QueryVectorizer | None = None


def get_query_vectorizer() -> QueryVectorizer:
    """Get or create the global query vectorizer."""
    global _global_vectorizer
    if _global_vectorizer is None:
        _global_vectorizer = QueryVectorizer()
    return _global_vectorizer


def vectorize_query(query: str) -> QueryVector:
    """Convenience function to vectorize a query."""
    return get_query_vectorizer().vectorize(query)
