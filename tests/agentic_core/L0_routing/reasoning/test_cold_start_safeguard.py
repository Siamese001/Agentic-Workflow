"""Tests for cold_start_safeguard.py module."""

from __future__ import annotations

import math

import pytest

from agentic_core.L0_routing.reasoning.cold_start_safeguard import (
    ColdStartDecision,
    maybe_override_for_cold_start,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    CostTier,
    FallbackEntry,
    RouteId,
)


class TestColdStartDecision:
    """Tests for ColdStartDecision dataclass."""

    def test_cold_start_decision_creation(self):
        """Test creating ColdStartDecision with override."""
        decision = ColdStartDecision(
            overridden=True,
            route_id=RouteId.R3_GROUNDED,
            cost_tier=CostTier.TIER_M,
            fallback_chain_prefix=(FallbackEntry(route_id=RouteId.R1A, cost_tier=CostTier.TIER_S),),
            reason_codes=("cold_start_override",),
        )
        assert decision.overridden is True
        assert decision.route_id == RouteId.R3_GROUNDED
        assert decision.cost_tier == CostTier.TIER_M
        assert len(decision.fallback_chain_prefix) == 1
        assert decision.reason_codes == ("cold_start_override",)

    def test_cold_start_decision_no_override(self):
        """Test creating ColdStartDecision without override."""
        decision = ColdStartDecision(
            overridden=False,
            route_id=RouteId.R1A,
            cost_tier=CostTier.TIER_S,
            fallback_chain_prefix=(),
            reason_codes=(),
        )
        assert decision.overridden is False
        assert decision.route_id == RouteId.R1A
        assert len(decision.fallback_chain_prefix) == 0
        assert len(decision.reason_codes) == 0

    def test_cold_start_decision_is_frozen(self):
        """Test that ColdStartDecision is frozen."""
        decision = ColdStartDecision(
            overridden=False,
            route_id=RouteId.R1A,
            cost_tier=CostTier.TIER_S,
            fallback_chain_prefix=(),
            reason_codes=(),
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            decision.overridden = True


class TestMaybeOverrideForColdStart:
    """Tests for maybe_override_for_cold_start function."""

    def test_high_confidence_no_override(self):
        """Test that high confidence does not trigger override."""
        decision = maybe_override_for_cold_start(
            top_pick=RouteId.R1A,
            top_pick_tier=CostTier.TIER_S,
            classifier_confidence=0.9,
            cold_start_threshold=0.5,
        )
        assert decision.overridden is False
        assert decision.route_id == RouteId.R1A
        assert decision.cost_tier == CostTier.TIER_S

    def test_low_confidence_triggers_override(self):
        """Test that low confidence triggers override to conservative route."""
        decision = maybe_override_for_cold_start(
            top_pick=RouteId.R1A,
            top_pick_tier=CostTier.TIER_S,
            classifier_confidence=0.3,
            cold_start_threshold=0.5,
        )
        assert decision.overridden is True
        assert decision.route_id == RouteId.R3_GROUNDED
        assert decision.cost_tier == CostTier.TIER_M
        assert len(decision.fallback_chain_prefix) == 1
        assert decision.fallback_chain_prefix[0].route_id == RouteId.R1A
        assert decision.fallback_chain_prefix[0].cost_tier == CostTier.TIER_S
        assert decision.reason_codes == ("cold_start_override",)

    def test_confidence_at_threshold_no_override(self):
        """Test that confidence at threshold does not trigger override."""
        decision = maybe_override_for_cold_start(
            top_pick=RouteId.R1A,
            top_pick_tier=CostTier.TIER_S,
            classifier_confidence=0.5,
            cold_start_threshold=0.5,
        )
        assert decision.overridden is False
        assert decision.route_id == RouteId.R1A

    def test_terminal_route_r1a_no_override(self):
        """Test that terminal route R1A is never overridden."""
        decision = maybe_override_for_cold_start(
            top_pick=RouteId.R1A,
            top_pick_tier=CostTier.TIER_S,
            classifier_confidence=0.1,
            cold_start_threshold=0.5,
        )
        assert decision.overridden is False
        assert decision.route_id == RouteId.R1A

    def test_terminal_route_r1b_no_override(self):
        """Test that terminal route R1B is never overridden."""
        decision = maybe_override_for_cold_start(
            top_pick=RouteId.R1B,
            top_pick_tier=CostTier.TIER_S,
            classifier_confidence=0.1,
            cold_start_threshold=0.5,
        )
        assert decision.overridden is False
        assert decision.route_id == RouteId.R1B

    def test_terminal_route_r5_fallback_no_override(self):
        """Test that terminal route R5_FALLBACK is never overridden."""
        decision = maybe_override_for_cold_start(
            top_pick=RouteId.R5_FALLBACK,
            top_pick_tier=CostTier.TIER_S,
            classifier_confidence=0.1,
            cold_start_threshold=0.5,
        )
        assert decision.overridden is False
        assert decision.route_id == RouteId.R5_FALLBACK

    def test_already_conservative_no_override(self):
        """Test that if top pick is already conservative, no override."""
        decision = maybe_override_for_cold_start(
            top_pick=RouteId.R3_GROUNDED,
            top_pick_tier=CostTier.TIER_M,
            classifier_confidence=0.1,
            cold_start_threshold=0.5,
        )
        assert decision.overridden is False
        assert decision.route_id == RouteId.R3_GROUNDED
        assert decision.cost_tier == CostTier.TIER_M
        assert decision.reason_codes == ("cold_start_already_conservative",)

    def test_custom_conservative_route(self):
        """Test using custom conservative route."""
        decision = maybe_override_for_cold_start(
            top_pick=RouteId.R1A,
            top_pick_tier=CostTier.TIER_S,
            classifier_confidence=0.3,
            cold_start_threshold=0.5,
            conservative_route=RouteId.R1B,
            conservative_tier=CostTier.TIER_S,
        )
        assert decision.overridden is True
        assert decision.route_id == RouteId.R1B
        assert decision.cost_tier == CostTier.TIER_S

    def test_invalid_classifier_confidence_nan(self):
        """Test that NaN classifier confidence raises ValueError."""
        with pytest.raises(ValueError, match="must be a finite float"):
            maybe_override_for_cold_start(
                top_pick=RouteId.R1A,
                top_pick_tier=CostTier.TIER_S,
                classifier_confidence=float("nan"),
                cold_start_threshold=0.5,
            )

    def test_invalid_classifier_confidence_inf(self):
        """Test that infinite classifier confidence raises ValueError."""
        with pytest.raises(ValueError, match="must be a finite float"):
            maybe_override_for_cold_start(
                top_pick=RouteId.R1A,
                top_pick_tier=CostTier.TIER_S,
                classifier_confidence=float("inf"),
                cold_start_threshold=0.5,
            )

    def test_invalid_classifier_confidence_range_high(self):
        """Test that classifier confidence > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="out of range \\[0,1\\]"):
            maybe_override_for_cold_start(
                top_pick=RouteId.R1A,
                top_pick_tier=CostTier.TIER_S,
                classifier_confidence=1.5,
                cold_start_threshold=0.5,
            )

    def test_invalid_classifier_confidence_range_low(self):
        """Test that classifier confidence < 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="out of range \\[0,1\\]"):
            maybe_override_for_cold_start(
                top_pick=RouteId.R1A,
                top_pick_tier=CostTier.TIER_S,
                classifier_confidence=-0.1,
                cold_start_threshold=0.5,
            )

    def test_invalid_threshold_nan(self):
        """Test that NaN threshold raises ValueError."""
        with pytest.raises(ValueError, match="must be a finite float"):
            maybe_override_for_cold_start(
                top_pick=RouteId.R1A,
                top_pick_tier=CostTier.TIER_S,
                classifier_confidence=0.5,
                cold_start_threshold=float("nan"),
            )

    def test_invalid_threshold_range_high(self):
        """Test that threshold > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="out of range \\[0,1\\]"):
            maybe_override_for_cold_start(
                top_pick=RouteId.R1A,
                top_pick_tier=CostTier.TIER_S,
                classifier_confidence=0.5,
                cold_start_threshold=1.5,
            )

    def test_invalid_threshold_range_low(self):
        """Test that threshold < 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="out of range \\[0,1\\]"):
            maybe_override_for_cold_start(
                top_pick=RouteId.R1A,
                top_pick_tier=CostTier.TIER_S,
                classifier_confidence=0.5,
                cold_start_threshold=-0.1,
            )

    def test_invalid_top_pick_type(self):
        """Test that non-RouteId top_pick raises TypeError."""
        with pytest.raises(TypeError, match="must be RouteId enum"):
            maybe_override_for_cold_start(
                top_pick="R1A",  # type: ignore
                top_pick_tier=CostTier.TIER_S,
                classifier_confidence=0.5,
                cold_start_threshold=0.5,
            )

    def test_invalid_top_pick_tier_type(self):
        """Test that non-CostTier top_pick_tier raises TypeError."""
        with pytest.raises(TypeError, match="must be CostTier enum"):
            maybe_override_for_cold_start(
                top_pick=RouteId.R1A,
                top_pick_tier="TIER_S",  # type: ignore
                classifier_confidence=0.5,
                cold_start_threshold=0.5,
            )

    def test_invalid_conservative_route_terminal(self):
        """Test that terminal conservative route raises ValueError."""
        with pytest.raises(ValueError, match="must not be a terminal route"):
            maybe_override_for_cold_start(
                top_pick=RouteId.R1A,
                top_pick_tier=CostTier.TIER_S,
                classifier_confidence=0.3,
                cold_start_threshold=0.5,
                conservative_route=RouteId.R1A,
            )

    def test_zero_confidence_override(self):
        """Test that zero confidence triggers override."""
        decision = maybe_override_for_cold_start(
            top_pick=RouteId.R1A,
            top_pick_tier=CostTier.TIER_S,
            classifier_confidence=0.0,
            cold_start_threshold=0.5,
        )
        assert decision.overridden is True
        assert decision.route_id == RouteId.R3_GROUNDED

    def test_one_confidence_no_override(self):
        """Test that confidence of 1.0 does not trigger override."""
        decision = maybe_override_for_cold_start(
            top_pick=RouteId.R1A,
            top_pick_tier=CostTier.TIER_S,
            classifier_confidence=1.0,
            cold_start_threshold=0.5,
        )
        assert decision.overridden is False

    def test_custom_threshold_override(self):
        """Test that custom threshold works correctly."""
        decision = maybe_override_for_cold_start(
            top_pick=RouteId.R1A,
            top_pick_tier=CostTier.TIER_S,
            classifier_confidence=0.6,
            cold_start_threshold=0.7,
        )
        assert decision.overridden is True
        assert decision.route_id == RouteId.R3_GROUNDED
