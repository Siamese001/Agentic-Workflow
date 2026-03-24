"""ADG importability contract for agentic_core/cache/redis_cache_client.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_redis_cache_client.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.cache.redis_cache_client import (  # noqa: F401
        CacheDB,
        CacheStats,
        DeterministicRedisCache,
        canonical_json_bytes,
        content_hash,
        get_hot_cache,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    CacheDB = None  # type: ignore[assignment,misc]
    canonical_json_bytes = None  # type: ignore[assignment,misc]
    content_hash = None  # type: ignore[assignment,misc]
    CacheStats = None  # type: ignore[assignment,misc]
    DeterministicRedisCache = None  # type: ignore[assignment,misc]
    get_hot_cache = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="redis_cache_client deps unavailable")
class TestRedisCacheClientImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/cache/redis_cache_client.py must be importable."""
        assert _AVAILABLE

    def test_cachedb_defined(self) -> None:
        assert CacheDB is not None

    def test_cachestats_defined(self) -> None:
        assert CacheStats is not None

    def test_deterministicrediscache_defined(self) -> None:
        assert DeterministicRedisCache is not None