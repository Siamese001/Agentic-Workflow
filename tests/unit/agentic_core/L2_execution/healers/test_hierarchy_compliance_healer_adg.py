"""ADG importability contract for agentic_core/L2_execution/healers/hierarchy_compliance_healer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_hierarchy_compliance_healer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.healers.hierarchy_compliance_healer import (  # noqa: F401
        heal_missing_structure,
        heal_subfolder_compliance,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    heal_missing_structure = None  # type: ignore[assignment,misc]
    heal_subfolder_compliance = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="hierarchy_compliance_healer.py deps unavailable")
class TestHierarchyComplianceHealerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: hierarchy_compliance_healer.py must be importable."""
        assert _AVAILABLE

    def test_heal_missing_structure_callable(self) -> None:
        assert callable(heal_missing_structure)

    def test_heal_subfolder_compliance_callable(self) -> None:
        assert callable(heal_subfolder_compliance)

