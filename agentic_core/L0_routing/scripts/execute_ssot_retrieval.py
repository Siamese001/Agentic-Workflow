"""Retrieval and caching module for execute_ssot - extracted from monolith.

This module contains cache management and context retrieval functionality
that was previously in the monolithic execute_ssot.py file.
"""

import hashlib
from typing import Any

# L1 Exact Match Cache - stores exact query results
_L1_EXACT_CACHE: dict[str, dict[str, Any]] = {}

# L2 Semantic Cache - stores semantic query results (would use embeddings in full implementation)
_L2_SEMANTIC_CACHE: dict[str, dict[str, Any]] = {}

# Maximum cache size to prevent unbounded memory growth
MAX_CACHE_SIZE: int = 1000

# Default cache TTL in seconds (5 minutes)
DEFAULT_CACHE_TTL: int = 300


def _enforce_cache_limit(cache: dict[str, Any], max_size: int = MAX_CACHE_SIZE) -> None:
    """Enforce cache size limit by removing oldest entries if exceeded.

    Args:
        cache: The cache dictionary to enforce limits on
        max_size: Maximum number of entries allowed
    """
    if len(cache) > max_size:
        # Remove oldest entries (first inserted)
        keys_to_remove = list(cache.keys())[:len(cache) - max_size]
        for key in keys_to_remove:
            del cache[key]


def _is_cache_entry_valid(entry: dict[str, Any], current_timestamp: int, ttl: int = DEFAULT_CACHE_TTL) -> bool:
    """Check if a cache entry is still valid (not expired).

    Args:
        entry: The cache entry dictionary
        current_timestamp: Current Unix timestamp for comparison
        ttl: Time-to-live in seconds

    Returns:
        True if entry is valid and not expired, False otherwise
    """
    if not entry or not isinstance(entry, dict):
        return False
    if "context" not in entry or "cached_at" not in entry:
        return False

    cached_at = entry.get("cached_at", 0)
    age = current_timestamp - cached_at
    return age <= ttl


def _get_query_hash(query: str) -> str:
    """Generate a hash for a query string.

    Args:
        query: The query string to hash

    Returns:
        16-character hex hash of the query
    """
    return hashlib.sha256(query.encode()).hexdigest()[:16]


def _store_in_retrieval_cache(
    query: str,
    context: dict[str, Any],
    timestamp: int,
    cache_type: str = "L1"
) -> None:
    """Store a context in the retrieval cache.

    Args:
        query: The query string
        context: The context to store
        timestamp: Unix timestamp of storage
        cache_type: Type of cache (L1 for exact, L2 for semantic)

    Raises:
        ValueError: If cache_type is not "L1" or "L2"
    """
    if cache_type not in ("L1", "L2"):
        raise ValueError(f"Invalid cache_type: {cache_type!r}. Must be 'L1' or 'L2'")

    query_hash = _get_query_hash(query)
    entry = {
        "context": context,
        "cached_at": timestamp,
        "query": query,
    }

    if cache_type == "L1":
        _L1_EXACT_CACHE[query_hash] = entry
        _enforce_cache_limit(_L1_EXACT_CACHE)
    elif cache_type == "L2":
        _L2_SEMANTIC_CACHE[query_hash] = entry
        _enforce_cache_limit(_L2_SEMANTIC_CACHE)


def _retrieve_execution_context(query: str, timestamp: int) -> dict[str, Any]:
    """Retrieve execution context for a query, using cache if available.

    Args:
        query: The query string
        timestamp: Current Unix timestamp

    Returns:
        Dictionary with context information including:
        - 'context': The retrieved context or None
        - 'tier': The cache tier used (L1, L2, or None)
        - 'cached': Whether result came from cache
        - 'timestamp': The retrieval timestamp
    """
    query_hash = _get_query_hash(query)

    # Check L1 exact cache first
    if query_hash in _L1_EXACT_CACHE:
        entry = _L1_EXACT_CACHE[query_hash]
        if _is_cache_entry_valid(entry, timestamp):
            return {
                "context": entry["context"],
                "tier": "L1",
                "cached": True,
                "timestamp": timestamp,
            }

    # Check L2 semantic cache
    if query_hash in _L2_SEMANTIC_CACHE:
        entry = _L2_SEMANTIC_CACHE[query_hash]
        if _is_cache_entry_valid(entry, timestamp):
            return {
                "context": entry["context"],
                "tier": "L2",
                "cached": True,
                "timestamp": timestamp,
            }

    # No cache hit - would perform actual retrieval here
    return {
        "context": None,
        "tier": None,
        "cached": False,
        "timestamp": timestamp,
    }


def _clear_retrieval_cache() -> None:
    """Clear all retrieval caches."""
    _L1_EXACT_CACHE.clear()
    _L2_SEMANTIC_CACHE.clear()


def _get_cache_stats() -> dict[str, int]:
    """Get cache statistics.

    Returns:
        Dictionary with L1 and L2 cache entry counts
    """
    return {
        "L1_count": len(_L1_EXACT_CACHE),
        "L2_count": len(_L2_SEMANTIC_CACHE),
    }
