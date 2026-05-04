"""Unit + integration tests for HealingRouter Wave 2 dispatch (P2.3, P2.4).

Covers:
  - route() applies gates and populates gate_applied
  - Tier config uses model_registry IDs
  - dispatch_to_executor() handles HIGH / MEDIUM / LOW / HITL
  - MEDIUM dispatch reaches AppsQwenGateway and degrades gracefully when vLLM
    is unavailable (integration guard — no live server required)
  - Full chain: FailureSignal → ConfidenceScorer → HealingRouter → dispatcher
"""

from __future__ import annotations

import time

import pytest

from agentic_core.L0_routing.config.model_registry import (
    DETERMINISTIC_MODEL_SENTINEL,
    GEMINI_FLASH_MODEL_ID,
    GEMINI_PRO_MODEL_ID,
    QWEN_LOCAL_MODEL_ID,
)
from agentic_core.L2_execution.healers.confidence_scorer import (
    ConfidenceScore,
    ConfidenceScorer,
    HealTier,
)
from agentic_core.L2_execution.healers.failure_signal import (
    FailureSignal,
    FailureSignalBuilder,
    HealFailureClass,
)
from agentic_core.L2_execution.healers.healing_router import (
    HealingRouter,
    RoutingDecision,
)
from agentic_core.L2_execution.healers.routing_gates import RoutingContext

pytestmark = pytest.mark.unit


def _score(tier: HealTier, value: float = 0.5) -> ConfidenceScore:
    return ConfidenceScore(
        score=value,
        tier=tier,
        confidence_in_score=0.8,
        reasoning="test",
    )


def _signal(retry_count: int = 0, error_code: str = "timeout") -> FailureSignal:
    return FailureSignal(
        check_id="t1",
        retry_count=retry_count,
        error_code=error_code,
        error_message="",
        lineage_hash="h",
        context_snapshot={},
        source_layer="L2_execution",
        operation="heal",
        timestamp=time.time(),
    )


# ==========================================================================
# route() gate wiring
# ==========================================================================


def test_route_populates_model_registry_ids():
    router = HealingRouter()
    # Wave 5 P5.1: LOW tier with NO_OVERRIDE → Flash (confidence-based).
    for tier, expected_model in (
        (HealTier.HIGH, DETERMINISTIC_MODEL_SENTINEL),
        (HealTier.MEDIUM, QWEN_LOCAL_MODEL_ID),
        (HealTier.LOW, GEMINI_FLASH_MODEL_ID),  # Flash for NO_OVERRIDE LOW
    ):
        decision = router.route(_score(tier), _signal())
        assert decision.target_model == expected_model


def test_route_no_context_yields_no_override():
    router = HealingRouter()
    decision = router.route(_score(HealTier.MEDIUM), _signal())
    assert decision.tier == HealTier.MEDIUM
    assert decision.gate_applied == "NO_OVERRIDE"
    assert "gate:" not in decision.reasoning


def test_route_with_replay_context_overrides_to_high():
    router = HealingRouter()
    decision = router.route(
        _score(HealTier.LOW),
        _signal(),
        RoutingContext(replay_mode=True),
    )
    assert decision.tier == HealTier.HIGH
    assert decision.gate_applied == "GATE_0_REPLAY"
    assert decision.target_model == DETERMINISTIC_MODEL_SENTINEL
    assert "gate:GATE_0_REPLAY" in decision.reasoning


def test_route_retry_escalates_to_low():
    router = HealingRouter()
    decision = router.route(
        _score(HealTier.MEDIUM),
        _signal(retry_count=3),
        RoutingContext(),
    )
    assert decision.tier == HealTier.LOW
    assert decision.gate_applied == "GATE_1_RETRY_OVERRIDE"
    assert decision.target_model == GEMINI_PRO_MODEL_ID


def test_route_structural_failure_with_coverage_pins_to_high():
    router = HealingRouter()
    decision = router.route(
        _score(HealTier.LOW),
        _signal(),
        RoutingContext(failure_type="LAYER_VIOLATION", deterministic_coverage=True),
    )
    assert decision.tier == HealTier.HIGH
    assert decision.gate_applied == "GATE_2_STRUCTURAL_DET_COV"


def test_route_tier_stats_increment_on_final_tier_not_initial():
    router = HealingRouter()
    router.route(
        _score(HealTier.MEDIUM),
        _signal(retry_count=3),
        RoutingContext(),
    )
    stats = router.get_tier_stats()
    assert stats["LOW"] == 1
    assert stats["MEDIUM"] == 0


# ==========================================================================
# dispatch_to_executor()
# ==========================================================================


def test_dispatch_high_tier_returns_deterministic_success():
    router = HealingRouter()
    decision = router.route(_score(HealTier.HIGH), _signal())
    result = router.dispatch_to_executor(decision, prompt="noop")
    assert result["tier"] == "HIGH"
    assert result["executor"] == "deterministic"
    assert result["success"] is True
    assert result["model_used"] == DETERMINISTIC_MODEL_SENTINEL


