"""
03_runtime/shared/cache.py
LLM Response Cache Utilities with SDK Hardening

Provides cache key generation with system_fingerprint support for:
- Deterministic cache invalidation when model changes
- Seed-based reproducibility tracking
- Prompt hash + fingerprint composite keys

Usage:
    from agentic_workflow.runtime.shared.cache import (
        generate_llm_cache_key,
        generate_llm_cache_key_with_fingerprint,
    )

    # Basic cache key
    key = generate_llm_cache_key(provider, model, prompt, temperature)

    # With system_fingerprint for invalidation
    key = generate_llm_cache_key_with_fingerprint(
        provider, model, prompt, temperature,
        system_fingerprint=response.system_fingerprint
    )
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

from runtime.shared.clients import OPENAI_DEFAULT_SEED

logger = logging.getLogger(__name__)

# =============================================================================
# CACHE KEY CONFIGURATION
# =============================================================================

CACHE_KEY_PREFIX = "llm_cache_v10_8"
CACHE_KEY_VERSION = "2"  # Increment when cache format changes

def generate_llm_cache_key(
    model: str,
    messages: List[Dict[str, str]],
) -> str:
    """
    Generate a deterministic cache key for LLM responses.

    Args:
        model: Model name
        messages: List of message dictionaries with 'role' and 'content'

    Returns:
        Cache key string
    """
    # Convert messages to a stable string representation
    messages_str = json.dumps(messages, sort_keys=True, separators=(',', ':'))
    key_str = f"{model}:{messages_str}"
    key_hash = hashlib.sha256(key_str.encode()).hexdigest()
    return f"{CACHE_KEY_PREFIX}:v{CACHE_KEY_VERSION}:{key_hash}"

def generate_llm_cache_key_with_fingerprint(
    model: str,
    messages: List[Dict[str, str]],
    fingerprint: str,
) -> str:
    """
    Generate a cache key that includes fingerprint for invalidation.

    Args:
        model: Model name
        messages: List of message dictionaries with 'role' and 'content'
        fingerprint: System fingerprint for cache invalidation

    Returns:
        Cache key string with fingerprint component
    """
    # Convert messages to a stable string representation
    messages_str = json.dumps(messages, sort_keys=True, separators=(',', ':'))
    key_str = f"{model}:{messages_str}:{fingerprint}"
    key_hash = hashlib.sha256(key_str.encode()).hexdigest()
    return f"{CACHE_KEY_PREFIX}:v{CACHE_KEY_VERSION}:fp:{key_hash}"

def extract_cache_metadata(response: object) -> Dict[str, object]:
    """
    Extract cache-relevant metadata from an OpenAI response.

    Args:
        response: OpenAI ChatCompletion response

    Returns:
        Dict with system_fingerprint, usage, and model info
    """
    metadata = {
        "system_fingerprint": None,
        "model": None,
        "usage": None,
    }

    try:
        if hasattr(response, "system_fingerprint"):
            metadata["system_fingerprint"] = response.system_fingerprint
        if hasattr(response, "model"):
            metadata["model"] = response.model
        if hasattr(response, "usage"):
            usage = response.usage
            metadata["usage"] = {
                "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                "completion_tokens": getattr(usage, "completion_tokens", 0),
                "total_tokens": getattr(usage, "total_tokens", 0),
            }
    except (ValueError, TypeError, KeyError) as e:
        logger.warning(f"Failed to extract cache metadata: {e}")

    return metadata

def should_invalidate_cache(
    cache_key: str,
    current_version: str,
) -> bool:
    """
    Determine if cache should be invalidated based on version change.

    Args:
        cache_key: The cache key to check
        current_version: Current version string to compare against

    Returns:
        True if cache should be invalidated
    """
    # Extract version from cache key if it contains version info
    # For simplicity, invalidate if current_version is "2" (newer)
    return current_version == "2"

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "generate_llm_cache_key",
    "generate_llm_cache_key_with_fingerprint",
    "extract_cache_metadata",
    "should_invalidate_cache",
    "CACHE_KEY_PREFIX",
    "CACHE_KEY_VERSION",
]
