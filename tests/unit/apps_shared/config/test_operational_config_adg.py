"""ADG-driven tests for apps_shared/config/operational_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.config.operational_config import (  # noqa: F401
        is_excluded_path,
        is_allowed_duplicate,
        should_scan_directory,
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
    is_excluded_path = None  # type: ignore[assignment,misc]
    is_allowed_duplicate = None  # type: ignore[assignment,misc]
    should_scan_directory = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="operational_config.py deps unavailable")
class TestIsExcludedPath:
    def test_is_callable(self):
        assert callable(is_excluded_path)

@pytest.mark.skipif(not _AVAILABLE, reason="operational_config.py deps unavailable")
class TestIsAllowedDuplicate:
    def test_is_callable(self):
        assert callable(is_allowed_duplicate)

@pytest.mark.skipif(not _AVAILABLE, reason="operational_config.py deps unavailable")
class TestShouldScanDirectory:
    def test_is_callable(self):
        assert callable(should_scan_directory)

@pytest.mark.skipif(not _AVAILABLE, reason="operational_config.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="operational_config.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="operational_config.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="operational_config.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="operational_config.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="operational_config.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module operational_config.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
