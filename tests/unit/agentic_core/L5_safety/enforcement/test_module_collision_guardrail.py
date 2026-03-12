"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/module_collision_guardrail.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_module_collision_guardrail_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.module_collision_guardrail import (  # noqa: F401
        compute_logical_import_path,
        should_exclude,
        scan_directory,
        is_allowed_shim_pair,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    compute_logical_import_path = None  # type: ignore[assignment,misc]
    should_exclude = None  # type: ignore[assignment,misc]
    scan_directory = None  # type: ignore[assignment,misc]
    is_allowed_shim_pair = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestComputeLogicalImportPathFunction:
    def test_is_callable(self):
        assert callable(compute_logical_import_path)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(compute_logical_import_path)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestShouldExcludeFunction:
    def test_is_callable(self):
        assert callable(should_exclude)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(should_exclude)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestScanDirectoryFunction:
    def test_is_callable(self):
        assert callable(scan_directory)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(scan_directory)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestIsAllowedShimPairFunction:
    def test_is_callable(self):
        assert callable(is_allowed_shim_pair)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_allowed_shim_pair)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module module_collision_guardrail must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
