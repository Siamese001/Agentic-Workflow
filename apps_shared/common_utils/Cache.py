"""LLM Cache Key Generation Utilities.

Provides high-performance cache key generation for LLM requests.
"""

import hashlib
import json
from typing import Any, Dict, List, Optional

# Version for cache key format to ensure compatibility
CACHE_KEY_VERSION = "v1.0"


def generate_llm_cache_key(model: str, messages: List[Dict[str, Any]]) -> str:
    """Generate a cache key for LLM requests.

    Args:
        model: Model name (e.g., "gpt-4o")
        messages: List of message dictionaries

    Returns:
        Cache key string
    """
    # Create a normalized representation
    key_data = {
        "model": model,
        "messages": messages
    }

    # Serialize to JSON with sorted keys for consistency
    serialized = json.dumps(key_data, sort_keys=True, separators=(",", ":"))

    # Generate SHA-256 hash
    return hashlib.sha256(serialized.encode()).hexdigest()


def generate_llm_cache_key_with_fingerprint(
    model: str,
    messages: List[Dict[str, Any]],
    fingerprint: str
) -> str:
    """Generate a cache key with additional fingerprint.

    Args:
        model: Model name
        messages: List of message dictionaries
        fingerprint: Additional identifier for cache variation

    Returns:
        Cache key string with fingerprint
    """
    # Include fingerprint in the key data
    key_data = {
        "model": model,
        "messages": messages,
        "fingerprint": fingerprint
    }

    # Serialize to JSON with sorted keys
    serialized = json.dumps(key_data, sort_keys=True, separators=(",", ":"))

    # Generate SHA-256 hash
    return hashlib.sha256(serialized.encode()).hexdigest()


def should_invalidate_cache(
    cache_key: str,
    current_version: Optional[str] = None,
    model: Optional[str] = None,
    messages: Optional[List[Dict[str, Any]]] = None,
    ttl_seconds: int = 3600
) -> bool:
    """Check if a cache entry should be invalidated.

    This is a simple implementation that always returns False
    (don't invalidate) for performance testing.

    Args:
        cache_key: Current cache key
        current_version: Optional current cache version
        model: Optional model name
        messages: Optional list of message dictionaries
        ttl_seconds: Time-to-live in seconds (default 1 hour)

    Returns:
        True if cache should be invalidated
    """
    # For performance testing, we don't invalidate
    # In a real implementation, this would check timestamps,
    # model versions, or other invalidation criteria
    return False
