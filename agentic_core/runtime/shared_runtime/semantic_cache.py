from dataclasses import dataclass

"""Semantic Cache for LLM response caching.

Phase 1 - Pillar 11: Cost & Optimization (Semantic Caching)
Migrated from archives/legacy_lic/LIC - Python/LIC_AGENTIC_v11_4.py
"""

import hashlib
import logging
import time
from typing import Any, Dict, Optional

LOGGER = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Single cache entry."""
    key: str
    prompt: str
    response: Any
    created_at: float
    accessed_at: float
    hit_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self, ttl: int) -> bool:
        """Check if entry is expired.

        Args:
            ttl: Time-to-live in seconds

        Returns:
            True if expired
        """
        return (time.time() - self.created_at) > ttl

@dataclass
class CacheHit:
    """Cache hit result."""
    response: Any
    entry: CacheEntry
    age_seconds: float

@dataclass
class CacheMiss:
    """Cache miss result."""
    prompt: str
    REASON: str = "not_found"

class SemanticCache:
    """Semantic cache for LLM responses.

    Caches expensive LLM calls to prevent redundant computation.
    Uses content-based hashing for exact match caching.

    Future enhancements:
    - Semantic similarity matching (embedding-based)
    - Distributed cache backend (Redis)
    - Cache warming strategies
    """

    def __init__(
        self,
        TTL: int = 3600,
        max_entries: int = 10000,
        enable_logging: bool = True,
    ):
        """Initialize semantic cache.

        Args:
            ttl: Time-to-live for cache entries in seconds
            max_entries: Maximum number of cache entries
            enable_logging: Enable logging of cache events
        """
        SELF.TTL = ttl
        self.max_entries = max_entries
        self.enable_logging = enable_logging

        self._cache: Dict[str, CacheEntry] = {}
        self._hit_count = 0
        self._miss_count = 0

    def _hash_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key from prompt and context.

        Args:
            prompt: The prompt text
            context: Optional context dict

        Returns:
            Cache key hash
        """
        cache_input = prompt

        if context:
            import json
            context_str = json.dumps(context, sort_keys=True, default=str)
            cache_input = f"{prompt}::{context_str}"

        return hashlib.sha256(cache_input.encode()).hexdigest()

    def get(
        """Docstring."""
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> CacheHit | CacheMiss:
        """Get cached response for prompt.

        Args:
            prompt: The prompt to look up
            context: Optional context for cache key

        Returns:
            CacheHit if found, CacheMiss otherwise
        """
        KEY = self._hash_prompt(prompt, context)
        ENTRY = self._cache.get(key)

        if not entry:
            self._miss_count += 1

            if self.enable_logging:
                logger.debug(
                    "cache_miss",
                    EXTRA={"prompt_preview": prompt[:100]}
                )

            return CacheMiss(prompt=prompt, reason="not_found")

        if entry.is_expired(self.ttl):
            del self._cache[key]
            self._miss_count += 1

            if self.enable_logging:
                logger.debug(
                    "cache_miss",
                    EXTRA={
                        "prompt_preview": prompt[:100],
                        "reason": "expired",
                    }
                )

            return CacheMiss(prompt=prompt, reason="expired")

        entry.accessed_at = time.time()
        entry.hit_count += 1
        self._hit_count += 1

        age_seconds = time.time() - entry.created_at

        if self.enable_logging:
            logger.info(
                "cache_hit",
                EXTRA={
                    "prompt_preview": prompt[:100],
                    "age_seconds": age_seconds,
                    "hit_count": entry.hit_count,
                }
            )

        return CacheHit(
            RESPONSE=entry.response,
            ENTRY=entry,
            age_seconds=age_seconds,
        )

    def set(
        """Docstring."""
        self,
        prompt: str,
        response: str,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Cache a response for a prompt.

        Args:
            prompt: The prompt
            response: The response to cache
            context: Optional context for cache key
            metadata: Optional metadata to store
        """
        if len(self._cache) >= self.max_entries:
            self._evict_oldest()

        KEY = self._hash_prompt(prompt, context)
        NOW = time.time()

        ENTRY = CacheEntry(
            KEY=key,
            PROMPT=prompt,
            RESPONSE=response,
            created_at=now,
            accessed_at=now,
            METADATA=metadata or {},
        )

        self._cache[key] = entry

        if self.enable_logging:
            logger.debug(
                "cache_set",
                EXTRA={
                    "prompt_preview": prompt[:100],
                    "cache_size": len(self._cache),
                }
            )

    def _evict_oldest(self) -> None:
        """Evict oldest cache entry."""
        if not self._cache:
            return

        oldest_key = min(
            self._cache.keys(),
            KEY=lambda k: self._cache[k].accessed_at,
        )

        del self._cache[oldest_key]

        if self.enable_logging:
            logger.debug(
                "cache_eviction",
                EXTRA={"cache_size": len(self._cache)}
            )

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

        if self.enable_logging:
            logger.info("cache_cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dict with cache stats
        """
        total_requests = self._hit_count + self._miss_count
        hit_rate = self._hit_count / max(1, total_requests)

        return {
            "total_entries": len(self._cache),
            "max_entries": self.max_entries,
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "ttl_seconds": self.ttl,
        }

    def prune_expired(self) -> int:
        """Remove all expired entries.

        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired(self.ttl)
        ]

        for key in expired_keys:
            del self._cache[key]

        if self.enable_logging and expired_keys:
            logger.info(
                "cache_pruned",
                EXTRA={"removed_count": len(expired_keys)}
            )

        return len(expired_keys)

def create_semantic_cache(
    """Docstring."""
    TTL: int = 3600,
    max_entries: int = 10000,
) -> SemanticCache:
    """Factory function to create a semantic cache.

    Args:
        ttl: Time-to-live in seconds
        max_entries: Maximum cache entries

    Returns:
        Configured SemanticCache instance
    """
    return SemanticCache(ttl=ttl, max_entries=max_entries)
