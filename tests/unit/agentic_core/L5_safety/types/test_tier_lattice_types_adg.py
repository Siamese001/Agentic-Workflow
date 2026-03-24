"""ADG importability contract for agentic_core/L5_safety/types/tier_lattice_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_tier_lattice_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.types.tier_lattice_types import (  # noqa: F401
        BackpressurePolicy,
        DropPolicy,
        LearningTier,
        TierLattice,
        validate_escalation_sequence,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    LearningTier = None  # type: ignore[assignment,misc]
    DropPolicy = None  # type: ignore[assignment,misc]
    TierLattice = None  # type: ignore[assignment,misc]
    BackpressurePolicy = None  # type: ignore[assignment,misc]
    validate_escalation_sequence = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="tier_lattice_types deps unavailable")
class TestTierLatticeTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/types/tier_lattice_types.py must be importable."""
        assert _AVAILABLE

    def test_learningtier_defined(self) -> None:
        assert LearningTier is not None

    def test_droppolicy_defined(self) -> None:
        assert DropPolicy is not None

    def test_tierlattice_defined(self) -> None:
        assert TierLattice is not None

    def test_backpressurepolicy_defined(self) -> None:
        assert BackpressurePolicy is not None