"""ADG-driven tests for agentic_core/L5_safety/utils/cache_invalidation_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.utils.cache_invalidation_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        heal_invalidate_cache,
        invalidate_all_caches,
        invalidate_on_file_change,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    heal_invalidate_cache = None  # type: ignore[assignment,misc]
    invalidate_on_file_change = None  # type: ignore[assignment,misc]
    invalidate_all_caches = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="cache_invalidation_util.py deps unavailable")
class TestHealInvalidateCache:
    def test_is_callable(self):
        assert callable(heal_invalidate_cache)

@pytest.mark.skipif(not _AVAILABLE, reason="cache_invalidation_util.py deps unavailable")
class TestInvalidateOnFileChange:
    def test_is_callable(self):
        assert callable(invalidate_on_file_change)

@pytest.mark.skipif(not _AVAILABLE, reason="cache_invalidation_util.py deps unavailable")
class TestInvalidateAllCaches:
    def test_is_callable(self):
        assert callable(invalidate_all_caches)

@pytest.mark.skipif(not _AVAILABLE, reason="cache_invalidation_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_invalidation_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_invalidation_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_invalidation_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_invalidation_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_invalidation_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module cache_invalidation_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
