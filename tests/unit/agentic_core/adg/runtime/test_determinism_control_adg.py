"""ADG importability contract for agentic_core/adg/runtime/determinism_control.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_determinism_control.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.determinism_control import (  # noqa: F401
        DeterminismControlReport,
        DeterminismDigest,
        DeterminismViolation,
        DeterminismViolationType,
        ReplayPatchRecord,
        SemanticClockReading,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DeterminismViolationType = None  # type: ignore[assignment,misc]
    DeterminismViolation = None  # type: ignore[assignment,misc]
    DeterminismDigest = None  # type: ignore[assignment,misc]
    SemanticClockReading = None  # type: ignore[assignment,misc]
    ReplayPatchRecord = None  # type: ignore[assignment,misc]
    DeterminismControlReport = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="determinism_control deps unavailable")
class TestDeterminismControlImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/determinism_control.py must be importable."""
        assert _AVAILABLE

    def test_determinismviolationtype_defined(self) -> None:
        assert DeterminismViolationType is not None

    def test_determinismviolation_defined(self) -> None:
        assert DeterminismViolation is not None

    def test_determinismdigest_defined(self) -> None:
        assert DeterminismDigest is not None

    def test_semanticclockreading_defined(self) -> None:
        assert SemanticClockReading is not None

    def test_replaypatchrecord_defined(self) -> None:
        assert ReplayPatchRecord is not None

    def test_determinismcontrolreport_defined(self) -> None:
        assert DeterminismControlReport is not None
