"""
agentic_core/L1_cognition/reasoning/types/client_types.py

Passive data structures and constants for MetaLearningClient.
Extracted from engine/meta_client.py to prevent circular dependencies.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Final

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR

DEFAULT_SIMILARITY_THRESHOLD: Final[float] = 0.85
DEFAULT_TTL_SECONDS: Final[int] = 3600
MAX_HEALING_DEPTH: Final[int] = 5
CACHE_KEY_PREFIX: Final[str] = "meta_learning:"
PINECONE_NAMESPACE_PREFIX: Final[str] = "healing_patterns"


@dataclass
class HealingPattern:
    """
    Represents a successful healing pattern stored in Pinecone.

    Attributes:
        pattern_id: Unique identifier for the pattern
        violation_type: Type of violation this pattern addresses
        error_signature: Hash of the error signature
        healing_strategy: The successful healing approach
        success_count: Number of times this pattern succeeded
        domain: Domain context (agentic_core, apps_lic, apps_rg)
        metadata: Additional pattern metadata
        embedding: Vector embedding of the pattern (optional)
    """

    pattern_id: str
    violation_type: str
    error_signature: str
    healing_strategy: dict[str, Any]
    success_count: int = 1
    domain: str = AGENTIC_CORE_DIR
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert pattern to dictionary for storage."""
        return {
            "pattern_id": self.pattern_id,
            "violation_type": self.violation_type,
            "error_signature": self.error_signature,
            "healing_strategy": self.healing_strategy,
            "success_count": self.success_count,
            "domain": self.domain,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HealingPattern:
        """Create pattern from dictionary."""
        return cls(
            pattern_id=data.get("pattern_id", ""),
            violation_type=data.get("violation_type", ""),
            error_signature=data.get("error_signature", ""),
            healing_strategy=data.get("healing_strategy", {}),
            success_count=data.get("success_count", 1),
            domain=data.get("domain", AGENTIC_CORE_DIR),
            metadata=data.get("metadata", {}),
            embedding=data.get("embedding"),
        )


@dataclass
class CacheEntry:
    """
    Represents a cached entry in Redis.

    Attributes:
        key: Cache key
        value: Cached value
        ttl: Time-to-live in seconds
        created_at: Timestamp of creation
        domain: Domain context
        hit_count: Number of cache hits
    """

    key: str
    value: Any
    ttl: int = DEFAULT_TTL_SECONDS
    created_at: float = field(default_factory=time.time)
    domain: str = AGENTIC_CORE_DIR
    hit_count: int = 0

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.created_at > self.ttl
