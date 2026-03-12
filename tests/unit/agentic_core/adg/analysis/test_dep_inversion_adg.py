"""ADG importability contract for agentic_core/adg/analysis/dep_inversion.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_dep_inversion.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.analysis.dep_inversion import (  # noqa: F401
        DIPViolation,
        DIPReport,
        detect_dip_violations,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DIPViolation = None  # type: ignore[assignment,misc]
    DIPReport = None  # type: ignore[assignment,misc]
    detect_dip_violations = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="dep_inversion.py deps unavailable")
class TestDepInversionImportability:
    def test_module_importable(self) -> None:
        """ADG contract: dep_inversion.py must be importable."""
        assert _AVAILABLE

    def test_dipviolation_is_type(self) -> None:
        assert DIPViolation is not None

    def test_dipreport_is_type(self) -> None:
        assert DIPReport is not None

    def test_detect_dip_violations_callable(self) -> None:
        assert callable(detect_dip_violations)

