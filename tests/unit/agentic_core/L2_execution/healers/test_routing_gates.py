"""Unit tests for L2 routing_gates (Wave 2 P2.1).

Covers Gate 0-4 + Qwen-disallowed post-filter + provider-prohibited fallbacks.
"""

from __future__ import annotations

import time

import pytest

from agentic_core.L2_execution.healers.confidence_scorer import HealTier
from agentic_core.L2_execution.healers.failure_signal import (
    FailureSignal,
    HealFailureClass,
)
from agentic_core.L2_execution.healers.routing_gates import (
    RoutingContext,
    STRUCTURAL_FAILURE_TYPES,
    apply_routing_gates,
)

pytestmark = pytest.mark.unit


def _signal(
    retry_count: int = 0,
    error_code: str = "timeout",
    budget_remaining: float = 1.0,
    failure_class: HealFailureClass = HealFailureClass.UNKNOWN,
) -> FailureSignal:
    return FailureSignal(
        check_id="c1",
        retry_count=retry_count,
        error_code=error_code,
        error_message="",
        lineage_hash="abcd1234",
        context_snapshot={},
        source_layer="L2_execution",
        operation="heal",
        timestamp=time.time(),
        failure_class=failure_class,
        budget_remaining=budget_remaining,
    )


# ==========================================================================
# Gate 0 — REPLAY
# ==========================================================================


def test_gate0_replay_mode_forces_high_tier():
    tier, gate = apply_routing_gates(
        HealTier.LOW,
        _signal(retry_count=5),
        RoutingContext(replay_mode=True, provider_prohibited_gemini=True),
    )
    assert tier == HealTier.HIGH
    assert gate == "GATE_0_REPLAY"


def test_gate0_replay_overrides_everything():
    """Replay wins over structural failure + retry + provider prohibition."""
    tier, gate = apply_routing_gates(
        HealTier.LOW,
        _signal(retry_count=10),
        RoutingContext(
            replay_mode=True,
            failure_type="LAYER_VIOLATION",
            provider_prohibited_gemini=True,
            provider_prohibited_qwen=True,
        ),
    )
    assert tier == HealTier.HIGH
    assert gate == "GATE_0_REPLAY"


# ==========================================================================
# Gate 1 — RETRY EXHAUSTION
# ==========================================================================


def test_gate1_retry_3_escalates_to_low():
    tier, gate = apply_routing_gates(HealTier.MEDIUM, _signal(retry_count=3), RoutingContext())
    assert tier == HealTier.LOW
    assert gate == "GATE_1_RETRY_OVERRIDE"


def test_gate1_retry_3_with_gemini_prohibited_goes_hitl():
    tier, gate = apply_routing_gates(
        HealTier.HIGH,
        _signal(retry_count=4),
        RoutingContext(provider_prohibited_gemini=True),
    )
    assert tier == HealTier.HITL
    assert gate == "GATE_1_RETRY_OVERRIDE_HITL"


def test_gate1_retry_2_does_not_trigger():
    tier, gate = apply_routing_gates(HealTier.HIGH, _signal(retry_count=2), RoutingContext())
    assert tier == HealTier.HIGH
    assert gate == "NO_OVERRIDE"


# ==========================================================================
# Gate 2 — STRUCTURAL FAILURE
# ==========================================================================


@pytest.mark.parametrize("ftype", sorted(STRUCTURAL_FAILURE_TYPES))
def test_gate2_structural_no_coverage_escalates(ftype):
    tier, gate = apply_routing_gates(
        HealTier.HIGH,
        _signal(),
        RoutingContext(failure_type=ftype),
    )
    assert tier == HealTier.LOW
    assert gate == "GATE_2_STRUCTURAL_NO_DET_COV"


def test_gate2_structural_with_coverage_uses_deterministic():
    tier, gate = apply_routing_gates(
        HealTier.LOW,
        _signal(),
        RoutingContext(failure_type="LAYER_VIOLATION", deterministic_coverage=True),
    )
    assert tier == HealTier.HIGH
    assert gate == "GATE_2_STRUCTURAL_DET_COV"


def test_gate2_structural_with_gemini_prohibited_goes_hitl():
    tier, gate = apply_routing_gates(
        HealTier.MEDIUM,
        _signal(),
        RoutingContext(failure_type="GATEWAY_BYPASS", provider_prohibited_gemini=True),
    )
    assert tier == HealTier.HITL
    assert gate == "GATE_2_STRUCTURAL_HITL"


