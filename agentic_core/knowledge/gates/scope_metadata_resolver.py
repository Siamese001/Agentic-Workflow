"""Scope Metadata Resolver.

Generates scope_metadata from filters with caching and optimization.
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

log = logging.getLogger(__name__)


@dataclass
class ScopeMetadata:
    """Resolved scope metadata for query routing."""

    scope_id: str
    tenant_id: str | None = None
    region: str | None = None
    confidentiality_level: str = "public"
    allowed_sources: list[str] = field(default_factory=list)
    excluded_sources: list[str] = field(default_factory=list)
    freshness_band: str = "daily"
    metadata: dict[str, Any] = field(default_factory=dict)
    resolved_at: float = field(default_factory=time.time)


class ScopeMetadataResolver:
    """Resolves scope metadata from filter contexts.

    The ScopeMetadataResolver generates scope_metadata from filter
    results with caching to optimize repeated lookups.
    """

    def __init__(self, cache_ttl: float = 300.0):
        """Initialize the scope metadata resolver.

        Args:
            cache_ttl: Cache time-to-live in seconds
        """
        self.cache_ttl = cache_ttl
        self._cache: dict[str, tuple] = {}  # key -> (metadata, timestamp)

        log.info(f"ScopeMetadataResolver initialized (ttl={cache_ttl}s)")

    def resolve(
        self,
        filter_context: dict[str, Any],
        use_cache: bool = True,
    ) -> ScopeMetadata:
        """Resolve scope metadata from filter context.

        Args:
            filter_context: Context from pre-retrieval filters
            use_cache: Whether to use caching

        Returns:
            ScopeMetadata with resolved scope
        """
        trace_id = f"scope_{hashlib.sha256(str(filter_context).encode()).hexdigest()[:8]}"
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L1_REASONING,
            "ScopeMetadataResolver.resolve",
        )

        # Check cache
        cache_key = self._get_cache_key(filter_context)
        if use_cache and cache_key in self._cache:
            cached, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                log.debug("Scope metadata cache hit")
                return cached

        # Extract tenant
        tenant_id = filter_context.get("tenant", {}).get("tenant_id")

        # Extract region
        region = filter_context.get("region", {}).get("region")

        # Extract confidentiality
        conf_filter = filter_context.get("confidentiality", {})
        confidentiality = conf_filter.get("user_clearance", "public")

        # Build scope ID
        scope_parts = [str(tenant_id) if tenant_id else "global"]
        if region:
            scope_parts.append(region)
        scope_id = "_".join(scope_parts)

        # Determine freshness band
        freshness = filter_context.get("freshness", {})
        freshness_band = freshness.get("freshness_band", "daily")

        # Build allowed/excluded sources
        allowed = []
        excluded = []

        if tenant_id:
            allowed.append(f"tenant:{tenant_id}")

        metadata = ScopeMetadata(
            scope_id=scope_id,
            tenant_id=tenant_id,
            region=region,
            confidentiality_level=confidentiality,
            allowed_sources=allowed,
            excluded_sources=excluded,
            freshness_band=freshness_band,
            metadata={
                "filter_context": filter_context,
                "cache_key": cache_key,
            },
        )

        # Store in cache
        if use_cache:
            self._cache[cache_key] = (metadata, time.time())

        log.debug(f"Resolved scope: {scope_id}")
        return metadata

    def invalidate_cache(self, scope_id: str | None = None) -> int:
        """Invalidate cache entries.

        Args:
            scope_id: Optional specific scope to invalidate

        Returns:
            Number of entries invalidated
        """
        if scope_id is None:
            count = len(self._cache)
            self._cache.clear()
            log.info(f"Invalidated all {count} cache entries")
            return count

        # Find and remove entries matching scope_id
        keys_to_remove = [k for k, (v, _) in self._cache.items() if v.scope_id == scope_id]
        for key in keys_to_remove:
            del self._cache[key]

        log.info(f"Invalidated {len(keys_to_remove)} cache entries for {scope_id}")
        return len(keys_to_remove)

    def get_cache_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        return {
            "cache_size": len(self._cache),
        }

    def _get_cache_key(self, context: dict[str, Any]) -> str:
        """Generate cache key from context."""
        # Hash the relevant parts of the context
        key_parts = []

        if "tenant" in context:
            key_parts.append(f"t:{context['tenant'].get('tenant_id', 'none')}")
        if "region" in context:
            key_parts.append(f"r:{context['region'].get('region', 'none')}")
        if "confidentiality" in context:
            key_parts.append(f"c:{context['confidentiality'].get('user_clearance', 'public')}")
        if "freshness" in context:
            key_parts.append(f"f:{context['freshness'].get('freshness_band', 'daily')}")

        key_str = "|".join(key_parts)
        return hashlib.sha256(key_str.encode()).hexdigest()


# Global instance
_global_resolver: ScopeMetadataResolver | None = None


def get_scope_metadata_resolver() -> ScopeMetadataResolver:
    """Get or create the global scope metadata resolver."""
    global _global_resolver
    if _global_resolver is None:
        _global_resolver = ScopeMetadataResolver()
    return _global_resolver


def resolve_scope_metadata(context: dict[str, Any]) -> ScopeMetadata:
    """Convenience function to resolve scope metadata."""
    return get_scope_metadata_resolver().resolve(context)
