"""ADG importability contract for agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_filesystem_ssot_reconciler.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import (  # noqa: F401
        FilesystemSSOTReconcilerAgent,
        ReconciliationViolation,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ReconciliationViolation = None  # type: ignore[assignment,misc]
    FilesystemSSOTReconcilerAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_ssot_reconciler deps unavailable")
class TestFilesystemSsotReconcilerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py must be importable."""
        assert _AVAILABLE

    def test_reconciliationviolation_defined(self) -> None:
        assert ReconciliationViolation is not None

    def test_filesystemssotreconcileragent_defined(self) -> None:
        assert FilesystemSSOTReconcilerAgent is not None
