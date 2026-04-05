"""Catalog Keymaker.

Multi-factor cache key generation with hash route_signal integration,
security ACL binding, and source version tracking.
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

log = logging.getLogger(__name__)


@dataclass
class CacheKey:
    """Multi-factor cache key."""
    key_hash: str
    factors: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class CatalogKeymaker:
    """Generates multi-factor cache keys.

    The CatalogKeymaker creates cache keys that incorporate multiple
    factors including query content, routing signals, security context,
    and source version for precise cache matching.
    """

    def __init__(self):
        """Initialize the catalog keymaker."""
        self._key_counter = 0
        log.info("CatalogKeymaker initialized")

    def make_key(
        self,
        query: str,
        routing_signal: dict[str, Any] | None = None,
        scope_metadata: dict[str, Any] | None = None,
        freshness_band: str = "daily",
    ) -> CacheKey:
        """Generate a multi-factor cache key.

        Args:
            query: Normalized query string
            routing_signal: Optional routing signal from detector
            scope_metadata: Optional scope metadata from gates
            freshness_band: Freshness requirement

        Returns:
            CacheKey with hash and factor breakdown
        """
        trace_id = f"key_{self._key_counter}"
        self._key_counter += 1
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "CatalogKeymaker.make_key"
        )

        # Build factor components
        factors = {
            "query_hash": self._hash_string(query),
            "freshness_band": freshness_band,
        }

        # Add routing signal factors
        if routing_signal:
            factors["intent"] = routing_signal.get("intent", "unknown")
            factors["domain"] = routing_signal.get("domain", "general")
            factors["urgency"] = routing_signal.get("urgency", 0.0)

        # Add scope metadata factors
        if scope_metadata:
            factors["tenant"] = scope_metadata.get("tenant_id", "public")
            factors["region"] = scope_metadata.get("region", "global")
            factors["confidentiality"] = scope_metadata.get("confidentiality_level", "public")

        # Generate composite hash
        key_data = json.dumps(factors, sort_keys=True)
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()

        cache_key = CacheKey(
            key_hash=key_hash,
            factors=factors,
            metadata={
                "created_at": __import__('time').time(),
                "factor_count": len(factors),
            },
        )

        log.debug(f"Generated cache key: {key_hash[:16]}... ({len(factors)} factors)")
        return cache_key

    def make_exact_key(self, query: str) -> CacheKey:
        """Generate an exact text match key (no other factors).

        Args:
            query: Exact query string

        Returns:
            CacheKey for exact matching
        """
        key_hash = self._hash_string(query)

        return CacheKey(
            key_hash=f"exact:{key_hash}",
            factors={"query_hash": key_hash, "match_type": "exact"},
            metadata={"exact_match": True},
        )

    def compare_keys(self, key1: CacheKey, key2: CacheKey) -> float:
        """Compare two cache keys for similarity.

        Args:
            key1: First cache key
            key2: Second cache key

        Returns:
            Similarity score (0-1)
        """
        if key1.key_hash == key2.key_hash:
            return 1.0

        # Compare factors
        common_factors = set(key1.factors.keys()) & set(key2.factors.keys())
        if not common_factors:
            return 0.0

        matches = sum(
            1 for f in common_factors
            if key1.factors[f] == key2.factors[f]
        )

        return matches / len(common_factors)

    def _hash_string(self, s: str) -> str:
        """Generate SHA-256 hash of string."""
        return hashlib.sha256(s.encode()).hexdigest()


# Global instance
_global_keymaker: CatalogKeymaker | None = None


def get_catalog_keymaker() -> CatalogKeymaker:
    """Get or create the global catalog keymaker."""
    global _global_keymaker
    if _global_keymaker is None:
        _global_keymaker = CatalogKeymaker()
    return _global_keymaker
