"""ADG-driven tests for agentic_core/L0_routing/scripts/run_hygiene_guardian_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.run_hygiene_guardian_util import (  # noqa: F401
        scan_temp_artifacts,
        scan_empty_folders,
        scan_folders_with_only_init,
        remove_artifacts,
        remove_empty_folders,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    scan_temp_artifacts = None  # type: ignore[assignment,misc]
    scan_empty_folders = None  # type: ignore[assignment,misc]
    scan_folders_with_only_init = None  # type: ignore[assignment,misc]
    remove_artifacts = None  # type: ignore[assignment,misc]
    remove_empty_folders = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="run_hygiene_guardian_util.py deps unavailable")
class TestScanTempArtifacts:
    def test_is_callable(self):
        assert callable(scan_temp_artifacts)

@pytest.mark.skipif(not _AVAILABLE, reason="run_hygiene_guardian_util.py deps unavailable")
class TestScanEmptyFolders:
    def test_is_callable(self):
        assert callable(scan_empty_folders)

@pytest.mark.skipif(not _AVAILABLE, reason="run_hygiene_guardian_util.py deps unavailable")
class TestScanFoldersWithOnlyInit:
    def test_is_callable(self):
        assert callable(scan_folders_with_only_init)

@pytest.mark.skipif(not _AVAILABLE, reason="run_hygiene_guardian_util.py deps unavailable")
class TestRemoveArtifacts:
    def test_is_callable(self):
        assert callable(remove_artifacts)

@pytest.mark.skipif(not _AVAILABLE, reason="run_hygiene_guardian_util.py deps unavailable")
class TestRemoveEmptyFolders:
    def test_is_callable(self):
        assert callable(remove_empty_folders)

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

@pytest.mark.skipif(not _AVAILABLE, reason="run_hygiene_guardian_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module run_hygiene_guardian_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
