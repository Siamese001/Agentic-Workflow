"""Wave 5 tests: Flash/Pro tier split + Gemini dispatch + Provider enum.

Covers:
  P5.1 — RoutingDecision.gemini_subtier populated based on gate name
  P5.2 — _dispatch_gemini: dry-plan when gateway absent; real call when provisioned
  P5.4 — Provider enum has GEMINI_FLASH and GEMINI_PRO values
"""

from __future__ import annotations

import time

import pytest

from agentic_core.L0_routing.config.model_registry import (
    GEMINI_FLASH_MODEL_ID,
    GEMINI_PRO_MODEL_ID,
)
from agentic_core.L2_execution.healers.confidence_scorer import (
    ConfidenceScore,
    HealTier,
)
from agentic_core.L2_execution.healers.failure_signal import FailureSignal
from agentic_core.L2_execution.healers.healing_router import (
    HealingRouter,
    _PRO_REQUIRED_GATES,
)
from agentic_core.L2_execution.healers.routing_gates import RoutingContext
from agentic_core.L4_state.config.vllm_routing_predicates import Provider

pytestmark = pytest.mark.unit


def _score(tier: HealTier, value: float = 0.3) -> ConfidenceScore:
    return ConfidenceScore(
        score=value,
        tier=tier,
        confidence_in_score=0.8,
        reasoning="w5-test",
    )


