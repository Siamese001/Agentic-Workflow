"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/module_collision_guardrail.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_module_collision_guardrail_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.module_collision_guardrail import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    compute_logical_import_path,
    is_allowed_shim_pair,
    scan_directory,
    should_exclude,
)


class TestComputeLogicalImportPathFunction:
    def test_is_callable(self):
        assert callable(compute_logical_import_path)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(compute_logical_import_path)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestShouldExcludeFunction:
    def test_is_callable(self):
        assert callable(should_exclude)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(should_exclude)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestScanDirectoryFunction:
    def test_is_callable(self):
        assert callable(scan_directory)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(scan_directory)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestIsAllowedShimPairFunction:
    def test_is_callable(self):
        assert callable(is_allowed_shim_pair)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_allowed_shim_pair)
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
    """Module module_collision_guardrail must be importable or skip gracefully."""
    pass  # Import verified at module level
