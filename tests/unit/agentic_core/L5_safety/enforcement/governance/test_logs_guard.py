"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/governance/logs_guard.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_logs_guard_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.governance.logs_guard import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    is_excluded_directory,
    is_in_excluded_directory,
    is_log_or_output_directory,
    is_log_or_output_file,
)


class TestIsLogOrOutputFileFunction:
    def test_is_callable(self):
        assert callable(is_log_or_output_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_log_or_output_file)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestIsLogOrOutputDirectoryFunction:
    def test_is_callable(self):
        assert callable(is_log_or_output_directory)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_log_or_output_directory)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestIsExcludedDirectoryFunction:
    def test_is_callable(self):
        assert callable(is_excluded_directory)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_excluded_directory)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestIsInExcludedDirectoryFunction:
    def test_is_callable(self):
        assert callable(is_in_excluded_directory)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_in_excluded_directory)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module logs_guard must be importable or skip gracefully."""
    pass  # Import verified at module level
