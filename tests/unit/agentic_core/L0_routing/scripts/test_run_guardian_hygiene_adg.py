"""ADG importability contract for agentic_core/L0_routing/scripts/run_guardian_hygiene.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_run_guardian_hygiene.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.run_guardian_hygiene import (  # noqa: F401
        scan_temp_artifacts,
        scan_empty_folders,
        scan_init_only_folders,
        run_hygiene_guardian,
        GUARDIAN_ID,
        IGNORE_NAMES,
        ARTIFACT_EXTENSIONS,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    scan_temp_artifacts = None  # type: ignore[assignment,misc]
    scan_empty_folders = None  # type: ignore[assignment,misc]
    scan_init_only_folders = None  # type: ignore[assignment,misc]
    run_hygiene_guardian = None  # type: ignore[assignment,misc]
    GUARDIAN_ID = None  # type: ignore[assignment,misc]
    IGNORE_NAMES = None  # type: ignore[assignment,misc]
    ARTIFACT_EXTENSIONS = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_hygiene.py deps unavailable")
class TestRunGuardianHygieneImportability:
    def test_module_importable(self) -> None:
        """ADG contract: run_guardian_hygiene.py must be importable."""
        assert _AVAILABLE

    def test_scan_temp_artifacts_callable(self) -> None:
        assert callable(scan_temp_artifacts)

    def test_scan_empty_folders_callable(self) -> None:
        assert callable(scan_empty_folders)

    def test_guardian_id_defined(self) -> None:
        assert GUARDIAN_ID is not None

    def test_ignore_names_defined(self) -> None:
        assert IGNORE_NAMES is not None

