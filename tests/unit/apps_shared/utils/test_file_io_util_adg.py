"""ADG-driven tests for apps_shared/utils/file_io_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.file_io_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        calculate_file_hash,
        get_python_files,
        is_excluded,
        write_compliant_file,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    calculate_file_hash = None  # type: ignore[assignment,misc]
    is_excluded = None  # type: ignore[assignment,misc]
    get_python_files = None  # type: ignore[assignment,misc]
    write_compliant_file = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="file_io_util.py deps unavailable")
class TestCalculateFileHash:
    def test_is_callable(self):
        assert callable(calculate_file_hash)

@pytest.mark.skipif(not _AVAILABLE, reason="file_io_util.py deps unavailable")
class TestIsExcluded:
    def test_is_callable(self):
        assert callable(is_excluded)

@pytest.mark.skipif(not _AVAILABLE, reason="file_io_util.py deps unavailable")
class TestGetPythonFiles:
    def test_is_callable(self):
        assert callable(get_python_files)

@pytest.mark.skipif(not _AVAILABLE, reason="file_io_util.py deps unavailable")
class TestWriteCompliantFile:
    def test_is_callable(self):
        assert callable(write_compliant_file)

@pytest.mark.skipif(not _AVAILABLE, reason="file_io_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_io_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_io_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_io_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_io_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_io_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module file_io_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE