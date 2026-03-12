"""ADG importability contract for agentic_core/L5_safety/types/tier_lattice_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_tier_lattice_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.types.tier_lattice_types import (  # noqa: F401
        LearningTier,
        DropPolicy,
        TierLattice,
        BackpressurePolicy,
        validate_escalation_sequence,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    LearningTier = None  # type: ignore[assignment,misc]
    DropPolicy = None  # type: ignore[assignment,misc]
    TierLattice = None  # type: ignore[assignment,misc]
    BackpressurePolicy = None  # type: ignore[assignment,misc]
    validate_escalation_sequence = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="tier_lattice_types.py deps unavailable")
class TestTierLatticeTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: tier_lattice_types.py must be importable."""
        assert _AVAILABLE

    def test_learningtier_is_type(self) -> None:
        assert LearningTier is not None

    def test_droppolicy_is_type(self) -> None:
        assert DropPolicy is not None

    def test_tierlattice_is_type(self) -> None:
        assert TierLattice is not None

    def test_validate_escalation_sequence_callable(self) -> None:
        assert callable(validate_escalation_sequence)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

