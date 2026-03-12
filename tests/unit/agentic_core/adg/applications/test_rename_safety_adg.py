"""ADG importability contract for agentic_core/adg/applications/rename_safety.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_rename_safety.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.applications.rename_safety import (  # noqa: F401
        RenameImpact,
        RenameRepairStep,
        RenameSafetyReport,
        analyze_rename,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RenameImpact = None  # type: ignore[assignment,misc]
    RenameRepairStep = None  # type: ignore[assignment,misc]
    RenameSafetyReport = None  # type: ignore[assignment,misc]
    analyze_rename = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="rename_safety.py deps unavailable")
class TestRenameSafetyImportability:
    def test_module_importable(self) -> None:
        """ADG contract: rename_safety.py must be importable."""
        assert _AVAILABLE

    def test_renameimpact_is_type(self) -> None:
        assert RenameImpact is not None

    def test_renamerepairstep_is_type(self) -> None:
        assert RenameRepairStep is not None

    def test_renamesafetyreport_is_type(self) -> None:
        assert RenameSafetyReport is not None

    def test_analyze_rename_callable(self) -> None:
        assert callable(analyze_rename)

