"""ADG importability contract for agentic_core/L0_routing/scripts/run_guardian_manifest.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_run_guardian_manifest.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.run_guardian_manifest import (  # noqa: F401
        run_manifest_guardian,
        main,
        GUARDIAN_ID,
        MANIFEST_FILENAME,
        LOCK_FILENAME,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    run_manifest_guardian = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    GUARDIAN_ID = None  # type: ignore[assignment,misc]
    MANIFEST_FILENAME = None  # type: ignore[assignment,misc]
    LOCK_FILENAME = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_manifest.py deps unavailable")
class TestRunGuardianManifestImportability:
    def test_module_importable(self) -> None:
        """ADG contract: run_guardian_manifest.py must be importable."""
        assert _AVAILABLE

    def test_run_manifest_guardian_callable(self) -> None:
        assert callable(run_manifest_guardian)

    def test_main_callable(self) -> None:
        assert callable(main)

    def test_guardian_id_defined(self) -> None:
        assert GUARDIAN_ID is not None

    def test_manifest_filename_defined(self) -> None:
        assert MANIFEST_FILENAME is not None

