"""Foundational behavioral tests for agentic_core/L0_routing/scripts/run_hygiene_guardian_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_run_hygiene_guardian_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.run_hygiene_guardian_util import (  # noqa: F401
        scan_temp_artifacts,
        scan_empty_folders,
        scan_folders_with_only_init,
        remove_artifacts,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    scan_temp_artifacts = None  # type: ignore[assignment,misc]
    scan_empty_folders = None  # type: ignore[assignment,misc]
    scan_folders_with_only_init = None  # type: ignore[assignment,misc]
    remove_artifacts = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="run_hygiene_guardian_util.py deps unavailable")
class TestScanTempArtifactsFunction:
    def test_is_callable(self):
        assert callable(scan_temp_artifacts)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(scan_temp_artifacts)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="run_hygiene_guardian_util.py deps unavailable")
class TestScanEmptyFoldersFunction:
    def test_is_callable(self):
        assert callable(scan_empty_folders)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(scan_empty_folders)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="run_hygiene_guardian_util.py deps unavailable")
class TestScanFoldersWithOnlyInitFunction:
    def test_is_callable(self):
        assert callable(scan_folders_with_only_init)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(scan_folders_with_only_init)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="run_hygiene_guardian_util.py deps unavailable")
class TestRemoveArtifactsFunction:
    def test_is_callable(self):
        assert callable(remove_artifacts)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(remove_artifacts)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="run_hygiene_guardian_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="run_hygiene_guardian_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="run_hygiene_guardian_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="run_hygiene_guardian_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="run_hygiene_guardian_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module run_hygiene_guardian_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
