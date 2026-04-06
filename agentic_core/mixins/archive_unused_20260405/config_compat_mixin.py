"""Legacy config dataclasses for mixin consolidation compatibility.

These dataclasses preserve the legacy attribute names from CachingMixin,
MetricsMixin, and BatchingMixin so that downstream consumers can migrate
incrementally without aliasing directly to PerformanceConfig.

Phase 2 of the SSOT mixin consolidation plan.
"""

from __future__ import annotations

from dataclasses import dataclass

# Configuration constants

@dataclass
class CacheConfig:
    """Legacy caching configuration (CachingMixin-compat)."""

    enabled: bool = True
    max_size: int = 1000
    default_ttl: float | None = None


@dataclass
class MetricsConfig:
    """Legacy metrics configuration (MetricsMixin-compat)."""

    enabled: bool = True


@dataclass
class BatchingConfig:
    """Legacy batching configuration (BatchingMixin-compat)."""

    enabled: bool = True
    max_batch_size: int = 10
    max_wait_ms: int = 50
    max_history: int = 100
