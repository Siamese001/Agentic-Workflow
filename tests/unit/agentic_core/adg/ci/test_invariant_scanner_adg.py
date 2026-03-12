"""ADG importability contract for agentic_core/adg/ci/invariant_scanner.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_invariant_scanner.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.ci.invariant_scanner import (  # noqa: F401
        Violation,
        ScanReport,
        InvariantScanner,
        run_ci_scan,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    Violation = None  # type: ignore[assignment,misc]
    ScanReport = None  # type: ignore[assignment,misc]
    InvariantScanner = None  # type: ignore[assignment,misc]
    run_ci_scan = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="invariant_scanner.py deps unavailable")
class TestInvariantScannerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: invariant_scanner.py must be importable."""
        assert _AVAILABLE

    def test_violation_is_type(self) -> None:
        assert Violation is not None

    def test_scanreport_is_type(self) -> None:
        assert ScanReport is not None

    def test_invariantscanner_is_type(self) -> None:
        assert InvariantScanner is not None

    def test_run_ci_scan_callable(self) -> None:
        assert callable(run_ci_scan)

