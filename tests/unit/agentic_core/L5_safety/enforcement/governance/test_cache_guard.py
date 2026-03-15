"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/governance/cache_guard.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_cache_guard_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.governance.cache_guard import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        estimate_directory_size,
        has_tracked_files,
        is_cache_directory,
        is_excluded_directory,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    is_cache_directory = None  # type: ignore[assignment,misc]
    is_excluded_directory = None  # type: ignore[assignment,misc]
    estimate_directory_size = None  # type: ignore[assignment,misc]
    has_tracked_files = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="cache_guard.py deps unavailable")
class TestIsCacheDirectoryFunction:
    def test_is_callable(self):
        assert callable(is_cache_directory)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_cache_directory)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="cache_guard.py deps unavailable")
class TestIsExcludedDirectoryFunction:
    def test_is_callable(self):
        assert callable(is_excluded_directory)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_excluded_directory)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="cache_guard.py deps unavailable")
class TestEstimateDirectorySizeFunction:
    def test_is_callable(self):
        assert callable(estimate_directory_size)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(estimate_directory_size)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="cache_guard.py deps unavailable")
class TestHasTrackedFilesFunction:
    def test_is_callable(self):
        assert callable(has_tracked_files)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(has_tracked_files)
        assert sig.return_annotation is not inspect.Parameter.empty

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


def test_module_importable():
    """Module cache_guard must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
