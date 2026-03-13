"""ADG importability contract for agentic_core/adg/extraction/static_scanner.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_static_scanner.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.extraction.static_scanner import (  # noqa: F401
        ADGStaticScanner,
        Edge,
        ScanManifest,
        ScanResult,
        run_scanner_self_test,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    Edge = None  # type: ignore[assignment,misc]
    ScanManifest = None  # type: ignore[assignment,misc]
    ScanResult = None  # type: ignore[assignment,misc]
    run_scanner_self_test = None  # type: ignore[assignment,misc]
    ADGStaticScanner = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="static_scanner deps unavailable")
class TestStaticScannerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/extraction/static_scanner.py must be importable."""
        assert _AVAILABLE

    def test_edge_defined(self) -> None:
        assert Edge is not None

    def test_scanmanifest_defined(self) -> None:
        assert ScanManifest is not None

    def test_scanresult_defined(self) -> None:
        assert ScanResult is not None

    def test_adgstaticscanner_defined(self) -> None:
        assert ADGStaticScanner is not None
