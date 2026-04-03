"""Retrieval and caching module for execute_ssot - extracted from monolith.

This module contains cache management and context retrieval functionality
that was previously in the monolithic execute_ssot.py file.
"""

from typing import Any, Dict
import hashlib

# L1 Exact Match Cache - stores exact query results
_L1_EXACT_CACHE: Dict[str, Dict[str, Any]] = {}

# L2 Semantic Cache - stores semantic query results (would use embeddings in full implementation)
_L2_SEMANTIC_CACHE: Dict[str, Dict[str, Any]] = {}


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
    context: Dict[str, Any],
    timestamp: int,
    cache_type: str = "L1"
) -> None:
    """Store a context in the retrieval cache.
    
    Args:
        query: The query string
        context: The context to store
        timestamp: Unix timestamp of storage
        cache_type: Type of cache (L1 for exact, L2 for semantic)
    """
    query_hash = _get_query_hash(query)
    entry = {
        "context": context,
        "cached_at": timestamp,
        "query": query,
    }
    
    if cache_type == "L1":
        _L1_EXACT_CACHE[query_hash] = entry
    elif cache_type == "L2":
        _L2_SEMANTIC_CACHE[query_hash] = entry


def _retrieve_execution_context(query: str, timestamp: int) -> Dict[str, Any]:
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
        if entry and isinstance(entry, dict) and "context" in entry:
            return {
                "context": entry["context"],
                "tier": "L1",
                "cached": True,
                "timestamp": timestamp,
            }
    
    # Check L2 semantic cache
    if query_hash in _L2_SEMANTIC_CACHE:
        entry = _L2_SEMANTIC_CACHE[query_hash]
        if entry and isinstance(entry, dict) and "context" in entry:
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


def _get_cache_stats() -> Dict[str, int]:
    """Get cache statistics.
    
    Returns:
        Dictionary with L1 and L2 cache entry counts
    """
    return {
        "L1_count": len(_L1_EXACT_CACHE),
        "L2_count": len(_L2_SEMANTIC_CACHE),
    }
