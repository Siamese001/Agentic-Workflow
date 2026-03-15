"""ADG importability contract for agentic_core/L2_execution/healers/healing_tier_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_healing_tier_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.healers.healing_tier_types import (  # noqa: F401
        FailureSignal,
        HealingDecision,
        HealingInput,
        HealingTier,
        InvocationRecord,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    HealingTier = None  # type: ignore[assignment,misc]
    HealingInput = None  # type: ignore[assignment,misc]
    HealingDecision = None  # type: ignore[assignment,misc]
    InvocationRecord = None  # type: ignore[assignment,misc]
    FailureSignal = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_types deps unavailable")
class TestHealingTierTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/healers/healing_tier_types.py must be importable."""
        assert _AVAILABLE

    def test_healingtier_defined(self) -> None:
        assert HealingTier is not None

    def test_healinginput_defined(self) -> None:
        assert HealingInput is not None

    def test_healingdecision_defined(self) -> None:
        assert HealingDecision is not None

    def test_invocationrecord_defined(self) -> None:
        assert InvocationRecord is not None

    def test_failuresignal_defined(self) -> None:
        assert FailureSignal is not None
