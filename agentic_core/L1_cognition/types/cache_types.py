"""
agentic_core/L1_cognition/reasoning/types/cache_types.py

Passive data structures and constants for CacheStrategyManager.
Extracted from engine/cache_manager.py to prevent circular dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final

# Constants
DEFAULT_TTL_SECONDS: Final[int] = 3600  # 1 hour
MIN_TTL_SECONDS: Final[int] = 60  # 1 minute minimum
MAX_TTL_SECONDS: Final[int] = 86400  # 24 hours maximum
DEFAULT_SIMILARITY_THRESHOLD: Final[float] = 0.85
MIN_SIMILARITY_THRESHOLD: Final[float] = 0.70
MAX_SIMILARITY_THRESHOLD: Final[float] = 0.99
MAX_CACHE_SIZE: Final[int] = 10000
MAX_HEALING_DEPTH: Final[int] = 5


class EvictionPolicy(Enum):
    """Cache eviction policies."""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time-based expiration only


@dataclass
class DomainConfig:
    """
    Domain-specific configuration for cache strategy.

    Attributes:
        domain: Domain name (agentic_core, apps_lic, apps_rg)
        ttl_seconds: Time-to-live for cache entries
        similarity_threshold: Minimum similarity for pattern matching
        max_cache_size: Maximum number of entries in domain cache
        eviction_policy: Cache eviction policy
        max_healing_depth: Maximum healing recursion depth
    """

    domain: str
    ttl_seconds: int = DEFAULT_TTL_SECONDS
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD
    max_cache_size: int = MAX_CACHE_SIZE
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    max_healing_depth: int = MAX_HEALING_DEPTH

    def __post_init__(self) -> None:
        """Validate configuration values."""
        self.ttl_seconds = max(MIN_TTL_SECONDS, min(MAX_TTL_SECONDS, self.ttl_seconds))
        self.similarity_threshold = max(
            MIN_SIMILARITY_THRESHOLD,
            min(MAX_SIMILARITY_THRESHOLD, self.similarity_threshold),
        )
        self.max_healing_depth = max(1, min(10, self.max_healing_depth))
