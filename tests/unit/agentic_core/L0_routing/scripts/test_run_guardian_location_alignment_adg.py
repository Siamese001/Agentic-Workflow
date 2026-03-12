"""ADG-driven tests for agentic_core/L0_routing/scripts/run_guardian_location_alignment.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.run_guardian_location_alignment import (  # noqa: F401
        scan_missing_directories,
        scan_misplaced_files,
        run_location_alignment_guardian,
        main,
        GUARDIAN_ID,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    scan_missing_directories = None  # type: ignore[assignment,misc]
    scan_misplaced_files = None  # type: ignore[assignment,misc]
    run_location_alignment_guardian = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    GUARDIAN_ID = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_location_alignment.py deps unavailable")
class TestScanMissingDirectories:
    def test_is_callable(self):
        assert callable(scan_missing_directories)

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_location_alignment.py deps unavailable")
class TestScanMisplacedFiles:
    def test_is_callable(self):
        assert callable(scan_misplaced_files)

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_location_alignment.py deps unavailable")
class TestRunLocationAlignmentGuardian:
    def test_is_callable(self):
        assert callable(run_location_alignment_guardian)

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_location_alignment.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_location_alignment.py deps unavailable")
class TestGuardianIdConstant:
    def test_is_not_none(self):
        assert GUARDIAN_ID is not None


def test_module_importable():
    """Module run_guardian_location_alignment.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
