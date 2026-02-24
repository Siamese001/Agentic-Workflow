"""
L2.3 Healing Tier Dispatcher — Tier Decision -> Provider Invocation Seam.

This module is the SINGLE production point where a HealingDecision.tier
is consumed to invoke the correct healing provider:

  LOCAL_AGENT    -> invoke_local()       (no external LLM call)
  QWEN_VLLM     -> invoke_qwen_vllm()   (Qwen vLLM provider)
  GEMINI_2_5_PRO -> invoke_gemini()      (Gemini 2.5 Pro provider)

The dispatcher accepts an injectable HealingProviderInvoker so tests can
substitute a FakeInvoker that records calls without network access.

Production callers use dispatch_healing() with the default invoker.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
from agentic_core.L2_execution.healers.healing_tier_router import route_healing_tier
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingDecision,
    HealingInput,
    HealingTier,
)

if TYPE_CHECKING:
    from system_learning.ports.healing_outcome_sink import HealingOutcomeSink

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Invocation trace record (immutable, serialisable)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class InvocationRecord:
    """Immutable record of a single provider invocation."""

    tier: HealingTier
    model_id: str
    agent_name: str
    trace_id: str
    heal_confidence: float
    method_called: str


# ---------------------------------------------------------------------------
# Provider invoker protocol (the seam)
# ---------------------------------------------------------------------------


class HealingProviderInvoker(Protocol):
    """Interface for healing provider invocation.

    Production implementations perform real LLM/provider calls.
    Test implementations record calls without network access.
    """

    def invoke_local(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord: ...

    def invoke_qwen_vllm(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord: ...

    def invoke_gemini(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord: ...


# ---------------------------------------------------------------------------
# Default production invoker (stub — real implementations plug in here)
# ---------------------------------------------------------------------------


class DefaultHealingProviderInvoker:
    """Default production invoker.

    Each method returns an InvocationRecord documenting what was invoked.
    In production, the body of each method would call the real provider SDK.
    Currently stubs that record the invocation without network calls.
    """

    def invoke_local(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        return InvocationRecord(
            tier=HealingTier.LOCAL_AGENT,
            model_id="local",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_local",
        )

    def invoke_qwen_vllm(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        return InvocationRecord(
            tier=HealingTier.QWEN_VLLM,
            model_id=config.model_qwen_vllm_id,
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_qwen_vllm",
        )

    def invoke_gemini(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        return InvocationRecord(
            tier=HealingTier.GEMINI_2_5_PRO,
            model_id=config.model_gemini_2_5_pro_id,
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_gemini",
        )


# ---------------------------------------------------------------------------
# Dispatcher — the single E2E path: HealingInput -> tier -> invocation
# ---------------------------------------------------------------------------

_TIER_TO_METHOD: dict[HealingTier, str] = {
    HealingTier.LOCAL_AGENT: "invoke_local",
    HealingTier.QWEN_VLLM: "invoke_qwen_vllm",
    HealingTier.GEMINI_2_5_PRO: "invoke_gemini",
}


def dispatch_healing(
    healing_input: HealingInput,
    config: HealingTierConfig,
    *,
    invoker: HealingProviderInvoker | None = None,
    agent_name: str = "",
    outcome_sink: HealingOutcomeSink | None = None,
    timestamp_utc: int | None = None,
) -> tuple[HealingDecision, InvocationRecord]:
    """End-to-end: route tier, then invoke the matching provider.

    Args:
        healing_input: Structured failure context.
        config: Validated healing tier configuration.
        invoker: Injectable provider invoker (default: DefaultHealingProviderInvoker).
        agent_name: Name of the calling agent (for trace).
        outcome_sink: Optional sink for emitting a HealingOutcomeEvent.
            When None (the default), no emission occurs and behaviour is unchanged.
        timestamp_utc: Deterministic timestamp for the outcome event.
            Required when outcome_sink is provided; ignored otherwise.

    Returns:
        (HealingDecision, InvocationRecord) — the routing decision and invocation trace.
    """
    if invoker is None:
        invoker = DefaultHealingProviderInvoker()

    decision = route_healing_tier(healing_input, config)

    method_name = _TIER_TO_METHOD[decision.tier]
    method = getattr(invoker, method_name)

    success = False
    try:
        record = method(healing_input, decision, config, agent_name=agent_name)
        success = True
    except Exception:
        raise
    finally:
        if outcome_sink is not None and timestamp_utc is not None:
            _emit_outcome(
                outcome_sink,
                healing_input=healing_input,
                decision=decision,
                success=success,
                timestamp_utc=timestamp_utc,
                agent_name=agent_name,
            )

    return decision, record


def _emit_outcome(
    sink: HealingOutcomeSink,
    *,
    healing_input: HealingInput,
    decision: HealingDecision,
    success: bool,
    timestamp_utc: int,
    agent_name: str,
) -> None:
    """Emit exactly one HealingOutcomeEvent to the sink.  Fire-and-forget."""
    from system_learning.types.healing_outcome_types import HealingOutcomeEvent

    event = HealingOutcomeEvent(
        healer_id=agent_name or "unknown",
        tier=decision.tier.value,
        failure_type=healing_input.failure_type,
        success=success,
        timestamp_utc=timestamp_utc,
        trace_id=healing_input.trace_id,
        error_signature=healing_input.error_signature,
    )
    try:
        sink.emit(event)
    except Exception:  # noqa: BLE001
        logger.debug("outcome_sink.emit failed; swallowed to preserve dispatch path")


__all__ = [
    "DefaultHealingProviderInvoker",
    "HealingProviderInvoker",
    "InvocationRecord",
    "dispatch_healing",
]
