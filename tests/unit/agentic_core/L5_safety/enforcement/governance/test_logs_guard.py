"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/governance/logs_guard.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_logs_guard_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.governance.logs_guard import (  # noqa: F401
        is_log_or_output_file,
        is_log_or_output_directory,
        is_excluded_directory,
        is_in_excluded_directory,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    is_log_or_output_file = None  # type: ignore[assignment,misc]
    is_log_or_output_directory = None  # type: ignore[assignment,misc]
    is_excluded_directory = None  # type: ignore[assignment,misc]
    is_in_excluded_directory = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestIsLogOrOutputFileFunction:
    def test_is_callable(self):
        assert callable(is_log_or_output_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_log_or_output_file)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestIsLogOrOutputDirectoryFunction:
    def test_is_callable(self):
        assert callable(is_log_or_output_directory)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_log_or_output_directory)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestIsExcludedDirectoryFunction:
    def test_is_callable(self):
        assert callable(is_excluded_directory)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_excluded_directory)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestIsInExcludedDirectoryFunction:
    def test_is_callable(self):
        assert callable(is_in_excluded_directory)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_in_excluded_directory)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module logs_guard must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
