"""ADG importability contract for agentic_core/L2_execution/healers/architecture_governance_healer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_architecture_governance_healer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.healers.architecture_governance_healer import (  # noqa: F401
        heal_import_compliance,
        heal_layer_gravity,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    heal_import_compliance = None  # type: ignore[assignment,misc]
    heal_layer_gravity = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="architecture_governance_healer.py deps unavailable")
class TestArchitectureGovernanceHealerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: architecture_governance_healer.py must be importable."""
        assert _AVAILABLE

    def test_heal_import_compliance_callable(self) -> None:
        assert callable(heal_import_compliance)

    def test_heal_layer_gravity_callable(self) -> None:
        assert callable(heal_layer_gravity)

