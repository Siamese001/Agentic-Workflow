"""W5 — E4 same-authority healing guardrails (repair_decision + routing gates)."""

from __future__ import annotations

import time

import pytest

from agentic_core.L2_execution.healers.confidence_scorer import ConfidenceScore, HealTier
from agentic_core.L2_execution.healers.failure_signal import FailureSignal
from agentic_core.L2_execution.healers.healing_router import HealingRouter
from agentic_core.L2_execution.healers.routing_gates import (
    RoutingContext,
    STRUCTURAL_FAILURE_TYPES,
    apply_routing_gates,
)
from agentic_core.L2_execution.types.l2_v4_contracts import RepairDecision, repair_decision

pytestmark = pytest.mark.unit

# Documented non-healable authority/policy classes (v4 repair table inputs).
NON_HEALABLE_AUTHORITY_CASES: tuple[dict[str, bool], ...] = (
    {"needs_new_authority_or_human": True},
    {"safety_or_policy_breach": True},
    {"same_authority": False},
    {"repairable": False},
    {"snapshot_intact": False},
)

ALLOWED_LOCAL_REPAIR_DECISION_INPUT: dict[str, bool] = {
    "repairable": True,
    "same_authority": True,
    "under_ceilings": True,
    "snapshot_intact": True,
    "has_useful_partial": False,
    "needs_new_authority_or_human": False,
    "safety_or_policy_breach": False,
}


@pytest.mark.parametrize("kwargs", NON_HEALABLE_AUTHORITY_CASES)
def test_repair_decision_blocks_non_same_authority_cases(kwargs: dict[str, bool]) -> None:
    base = dict(ALLOWED_LOCAL_REPAIR_DECISION_INPUT)
    base.update(kwargs)
    decision = repair_decision(**base)
    assert decision != RepairDecision.REPAIR_AND_RETRY
    assert decision in (
        RepairDecision.STOP_NEEDS_HELP_OR_ESCALATE,
        RepairDecision.STOP_REJECTED_QUARANTINE,
        RepairDecision.SEAL_DEGRADED_OR_NEEDS_HELP,
    )


def test_repair_decision_allows_same_authority_local_repair() -> None:
    decision = repair_decision(**ALLOWED_LOCAL_REPAIR_DECISION_INPUT)
    assert decision == RepairDecision.REPAIR_AND_RETRY


def test_structural_gateway_bypass_routes_to_hitl_when_gemini_prohibited() -> None:
    signal = FailureSignal(
        check_id="g2",
        retry_count=0,
        error_code="GATEWAY_BYPASS",
        error_message="",
        lineage_hash="h",
        context_snapshot={},
        source_layer="L2_execution",
        operation="heal",
        timestamp=time.time(),
    )
    tier, gate = apply_routing_gates(
        HealTier.MEDIUM,
        signal,
        RoutingContext(failure_type="GATEWAY_BYPASS", provider_prohibited_gemini=True),
    )
    assert tier == HealTier.HITL
    assert gate == "GATE_2_STRUCTURAL_HITL"


@pytest.mark.parametrize("failure_type", sorted(STRUCTURAL_FAILURE_TYPES))
def test_structural_failure_types_are_recognized(failure_type: str) -> None:
    assert failure_type in STRUCTURAL_FAILURE_TYPES


def test_healing_router_hitl_tier_does_not_dispatch_gemini_repair() -> None:
    router = HealingRouter()
    score = ConfidenceScore(
        score=0.1,
        tier=HealTier.HITL,
        confidence_in_score=0.1,
        reasoning="test",
    )
    signal = FailureSignal(
        check_id="hitl",
        retry_count=0,
        error_code="needs_human",
        error_message="",
        lineage_hash="h",
        context_snapshot={},
        source_layer="L2_execution",
        operation="heal",
        timestamp=time.time(),
    )
    decision = router.route(score, signal)
    assert decision.tier == HealTier.HITL
    result = router.dispatch_to_executor(decision, "bounded review packet")
    assert result["tier"] == "HITL"
    assert result["executor"] == "hitl"


def test_v4_invariant_bounded_repair_only_documented() -> None:
    from agentic_core.L2_execution.types import l2_v4_contracts as v4

    texts = [inv.description for inv in v4.L2_FULL_INVARIANTS]
    assert any("same-authority" in t for t in texts)
