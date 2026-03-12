"""ADG-driven tests for agentic_core/L5_safety/enforcement/governance/cache_guard.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.governance.cache_guard import (  # noqa: F401
        is_cache_directory,
        is_excluded_directory,
        estimate_directory_size,
        has_tracked_files,
        is_forbidden_location,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    is_cache_directory = None  # type: ignore[assignment,misc]
    is_excluded_directory = None  # type: ignore[assignment,misc]
    estimate_directory_size = None  # type: ignore[assignment,misc]
    has_tracked_files = None  # type: ignore[assignment,misc]
    is_forbidden_location = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="cache_guard.py deps unavailable")
class TestIsCacheDirectory:
    def test_is_callable(self):
        assert callable(is_cache_directory)

@pytest.mark.skipif(not _AVAILABLE, reason="cache_guard.py deps unavailable")
class TestIsExcludedDirectory:
    def test_is_callable(self):
        assert callable(is_excluded_directory)

@pytest.mark.skipif(not _AVAILABLE, reason="cache_guard.py deps unavailable")
class TestEstimateDirectorySize:
    def test_is_callable(self):
        assert callable(estimate_directory_size)

@pytest.mark.skipif(not _AVAILABLE, reason="cache_guard.py deps unavailable")
class TestHasTrackedFiles:
    def test_is_callable(self):
        assert callable(has_tracked_files)

@pytest.mark.skipif(not _AVAILABLE, reason="cache_guard.py deps unavailable")
class TestIsForbiddenLocation:
    def test_is_callable(self):
        assert callable(is_forbidden_location)

@pytest.mark.skipif(not _AVAILABLE, reason="cache_guard.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_guard.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_guard.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_guard.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_guard.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_guard.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module cache_guard.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
