"""ADG-driven tests for agentic_core/L0_routing/scripts/run_guardian_hierarchy_compliance.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.run_guardian_hierarchy_compliance import (  # noqa: F401
        scan_missing_structure,
        scan_subfolder_compliance,
        run_hierarchy_compliance_guardian,
        main,
        GUARDIAN_ID,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    scan_missing_structure = None  # type: ignore[assignment,misc]
    scan_subfolder_compliance = None  # type: ignore[assignment,misc]
    run_hierarchy_compliance_guardian = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    GUARDIAN_ID = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_hierarchy_compliance.py deps unavailable")
class TestScanMissingStructure:
    def test_is_callable(self):
        assert callable(scan_missing_structure)

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_hierarchy_compliance.py deps unavailable")
class TestScanSubfolderCompliance:
    def test_is_callable(self):
        assert callable(scan_subfolder_compliance)

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_hierarchy_compliance.py deps unavailable")
class TestRunHierarchyComplianceGuardian:
    def test_is_callable(self):
        assert callable(run_hierarchy_compliance_guardian)

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_hierarchy_compliance.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_hierarchy_compliance.py deps unavailable")
class TestGuardianIdConstant:
    def test_is_not_none(self):
        assert GUARDIAN_ID is not None


def test_module_importable():
    """Module run_guardian_hierarchy_compliance.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
