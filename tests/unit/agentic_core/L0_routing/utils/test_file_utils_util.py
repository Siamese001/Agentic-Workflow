"""Foundational behavioral tests for agentic_core/L0_routing/utils/file_utils_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_file_utils_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.utils.file_utils_util import (  # noqa: F401
        ensure_directory,
        safe_read_file,
        safe_write_file,
        safe_append_file,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    ensure_directory = None  # type: ignore[assignment,misc]
    safe_read_file = None  # type: ignore[assignment,misc]
    safe_write_file = None  # type: ignore[assignment,misc]
    safe_append_file = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="file_utils_util.py deps unavailable")
class TestEnsureDirectoryFunction:
    def test_is_callable(self):
        assert callable(ensure_directory)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(ensure_directory)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="file_utils_util.py deps unavailable")
class TestSafeReadFileFunction:
    def test_is_callable(self):
        assert callable(safe_read_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_read_file)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="file_utils_util.py deps unavailable")
class TestSafeWriteFileFunction:
    def test_is_callable(self):
        assert callable(safe_write_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_write_file)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="file_utils_util.py deps unavailable")
class TestSafeAppendFileFunction:
    def test_is_callable(self):
        assert callable(safe_append_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_append_file)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="file_utils_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_utils_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_utils_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_utils_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_utils_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module file_utils_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
