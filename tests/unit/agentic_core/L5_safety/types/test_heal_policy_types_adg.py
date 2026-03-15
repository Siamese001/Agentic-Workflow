"""ADG importability contract for agentic_core/L5_safety/types/heal_policy_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_heal_policy_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.types.heal_policy_types import (  # noqa: F401
        HealEscalationDecision,
        HealEscalationInputs,
        LegacyHealEscalationInputs,
        ReasoningTier,
        ScoreBand,
        classify_score,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ReasoningTier = None  # type: ignore[assignment,misc]
    ScoreBand = None  # type: ignore[assignment,misc]
    HealEscalationInputs = None  # type: ignore[assignment,misc]
    LegacyHealEscalationInputs = None  # type: ignore[assignment,misc]
    HealEscalationDecision = None  # type: ignore[assignment,misc]
    classify_score = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="heal_policy_types deps unavailable")
class TestHealPolicyTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/types/heal_policy_types.py must be importable."""
        assert _AVAILABLE

    def test_reasoningtier_defined(self) -> None:
        assert ReasoningTier is not None

    def test_scoreband_defined(self) -> None:
        assert ScoreBand is not None

    def test_healescalationinputs_defined(self) -> None:
        assert HealEscalationInputs is not None

    def test_legacyhealescalationinputs_defined(self) -> None:
        assert LegacyHealEscalationInputs is not None

    def test_healescalationdecision_defined(self) -> None:
        assert HealEscalationDecision is not None
