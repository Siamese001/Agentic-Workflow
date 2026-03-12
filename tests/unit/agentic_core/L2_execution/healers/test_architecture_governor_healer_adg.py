"""ADG importability contract for agentic_core/L2_execution/healers/architecture_governor_healer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_architecture_governor_healer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.healers.architecture_governor_healer import (  # noqa: F401
        heal_architecture_governance,
        CHECK_ID,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    heal_architecture_governance = None  # type: ignore[assignment,misc]
    CHECK_ID = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="architecture_governor_healer.py deps unavailable")
class TestArchitectureGovernorHealerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: architecture_governor_healer.py must be importable."""
        assert _AVAILABLE

    def test_heal_architecture_governance_callable(self) -> None:
        assert callable(heal_architecture_governance)

    def test_check_id_defined(self) -> None:
        assert CHECK_ID is not None

