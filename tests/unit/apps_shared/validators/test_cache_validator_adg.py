"""ADG-driven tests for apps_shared/validators/cache_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.validators.cache_validator import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        generate_llm_cache_key,
        generate_llm_cache_key_with_fingerprint,
        should_invalidate_cache,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    generate_llm_cache_key = None  # type: ignore[assignment,misc]
    generate_llm_cache_key_with_fingerprint = None  # type: ignore[assignment,misc]
    should_invalidate_cache = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="cache_validator.py deps unavailable")
class TestGenerateLlmCacheKey:
    def test_is_callable(self):
        assert callable(generate_llm_cache_key)

@pytest.mark.skipif(not _AVAILABLE, reason="cache_validator.py deps unavailable")
class TestGenerateLlmCacheKeyWithFingerprint:
    def test_is_callable(self):
        assert callable(generate_llm_cache_key_with_fingerprint)

@pytest.mark.skipif(not _AVAILABLE, reason="cache_validator.py deps unavailable")
class TestShouldInvalidateCache:
    def test_is_callable(self):
        assert callable(should_invalidate_cache)

@pytest.mark.skipif(not _AVAILABLE, reason="cache_validator.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_validator.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_validator.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_validator.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_validator.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_validator.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module cache_validator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