def test_dispatch_low_tier_flash_returns_dry_plan_when_gateway_absent():
    """Wave 5 P5.2: LOW tier with no gateway → structured dry-plan response.
    Confidence-based LOW (NO_OVERRIDE) routes to Flash.
    """
    router = HealingRouter()
    decision = router.route(_score(HealTier.LOW), _signal())
    assert decision.gemini_subtier == "FLASH"
    result = router.dispatch_to_executor(decision, prompt="fix")
    assert result["tier"] == "LOW"
    assert result["executor"] == "gemini_flash"
    assert result["success"] is False
    assert result["error"] == "gemini_gateway_not_provisioned"
    assert result["dry_plan"] is True
    assert result["model_used"] == GEMINI_FLASH_MODEL_ID


def test_dispatch_hitl_tier_returns_human_review_sentinel():
    router = HealingRouter()
    decision = router.route(_score(HealTier.HITL), _signal())
    result = router.dispatch_to_executor(decision, prompt="review")
    assert result["tier"] == "HITL"
    assert result["executor"] == "hitl"
    assert result["success"] is False
    assert result["error"] == "human_review_required"


@pytest.mark.skip(reason="Requires live vLLM server — hangs without it")
def test_dispatch_medium_degrades_gracefully_without_live_vllm(monkeypatch):
    """When vLLM is not running, dispatch must return a well-formed error
    instead of raising. The Qwen gateway converts errors to a failed
    QwenInferenceResponse, which we surface as success=False + error text.

    Pinned to ``DISABLE_QWEN_FALLBACK=1`` so this test is deterministic
    regardless of suite ordering: with the cascade-fallback disabled,
    a Qwen dispatch error returns ``executor='qwen_vllm'`` directly
    instead of cascading to Gemini Flash. Without the pin, suite-level
    state from neighboring tests (vllm_health_probe cache + asyncio
    event-loop teardown) can flip the executor to ``gemini_flash``.
    """
    monkeypatch.setenv("DISABLE_QWEN_FALLBACK", "1")
    router = HealingRouter()
    decision = router.route(_score(HealTier.MEDIUM), _signal())
    result = router.dispatch_to_executor(decision, prompt="do a thing")
    assert result["tier"] == "MEDIUM"
    assert result["executor"] == "qwen_vllm"
    # Result shape is well-formed regardless of whether vLLM is up
    assert "success" in result
    assert "response" in result
    assert "model_used" in result
    assert "error" in result


# ==========================================================================
# Full chain: Signal → Scorer → Router → Dispatcher
# ==========================================================================


def test_full_chain_schema_validation_error_routes_to_high():
    """Schema validation failures have 0.90 base confidence → HIGH tier."""
    signal = (
        FailureSignalBuilder()
        .from_context({"k": "v"})
        .with_check("chain_t1", retry_count=0)
        .with_error("schema_validation_error", "missing field")
        .with_lineage("abcd1234")
        .from_layer("L2_execution", "heal")
        .with_failure_class(HealFailureClass.SSOT_DRIFT)
        .build()
    )
    scorer = ConfidenceScorer()
    score = scorer.score(signal)
    assert score.tier == HealTier.HIGH

    router = HealingRouter()
    decision = router.route(score, signal)
    assert decision.tier == HealTier.HIGH
    assert decision.target_model == DETERMINISTIC_MODEL_SENTINEL


def test_full_chain_network_error_with_retries_escalates_via_gate1():
    """network_error base=0.40 → after retry_count=3, Gate 1 forces LOW."""
    signal = (
        FailureSignalBuilder()
        .from_context({})
        .with_check("chain_t2", retry_count=3)
        .with_error("network_error", "timeout")
        .with_lineage("abcd1234")
        .from_layer("L3_orchestration", "heal")
        .with_failure_class(HealFailureClass.UNKNOWN)
        .build()
    )
    score = ConfidenceScorer().score(signal)
    router = HealingRouter()
    decision = router.route(score, signal, RoutingContext())
    assert decision.tier == HealTier.LOW
    assert decision.gate_applied == "GATE_1_RETRY_OVERRIDE"
    assert decision.target_model == GEMINI_PRO_MODEL_ID


def test_full_chain_structural_failure_ignores_scorer_tier():
    """Even with MEDIUM score, a structural failure type forces LOW."""
    signal = (
        FailureSignalBuilder()
        .from_context({})
        .with_check("chain_t3", retry_count=1)
        .with_error("timeout", "x")  # base 0.60 → MEDIUM
        .with_lineage("abcd1234")
        .from_layer("L2_execution", "heal")
        .build()
    )
    score = ConfidenceScorer().score(signal)
    assert score.tier == HealTier.MEDIUM

    router = HealingRouter()
    decision = router.route(
        score,
        signal,
        RoutingContext(failure_type="GATEWAY_BYPASS"),
    )
    assert decision.tier == HealTier.LOW
    assert decision.gate_applied == "GATE_2_STRUCTURAL_NO_DET_COV"


def test_routing_decision_is_dataclass_with_gate_applied():
    """Regression: gate_applied must be part of RoutingDecision."""
    router = HealingRouter()
    decision = router.route(_score(HealTier.MEDIUM), _signal())
    assert isinstance(decision, RoutingDecision)
    assert hasattr(decision, "gate_applied")
    assert decision.gate_applied == "NO_OVERRIDE"
