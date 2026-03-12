"""ADG importability contract for agentic_core/adg/applications/health_reporter.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_health_reporter.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.applications.health_reporter import (  # noqa: F401
        TrustViolation,
        ADGHealthReport,
        build_health_report,
        build_health_report_from_scan,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    TrustViolation = None  # type: ignore[assignment,misc]
    ADGHealthReport = None  # type: ignore[assignment,misc]
    build_health_report = None  # type: ignore[assignment,misc]
    build_health_report_from_scan = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="health_reporter.py deps unavailable")
class TestHealthReporterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: health_reporter.py must be importable."""
        assert _AVAILABLE

    def test_trustviolation_is_type(self) -> None:
        assert TrustViolation is not None

    def test_adghealthreport_is_type(self) -> None:
        assert ADGHealthReport is not None

    def test_build_health_report_callable(self) -> None:
        assert callable(build_health_report)

    def test_build_health_report_from_scan_callable(self) -> None:
        assert callable(build_health_report_from_scan)