# ==========================================================================
# Gate 4 — HARD OVERRIDE (budget pressure + retry)
# ==========================================================================


def test_gate4_low_budget_plus_retry_escalates():
    tier, gate = apply_routing_gates(
        HealTier.HIGH,
        _signal(retry_count=1, budget_remaining=0.05),
        RoutingContext(),
    )
    assert tier == HealTier.LOW
    assert gate == "GATE_4_HARD_OVERRIDE"


def test_gate4_budget_pressure_with_deterministic_coverage_does_not_trigger():
    tier, gate = apply_routing_gates(
        HealTier.HIGH,
        _signal(retry_count=1, budget_remaining=0.05),
        RoutingContext(deterministic_coverage=True),
    )
    # Gate 4 suppressed; no other gate applies → NO_OVERRIDE
    assert tier == HealTier.HIGH
    assert gate == "NO_OVERRIDE"


def test_gate4_both_providers_prohibited_goes_hitl():
    tier, gate = apply_routing_gates(
        HealTier.MEDIUM,
        _signal(retry_count=2, budget_remaining=0.02),
        RoutingContext(provider_prohibited_gemini=True, provider_prohibited_qwen=True),
    )
    assert tier == HealTier.HITL
    assert gate == "GATE_4_HARD_OVERRIDE_HITL"


# ==========================================================================
# QWEN-DISALLOWED POST-FILTER
# ==========================================================================


def test_qwen_disallowed_import_boundary_escalates_from_medium():
    tier, gate = apply_routing_gates(
        HealTier.MEDIUM,
        _signal(),
        RoutingContext(failure_type="IMPORT_BOUNDARY_VIOLATION"),
    )
    assert tier == HealTier.LOW
    assert gate == "QWEN_DISALLOWED"


def test_qwen_disallowed_with_gemini_prohibited_goes_hitl():
    tier, gate = apply_routing_gates(
        HealTier.MEDIUM,
        _signal(),
        RoutingContext(
            failure_type="SCHEMA_REQUIRED_FIELDS_MISSING",
            provider_prohibited_gemini=True,
        ),
    )
    assert tier == HealTier.HITL
    assert gate == "QWEN_DISALLOWED_HITL"


def test_qwen_disallowed_does_not_trigger_on_non_medium():
    # Initial HIGH tier not affected by Qwen disallow post-filter
    tier, gate = apply_routing_gates(
        HealTier.HIGH,
        _signal(),
        RoutingContext(failure_type="IMPORT_BOUNDARY_VIOLATION"),
    )
    assert tier == HealTier.HIGH
    assert gate == "NO_OVERRIDE"


# ==========================================================================
# PROVIDER-UNAVAILABLE FALLBACKS
# ==========================================================================


def test_medium_with_qwen_prohibited_falls_back_to_low():
    tier, gate = apply_routing_gates(
        HealTier.MEDIUM,
        _signal(),
        RoutingContext(provider_prohibited_qwen=True),
    )
    assert tier == HealTier.LOW
    assert gate == "QWEN_UNAVAILABLE_FALLBACK"


def test_medium_both_providers_prohibited_goes_hitl():
    tier, gate = apply_routing_gates(
        HealTier.MEDIUM,
        _signal(),
        RoutingContext(provider_prohibited_qwen=True, provider_prohibited_gemini=True),
    )
    assert tier == HealTier.HITL
    assert gate == "QWEN_UNAVAILABLE_HITL"


def test_low_with_gemini_prohibited_goes_hitl():
    tier, gate = apply_routing_gates(
        HealTier.LOW,
        _signal(),
        RoutingContext(provider_prohibited_gemini=True),
    )
    assert tier == HealTier.HITL
    assert gate == "GEMINI_UNAVAILABLE_HITL"


# ==========================================================================
# NO-OVERRIDE BASELINE
# ==========================================================================


def test_no_context_preserves_initial_tier():
    tier, gate = apply_routing_gates(HealTier.MEDIUM, _signal(), None)
    assert tier == HealTier.MEDIUM
    assert gate == "NO_OVERRIDE"


def test_empty_context_preserves_initial_tier():
    for initial in [HealTier.HIGH, HealTier.MEDIUM, HealTier.LOW, HealTier.HITL]:
        tier, gate = apply_routing_gates(initial, _signal(), RoutingContext())
        assert tier == initial
        assert gate == "NO_OVERRIDE"
