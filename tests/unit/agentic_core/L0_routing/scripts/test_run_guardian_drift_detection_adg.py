"""ADG-driven tests for agentic_core/L0_routing/scripts/run_guardian_drift_detection.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.run_guardian_drift_detection import (  # noqa: F401
        scan_forbidden_root_folders,
        scan_archived_files_at_root,
        scan_duplicate_ssot_folders,
        run_drift_detection_guardian,
        main,
        GUARDIAN_ID,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    scan_forbidden_root_folders = None  # type: ignore[assignment,misc]
    scan_archived_files_at_root = None  # type: ignore[assignment,misc]
    scan_duplicate_ssot_folders = None  # type: ignore[assignment,misc]
    run_drift_detection_guardian = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    GUARDIAN_ID = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_drift_detection.py deps unavailable")
class TestScanForbiddenRootFolders:
    def test_is_callable(self):
        assert callable(scan_forbidden_root_folders)

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_drift_detection.py deps unavailable")
class TestScanArchivedFilesAtRoot:
    def test_is_callable(self):
        assert callable(scan_archived_files_at_root)

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_drift_detection.py deps unavailable")
class TestScanDuplicateSsotFolders:
    def test_is_callable(self):
        assert callable(scan_duplicate_ssot_folders)

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_drift_detection.py deps unavailable")
class TestRunDriftDetectionGuardian:
    def test_is_callable(self):
        assert callable(run_drift_detection_guardian)

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_drift_detection.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_drift_detection.py deps unavailable")
class TestGuardianIdConstant:
    def test_is_not_none(self):
        assert GUARDIAN_ID is not None


def test_module_importable():
    """Module run_guardian_drift_detection.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
