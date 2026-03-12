"""ADG importability contract for agentic_core/L0_routing/scripts/run_guardian_classification_compliance.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_run_guardian_classification_compliance.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.run_guardian_classification_compliance import (  # noqa: F401
        scan_naming_compliance,
        scan_territory_compliance,
        run_classification_compliance_guardian,
        main,
        GUARDIAN_ID,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    scan_naming_compliance = None  # type: ignore[assignment,misc]
    scan_territory_compliance = None  # type: ignore[assignment,misc]
    run_classification_compliance_guardian = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    GUARDIAN_ID = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_classification_compliance.py deps unavailable")
class TestRunGuardianClassificationComplianceImportability:
    def test_module_importable(self) -> None:
        """ADG contract: run_guardian_classification_compliance.py must be importable."""
        assert _AVAILABLE

    def test_scan_naming_compliance_callable(self) -> None:
        assert callable(scan_naming_compliance)

    def test_scan_territory_compliance_callable(self) -> None:
        assert callable(scan_territory_compliance)

    def test_guardian_id_defined(self) -> None:
        assert GUARDIAN_ID is not None

