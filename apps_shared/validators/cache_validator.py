"""LLM cache Key Generation Utilities.

Provides high-performance cache key generation for LLM requests.
"""

import hashlib
import json
from typing import Any

CACHE_KEY_VERSION = "v1.0"


def generate_llm_cache_key(model: str, messages: list[dict[str, Any]]) -> str:
    """Generate a cache key for LLM requests.

    Args:
        model: Model name (e.g., "gpt-4o")
        messages: List of message dictionaries

    Returns:
        cache key string
    """
    key_data = {"model": model, "messages": messages}
    serialized = json.dumps(key_data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode()).hexdigest()


def generate_llm_cache_key_with_fingerprint(
    model: str,
    messages: list[dict[str, Any]],
    fingerprint: str,
) -> str:
    """Generate a cache key with additional fingerprint.

    Args:
        model: Model name
        messages: List of message dictionaries
        fingerprint: Additional identifier for cache variation

    Returns:
        cache key string with fingerprint
    """
    key_data = {"model": model, "messages": messages, "fingerprint": fingerprint}
    serialized = json.dumps(key_data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode()).hexdigest()


def should_invalidate_cache(
    cache_key: str,
    current_version: str | None = None,
    model: str | None = None,
    messages: list[dict[str, Any]] | None = None,
    ttl_seconds: int = 3600,
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
    return False
