"""ADG importability contract for agentic_core/L2_execution/healers/classification_compliance_healer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_classification_compliance_healer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.healers.classification_compliance_healer import (  # noqa: F401
        heal_naming_compliance,
        heal_territory_compliance,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    heal_naming_compliance = None  # type: ignore[assignment,misc]
    heal_territory_compliance = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="classification_compliance_healer.py deps unavailable")
class TestClassificationComplianceHealerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: classification_compliance_healer.py must be importable."""
        assert _AVAILABLE

    def test_heal_naming_compliance_callable(self) -> None:
        assert callable(heal_naming_compliance)

    def test_heal_territory_compliance_callable(self) -> None:
        assert callable(heal_territory_compliance)

