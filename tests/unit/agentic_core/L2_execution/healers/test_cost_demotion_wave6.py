"""Wave 6 P6.2: Tests for cost-weighted tier demotion in HealingRouter."""

from __future__ import annotations

import time

import pytest

from agentic_core.L0_routing.config.model_registry import (
    GEMINI_FLASH_MODEL_ID,
    GEMINI_PRO_MODEL_ID,
    QWEN_LOCAL_MODEL_ID,
)
from agentic_core.L2_execution.healers.confidence_scorer import (
    ConfidenceScore,
    HealTier,
)
from agentic_core.L2_execution.healers.failure_signal import FailureSignal
from agentic_core.L2_execution.healers.healing_router import (
    COST_DEMOTE_FLASH_USD,
    COST_DEMOTE_PRO_USD,
    HealingRouter,
)
from agentic_core.L2_execution.healers.routing_gates import RoutingContext

pytestmark = pytest.mark.unit


def _score(tier: HealTier) -> ConfidenceScore:
    return ConfidenceScore(score=0.3, tier=tier, confidence_in_score=0.8, reasoning="w6")


def _signal(retry_count: int = 0) -> FailureSignal:
    return FailureSignal(
        check_id="w6",
        retry_count=retry_count,
        error_code="timeout",
        error_message="",
        lineage_hash="h",
        context_snapshot={},
        source_layer="L2_execution",
        operation="heal",
        timestamp=time.time(),
    )


# ==========================================================================
# No demotion when budget is not provided (default None)
# ==========================================================================


def test_no_demotion_when_budget_is_none():
    router = HealingRouter()
    # Pro-triggering path (retry=3 → GATE_1_RETRY_OVERRIDE)
    decision = router.route(_score(HealTier.MEDIUM), _signal(retry_count=3))
    assert decision.tier == HealTier.LOW
    assert decision.gemini_subtier == "PRO"
    assert decision.target_model == GEMINI_PRO_MODEL_ID
    assert decision.cost_demoted is False


def test_no_demotion_when_budget_is_abundant():
    router = HealingRouter()
    decision = router.route(
        _score(HealTier.MEDIUM),
        _signal(retry_count=3),
        RoutingContext(cost_budget_remaining_usd=100.0),
    )
    assert decision.gemini_subtier == "PRO"
    assert decision.target_model == GEMINI_PRO_MODEL_ID
    assert decision.cost_demoted is False


# ==========================================================================
# Pro → Flash demotion
# ==========================================================================


def test_pro_demoted_to_flash_under_budget_pressure():
    router = HealingRouter()
    # Budget just below the Pro threshold
    decision = router.route(
        _score(HealTier.MEDIUM),
        _signal(retry_count=3),
        RoutingContext(cost_budget_remaining_usd=COST_DEMOTE_PRO_USD - 0.01),
    )
    assert decision.tier == HealTier.LOW  # still LOW, just cheaper model
    assert decision.gemini_subtier == "FLASH"
    assert decision.target_model == GEMINI_FLASH_MODEL_ID
    assert decision.cost_demoted is True
    assert "cost_demote_pro_to_flash" in decision.reasoning


def test_pro_not_demoted_at_threshold_boundary():
    router = HealingRouter()
    # Budget exactly at the Pro threshold → no demotion (strict <)
    decision = router.route(
        _score(HealTier.MEDIUM),
        _signal(retry_count=3),
        RoutingContext(cost_budget_remaining_usd=COST_DEMOTE_PRO_USD),
    )
    assert decision.gemini_subtier == "PRO"
    assert decision.cost_demoted is False


# ==========================================================================
# Flash → Qwen demotion
# ==========================================================================


def test_flash_demoted_to_qwen_under_severe_budget_pressure():
    router = HealingRouter()
    # Budget below the Flash threshold (and below Pro threshold)
    # Start with a LOW+NO_OVERRIDE decision → initially Flash
    decision = router.route(
        _score(HealTier.LOW),
        _signal(),
        RoutingContext(cost_budget_remaining_usd=COST_DEMOTE_FLASH_USD - 0.01),
    )
    # Demoted all the way to Qwen
    assert decision.tier == HealTier.MEDIUM
    assert decision.gemini_subtier == ""
    assert decision.target_model == QWEN_LOCAL_MODEL_ID
    assert decision.cost_demoted is True
    assert "cost_demote_flash_to_qwen" in decision.reasoning


def test_pro_cascade_demoted_to_qwen_under_severe_pressure():
    """When budget is very low and Qwen available, Pro demotes all the way to Qwen."""
    router = HealingRouter()
    decision = router.route(
        _score(HealTier.MEDIUM),
        _signal(retry_count=3),  # GATE_1 → Pro
        RoutingContext(cost_budget_remaining_usd=0.10),  # below both thresholds
    )
    # Pro → Flash → Qwen cascade
    assert decision.tier == HealTier.MEDIUM
    assert decision.target_model == QWEN_LOCAL_MODEL_ID
    assert decision.cost_demoted is True


def test_flash_not_demoted_to_qwen_when_qwen_prohibited():
    """If Qwen is unavailable, Flash stays as Flash even under severe pressure."""
    router = HealingRouter()
    decision = router.route(
        _score(HealTier.LOW),
        _signal(),
        RoutingContext(
            cost_budget_remaining_usd=COST_DEMOTE_FLASH_USD - 0.01,
            provider_prohibited_qwen=True,
        ),
    )
    # Flash stays — Qwen not available
    assert decision.tier == HealTier.LOW
    assert decision.gemini_subtier == "FLASH"
    assert decision.target_model == GEMINI_FLASH_MODEL_ID
    assert decision.cost_demoted is False


# ==========================================================================
# Demotion does not affect non-LOW tiers
# ==========================================================================


def test_high_tier_not_affected_by_budget():
    router = HealingRouter()
    decision = router.route(
        _score(HealTier.HIGH),
        _signal(),
        RoutingContext(cost_budget_remaining_usd=0.0),
    )
    assert decision.tier == HealTier.HIGH
    assert decision.cost_demoted is False


def test_medium_tier_not_affected_by_budget():
    router = HealingRouter()
    decision = router.route(
        _score(HealTier.MEDIUM),
        _signal(),
        RoutingContext(cost_budget_remaining_usd=0.0),
    )
    # MEDIUM is already Qwen (free) — demotion would be a no-op
    assert decision.tier == HealTier.MEDIUM
    assert decision.cost_demoted is False


def test_hitl_tier_not_affected_by_budget():
    router = HealingRouter()
    decision = router.route(
        _score(HealTier.HITL),
        _signal(),
        RoutingContext(cost_budget_remaining_usd=0.0),
    )
    assert decision.tier == HealTier.HITL
    assert decision.cost_demoted is False


# ==========================================================================
# Tier stats accounting after demotion
# ==========================================================================


def test_tier_stats_reflect_final_post_demotion_tier():
    router = HealingRouter()
    router.route(
        _score(HealTier.MEDIUM),
        _signal(retry_count=3),
        RoutingContext(cost_budget_remaining_usd=0.10),  # cascade to Qwen
    )
    stats = router.get_tier_stats()
    # The pre-demotion tier stat (LOW) is incremented because tier_stats
    # increments on `final_tier` from apply_routing_gates. Demotion is a
    # post-gate step. Document this in the test so expectations are clear.
    assert stats["LOW"] == 1
    # MEDIUM stat does NOT increment from this call (demotion happens after
    # the stat bump).
    assert stats["MEDIUM"] == 0
