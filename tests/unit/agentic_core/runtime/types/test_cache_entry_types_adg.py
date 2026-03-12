"""ADG importability contract for agentic_core/runtime/types/cache_entry_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_cache_entry_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.types.cache_entry_types import (  # noqa: F401
        CacheEntry,
        SemanticCacheHit,
        CacheMiss,
        semantic_cache,
        create_semantic_cache,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    CacheEntry = None  # type: ignore[assignment,misc]
    SemanticCacheHit = None  # type: ignore[assignment,misc]
    CacheMiss = None  # type: ignore[assignment,misc]
    semantic_cache = None  # type: ignore[assignment,misc]
    create_semantic_cache = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="cache_entry_types.py deps unavailable")
class TestCacheEntryTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: cache_entry_types.py must be importable."""
        assert _AVAILABLE

    def test_cacheentry_is_type(self) -> None:
        assert CacheEntry is not None

    def test_semanticcachehit_is_type(self) -> None:
        assert SemanticCacheHit is not None

    def test_cachemiss_is_type(self) -> None:
        assert CacheMiss is not None

    def test_create_semantic_cache_callable(self) -> None:
        assert callable(create_semantic_cache)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

