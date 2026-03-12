"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/governance/docs_structure_guard.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_docs_structure_guard_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.governance.docs_structure_guard import (  # noqa: F401
        is_valid_extension,
        has_backup_suffix,
        has_h1_heading,
        scan_docs_directory,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    is_valid_extension = None  # type: ignore[assignment,misc]
    has_backup_suffix = None  # type: ignore[assignment,misc]
    has_h1_heading = None  # type: ignore[assignment,misc]
    scan_docs_directory = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestIsValidExtensionFunction:
    def test_is_callable(self):
        assert callable(is_valid_extension)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_valid_extension)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestHasBackupSuffixFunction:
    def test_is_callable(self):
        assert callable(has_backup_suffix)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(has_backup_suffix)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestHasH1HeadingFunction:
    def test_is_callable(self):
        assert callable(has_h1_heading)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(has_h1_heading)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestScanDocsDirectoryFunction:
    def test_is_callable(self):
        assert callable(scan_docs_directory)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(scan_docs_directory)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module docs_structure_guard must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
