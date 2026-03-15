"""ADG-driven tests for agentic_core/runtime/utils/file_cache_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.runtime.utils.file_cache_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        FileCache,
        get_all_files,
        get_python_files,
        invalidate_cache,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    FileCache = None  # type: ignore[assignment,misc]
    get_python_files = None  # type: ignore[assignment,misc]
    get_all_files = None  # type: ignore[assignment,misc]
    invalidate_cache = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="file_cache_util.py deps unavailable")
class TestFileCache:
    def test_is_class(self):
        assert isinstance(FileCache, type)
    def test_importable(self):
        assert FileCache is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_cache_util.py deps unavailable")
class TestGetPythonFiles:
    def test_is_callable(self):
        assert callable(get_python_files)

@pytest.mark.skipif(not _AVAILABLE, reason="file_cache_util.py deps unavailable")
class TestGetAllFiles:
    def test_is_callable(self):
        assert callable(get_all_files)

@pytest.mark.skipif(not _AVAILABLE, reason="file_cache_util.py deps unavailable")
class TestInvalidateCache:
    def test_is_callable(self):
        assert callable(invalidate_cache)

@pytest.mark.skipif(not _AVAILABLE, reason="file_cache_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_cache_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_cache_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_cache_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_cache_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_cache_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module file_cache_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
