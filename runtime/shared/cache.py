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
from typing import Any, Dict, Optional

from .clients import OPENAI_DEFAULT_SEED

logger = logging.getLogger(__name__)

# =============================================================================
# CACHE KEY CONFIGURATION
# =============================================================================

CACHE_KEY_PREFIX = "llm_cache_v10_8"
CACHE_KEY_VERSION = "2"  # Increment when cache format changes


def generate_llm_cache_key(
    provider: str,
    model: str,
    prompt: str,
    temperature: float,
    seed: Optional[int] = None,
) -> str:
    """
    Generate a deterministic cache key for LLM responses.

    Args:
        provider: Model provider (openai, anthropic, google)
        model: Model name
        prompt: Full prompt text
        temperature: Temperature setting
        seed: Optional seed for deterministic outputs (default: OPENAI_DEFAULT_SEED)

    Returns:
        Cache key string
    """
    effective_seed = seed if seed is not None else OPENAI_DEFAULT_SEED
    key_str = f"{provider}:{model}:{prompt}:{temperature}:{effective_seed}"
    key_hash = hashlib.sha256(key_str.encode()).hexdigest()
    return f"{CACHE_KEY_PREFIX}:v{CACHE_KEY_VERSION}:{key_hash}"


def generate_llm_cache_key_with_fingerprint(
    provider: str,
    model: str,
    prompt: str,
    temperature: float,
    system_fingerprint: Optional[str] = None,
    seed: Optional[int] = None,
) -> str:
    """
    Generate a cache key that includes system_fingerprint for invalidation.

    When the model is updated (indicated by a new system_fingerprint),
    the cache key changes, ensuring stale responses are not used.

    Args:
        provider: Model provider
        model: Model name
        prompt: Full prompt text
        temperature: Temperature setting
        system_fingerprint: OpenAI system_fingerprint from response
        seed: Optional seed for deterministic outputs

    Returns:
        Cache key string with fingerprint component
    """
    effective_seed = seed if seed is not None else OPENAI_DEFAULT_SEED
    fingerprint = system_fingerprint or "none"
    key_str = f"{provider}:{model}:{prompt}:{temperature}:{effective_seed}:{fingerprint}"
    key_hash = hashlib.sha256(key_str.encode()).hexdigest()
    return f"{CACHE_KEY_PREFIX}:v{CACHE_KEY_VERSION}:fp:{key_hash}"


def extract_cache_metadata(response: Any) -> Dict[str, Any]:
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
    except Exception as e:
        logger.warning(f"Failed to extract cache metadata: {e}")

    return metadata


def should_invalidate_cache(
    cached_fingerprint: Optional[str],
    current_fingerprint: Optional[str],
) -> bool:
    """
    Determine if cache should be invalidated based on fingerprint change.

    Args:
        cached_fingerprint: Fingerprint stored with cached response
        current_fingerprint: Fingerprint from current response

    Returns:
        True if cache should be invalidated
    """
    # If either is None, don't invalidate (fingerprint not available)
    if cached_fingerprint is None or current_fingerprint is None:
        return False

    # Invalidate if fingerprints differ
    return cached_fingerprint != current_fingerprint


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