def _signal(retry_count: int = 0) -> FailureSignal:
    return FailureSignal(
        check_id="w5",
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
# P5.1 — Flash/Pro subtier populated on RoutingDecision
# ==========================================================================


def test_low_tier_no_override_selects_flash():
    router = HealingRouter()
    decision = router.route(_score(HealTier.LOW), _signal())
    assert decision.tier == HealTier.LOW
    assert decision.gate_applied == "NO_OVERRIDE"
    assert decision.gemini_subtier == "FLASH"
    assert decision.target_model == GEMINI_FLASH_MODEL_ID


def test_low_tier_retry_gate_selects_pro():
    router = HealingRouter()
    decision = router.route(_score(HealTier.MEDIUM), _signal(retry_count=3))
    # Gate 1 forces LOW
    assert decision.tier == HealTier.LOW
    assert decision.gate_applied == "GATE_1_RETRY_OVERRIDE"
    assert decision.gemini_subtier == "PRO"
    assert decision.target_model == GEMINI_PRO_MODEL_ID


def test_low_tier_structural_gate_selects_pro():
    router = HealingRouter()
    decision = router.route(
        _score(HealTier.MEDIUM),
        _signal(),
        RoutingContext(failure_type="LAYER_VIOLATION"),
    )
    assert decision.tier == HealTier.LOW
    assert decision.gate_applied == "GATE_2_STRUCTURAL_NO_DET_COV"
    assert decision.gemini_subtier == "PRO"
    assert decision.target_model == GEMINI_PRO_MODEL_ID


def test_low_tier_qwen_disallowed_selects_pro():
    router = HealingRouter()
    decision = router.route(
        _score(HealTier.MEDIUM),
        _signal(),
        RoutingContext(failure_type="IMPORT_BOUNDARY_VIOLATION"),
    )
    assert decision.tier == HealTier.LOW
    assert decision.gate_applied == "QWEN_DISALLOWED"
    assert decision.gemini_subtier == "PRO"
    assert decision.target_model == GEMINI_PRO_MODEL_ID


def test_high_tier_has_no_subtier():
    router = HealingRouter()
    decision = router.route(_score(HealTier.HIGH), _signal())
    assert decision.gemini_subtier == ""


def test_medium_tier_has_no_subtier():
    router = HealingRouter()
    decision = router.route(_score(HealTier.MEDIUM), _signal())
    assert decision.gemini_subtier == ""


def test_pro_required_gates_frozenset_is_correct():
    # Sanity: all structural/retry/hard-override gates demand Pro.
    expected_pro = {
        "GATE_1_RETRY_OVERRIDE",
        "GATE_1_RETRY_OVERRIDE_HITL",
        "GATE_2_STRUCTURAL_NO_DET_COV",
        "GATE_2_STRUCTURAL_HITL",
        "GATE_4_HARD_OVERRIDE",
        "GATE_4_HARD_OVERRIDE_HITL",
        "QWEN_DISALLOWED",
        "QWEN_DISALLOWED_HITL",
    }
    assert _PRO_REQUIRED_GATES == frozenset(expected_pro)


# ==========================================================================
# P5.2 — _dispatch_gemini
# ==========================================================================


def test_dispatch_gemini_flash_dry_plan_when_gateway_absent():
    router = HealingRouter()
    decision = router.route(_score(HealTier.LOW), _signal())
    result = router.dispatch_to_executor(decision, prompt="x")
    assert result["executor"] == "gemini_flash"
    assert result["gemini_subtier"] == "FLASH"
    assert result["dry_plan"] is True
    assert result["error"] == "gemini_gateway_not_provisioned"


def test_dispatch_gemini_pro_dry_plan_when_gateway_absent():
    router = HealingRouter()
    decision = router.route(_score(HealTier.MEDIUM), _signal(retry_count=3))
    result = router.dispatch_to_executor(decision, prompt="x")
    assert result["executor"] == "gemini_pro"
    assert result["gemini_subtier"] == "PRO"
    assert result["dry_plan"] is True
    assert result["model_used"] == GEMINI_PRO_MODEL_ID


class _MockGeminiGateway:
    """Minimal mock providing route_generation(request) -> response."""

    def __init__(self, content: str = "ok", model: str = "mock-gemini"):
        self._content = content
        self._model = model
        self.calls: list[dict] = []

    async def route_generation(self, request):
        self.calls.append(
            {
                "prompt": request.prompt,
                "model": request.model,
                "provider": request.provider,
                "agent_id": request.agent_id,
            }
        )

        class _Resp:
            def __init__(self, content: str, model: str):
                self.content = content
                self.model = model

        return _Resp(self._content, self._model)


def test_dispatch_gemini_with_injected_gateway_succeeds():
    router = HealingRouter()
    router._gemini_gateway = _MockGeminiGateway(content="fixed", model="mock-gemini")

    decision = router.route(_score(HealTier.LOW), _signal())
    result = router.dispatch_to_executor(decision, prompt="please fix")

    assert result["success"] is True
    assert result["executor"] == "gemini_flash"
    assert result["response"] == "fixed"
    assert result["model_used"] == "mock-gemini"
    assert result["gemini_subtier"] == "FLASH"
    # Verify the gateway was called with Flash model id
    assert len(router._gemini_gateway.calls) == 1
    call = router._gemini_gateway.calls[0]
    assert call["model"] == GEMINI_FLASH_MODEL_ID
    assert call["provider"] == "google"


def test_dispatch_gemini_with_injected_gateway_handles_runtime_error():
    class _FailGateway:
        async def route_generation(self, request):
            raise RuntimeError("provider unreachable")

    router = HealingRouter()
    router._gemini_gateway = _FailGateway()

    decision = router.route(_score(HealTier.LOW), _signal())
    result = router.dispatch_to_executor(decision, prompt="x")

    assert result["success"] is False
    assert result["executor"] == "gemini_flash"
    assert "RuntimeError" in (result["error"] or "")
    assert "provider unreachable" in (result["error"] or "")


# ==========================================================================
# P5.4 — Provider enum extension
# ==========================================================================


def test_provider_enum_has_gemini_flash_and_pro():
    assert Provider.GEMINI_FLASH.value == "gemini_flash"
    assert Provider.GEMINI_PRO.value == "gemini_pro"


def test_provider_enum_retains_backward_compat():
    # OPUS and LOCAL_VLLM must still exist for existing callers (6 apps).
    assert Provider.OPUS.value == "opus"
    assert Provider.LOCAL_VLLM.value == "local_vllm"
    # Expected total: 4 providers
    assert {p.name for p in Provider} == {"OPUS", "LOCAL_VLLM", "GEMINI_FLASH", "GEMINI_PRO"}
