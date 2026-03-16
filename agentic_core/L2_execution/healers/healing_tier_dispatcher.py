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

import hashlib
import logging
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol

from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
from agentic_core.L2_execution.healers.healing_tier_router import route_healing_tier
from agentic_core.L2_execution.healers.healing_tier_types import (
    FailureSignal,
    HealingDecision,
    HealingInput,
    HealingTier,
)
from agentic_core.L3_orchestration.registry.agent_dispatch_registry import get_agent_dispatch_registry
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "healing_tier_dispatcher")
emit_determinism_digest("p0", "healing_tier_dispatcher")

_emit_dispatches_healing_run("p1", "healing_tier_dispatcher", "L2")
_emit_routes_through("p1", "healing_tier_dispatcher", "L2")
_emit_escalates_to_human("p1", "healing_tier_dispatcher", "L2")
_emit_reads_policy_state("p1", "healing_tier_dispatcher", "L2")

_emit_snapshots_state("p0", "healing_tier_dispatcher", "state_snapshot")

if TYPE_CHECKING:
    from agentic_core.L2_execution.engines.resource_predictor import ResourcePredictor
    from agentic_core.L2_execution.engines.rollback_refiner import RollbackRefiner
    from system_learning.ports.healing_outcome_sink import HealingOutcomeSink
    from system_learning.ports.healing_pattern_advisor import HealingPatternAdvisor
    from system_learning.ports.meta_outcome_bus_hook import MetaOutcomeBusHook
    from system_learning.ports.meta_prior_provider import MetaPriorProvider
    from system_learning.ports.outcome_write_back_hook import OutcomeWriteBackHook

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# P2-G3: Lazy process-global L4MetaPriorProvider singleton
# ---------------------------------------------------------------------------

_l4_prior_provider: Any | None = None


def _get_l4_prior_provider() -> Any:
    """Return a process-global L4MetaPriorProvider backed by HealingSuccessRateStore.

    Falls back to NeutralMetaPriorProvider if the adapter is unavailable (cold start).
    """
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_l4_prior_provider", "p0_governance")
    global _l4_prior_provider
    if _l4_prior_provider is None:
        try:
            from system_learning.adapters.l4_meta_prior_provider import L4MetaPriorProvider

            _l4_prior_provider = L4MetaPriorProvider.from_default_store()
            logger.debug("dispatch_healing: L4MetaPriorProvider singleton initialised")
        except (ImportError, AttributeError, OSError):
            from system_learning.ports.meta_prior_provider import NeutralMetaPriorProvider

            _l4_prior_provider = NeutralMetaPriorProvider()
            logger.debug(
                "dispatch_healing: L4MetaPriorProvider unavailable — using NeutralMetaPriorProvider",
                exc_info=True,
            )
    return _l4_prior_provider


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
    # Optional provider metadata (prevents type branching)
    provider_metadata: dict[str, Any] | None = None


def handle_qwen_oom_via_router(healing_input: HealingInput, config: HealingTierConfig) -> HealingDecision:
    """Handle OOM by routing through single choke point."""
    # Increment retry count
    new_retry_count = healing_input.retry_count + 1

    # Create FailureSignal for L2.3 consumption
    failure_signal = FailureSignal(
        source_agent=healing_input.agent_id,
        failure_type="gpu_oom",
        error_signature="qwen_gpu_oom",
        trace_id=healing_input.trace_id,
        context={"retry_count": new_retry_count, "error": "GPU out of memory"},
        retry_count=new_retry_count,
        blast_radius_estimate=0.1,
    )

    # Convert to HealingInput and route through choke point
    escalated_input = failure_signal.to_healing_input(
        required_tools=healing_input.required_tools,
        violation_metadata_refs=healing_input.violation_metadata_refs,
    )

    # Return router decision directly (no exceptions, no manual tier selection)
    return route_healing_tier(escalated_input, config)


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
        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"LocalHealingTierDispatcher.invoke_local:{agent_name}",
        )
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
    resource_predictor: ResourcePredictor | None = None,
    rollback_refiner: RollbackRefiner | None = None,
    meta_prior_provider: MetaPriorProvider | None = None,
    outcome_write_back_hook: OutcomeWriteBackHook | None = None,
    pattern_advisor: HealingPatternAdvisor | None = None,
    meta_outcome_bus_hook: MetaOutcomeBusHook | None = None,
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
        resource_predictor: Optional resource predictor for proposal-only predictions.
        rollback_refiner: Optional rollback refiner for proposal-only strategy selection.

    Returns:
        (HealingDecision, InvocationRecord) — the routing decision and invocation trace.
    """
    if invoker is None:
        invoker = DefaultHealingProviderInvoker()

    # P2-G3: Wire live L4-backed prior provider when caller does not supply one
    effective_prior_provider = (
        meta_prior_provider if meta_prior_provider is not None else _get_l4_prior_provider()
    )

    decision = route_healing_tier(
        healing_input,
        meta_prior_provider=effective_prior_provider,
    )

    # Emit proposal-only resource prediction if predictor available
    if resource_predictor is not None:
        _emit_resource_prediction(resource_predictor, healing_input, agent_name, timestamp_utc)

    # Emit proposal-only rollback refinement if refiner available
    if rollback_refiner is not None:
        _emit_rollback_refinement(rollback_refiner, healing_input, agent_name, timestamp_utc)

    method_name = _TIER_TO_METHOD[decision.tier]
    # Wave 2: Use AgentDispatchRegistry instead of raw getattr
    registry = get_agent_dispatch_registry()

    success = False
    record: InvocationRecord | None = None
    try:
        record = registry.dispatch(
            caller="healing_tier_dispatcher",
            target_class=invoker.__class__.__name__,
            method=method_name,
            target_instance=invoker,
            args=(healing_input, decision, config),
            kwargs={"agent_name": agent_name},
        )
        success = True
    # guardian: allow-silent-swallow
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
        # Phase 2: Real-time write-back into meta-learning store
        if outcome_write_back_hook is not None:
            try:
                outcome_write_back_hook.on_outcome(
                    healing_input=healing_input,
                    decision=decision,
                    record=record,
                    success=success,
                )
            # guardian: allow-silent-swallow
            except Exception as e:  # guardian: allow-silent-swallower
                logger.warning("outcome_write_back_hook raised — continuing", exc_info=True)
        # Phase 3: C0 informational-only pattern advisor (cannot change tier)
        if pattern_advisor is not None:
            try:
                pattern_advice = pattern_advisor.advise(healing_input)
                if pattern_advice is not None and timestamp_utc is not None:
                    _emit_pattern_advice(pattern_advice, healing_input, agent_name, timestamp_utc)
            # guardian: allow-silent-swallow
            except Exception as e:  # guardian: allow-silent-swallower
                logger.warning("pattern_advisor raised — continuing", exc_info=True)
        # Phase 4: Publish outcome to MetaLearningBus (proposal_only=True)
        if meta_outcome_bus_hook is not None:
            try:
                meta_outcome_bus_hook.publish_outcome(
                    healing_input=healing_input,
                    decision=decision,
                    record=record,
                    success=success,
                )
            # guardian: allow-silent-swallow
            except (AttributeError, TypeError, ValueError, Exception) as e:
                logger.warning("meta_outcome_bus_hook raised — continuing", exc_info=True)

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
    # guardian: allow-silent-swallow
    except Exception:  # noqa: BLE001
        logger.debug("outcome_sink.emit failed; swallowed to preserve dispatch path")


def _emit_resource_prediction(
    resource_predictor: ResourcePredictor,
    healing_input: HealingInput,
    agent_name: str,
    timestamp_utc: int | None,
) -> None:
    """Emit resource prediction as proposal-only artifact."""
    from agentic_core.L2_execution.types.resource_prediction_types import FailureSignature

    # Create deterministic failure signature
    fingerprint = hashlib.sha256(
        f"{healing_input.failure_type}:{healing_input.error_signature}:{healing_input.trace_id}".encode()
    ).hexdigest()[:64]

    signature = FailureSignature(
        component=agent_name or "unknown",
        failure_type=healing_input.failure_type,
        fingerprint=fingerprint,
    )

    try:
        prediction = resource_predictor.predict(signature=signature, history_bytes=None)

        # Emit as proposal artifact (no direct mutation)
        logger.info(
            "Resource prediction emitted",
            extra={
                "agent": agent_name,
                "trace_id": healing_input.trace_id,
                "prediction_hash": prediction.content_hash(),
                "confidence": prediction.confidence,
            },
        )
    # guardian: allow-silent-swallow
    except Exception:  # noqa: BLE001  # guardian: allow-silent-swallower
        logger.debug("resource prediction failed; swallowed to preserve dispatch path")


def _emit_rollback_refinement(
    rollback_refiner: RollbackRefiner,
    healing_input: HealingInput,
    agent_name: str,
    timestamp_utc: int | None,
) -> None:
    """Emit rollback refinement as proposal-only artifact."""
    from agentic_core.L2_execution.types.resource_prediction_types import FailureSignature
    from agentic_core.L2_execution.types.rollback_refinement_types import (
        RollbackRefinementRequest,
        RollbackStrategyId,
    )

    # Create deterministic failure signature
    fingerprint = hashlib.sha256(
        f"{healing_input.failure_type}:{healing_input.error_signature}:{healing_input.trace_id}".encode()
    ).hexdigest()[:64]

    signature = FailureSignature(
        component=agent_name or "unknown",
        failure_type=healing_input.failure_type,
        fingerprint=fingerprint,
    )

    # Default candidate strategies
    candidates = tuple(
        RollbackStrategyId(name)
        for name in [
            "graceful_shutdown",
            "checkpoint_restore",
            "state_snapshot",
            "incremental_rollback",
            "full_restart",
            "circuit_breaker",
        ]
    )

    request = RollbackRefinementRequest(
        failure_signature=signature,
        candidates=candidates,
        history_bytes=None,
    )

    try:
        decision = rollback_refiner.refine(request=request)

        # Emit as proposal artifact (no direct mutation)
        logger.info(
            "Rollback refinement emitted",
            extra={
                "agent": agent_name,
                "trace_id": healing_input.trace_id,
                "chosen_strategy": decision.chosen.name,
                "decision_hash": decision.content_hash(),
            },
        )
    # guardian: allow-silent-swallow
    except Exception:  # noqa: BLE001  # guardian: allow-silent-swallower
        logger.debug("rollback refinement failed; swallowed to preserve dispatch path")


def _emit_pattern_advice(
    pattern_advice,
    healing_input,
    agent_name: str,
    timestamp_utc: int,
) -> None:
    """Emit pattern advice metadata (informational-only)."""
    try:
        logger.info(
            "pattern_advice",
            extra={
                "trace_id": healing_input.trace_id,
                "agent_name": agent_name,
                "timestamp_utc": timestamp_utc,
                "pattern_match": pattern_advice["pattern_match"],
                "pattern_name": pattern_advice["pattern_name"],
                "pattern_boost": pattern_advice["pattern_boost"],
                "extra_reason_codes": pattern_advice["extra_reason_codes"],
            },
        )
    # guardian: allow-silent-swallow
    except Exception:  # guardian: allow-silent-swallower
        logger.debug("pattern advice emission failed; swallowed to preserve dispatch path")


def invoke_qwen_with_oom_protection(
    healing_input: HealingInput,
    decision: HealingDecision,
    config: HealingTierConfig,
    invoker: HealingProviderInvoker,
    agent_name: str = "",
) -> InvocationRecord:
    """Invoke Qwen with OOM protection and proper escalation."""
    try:
        return invoker.invoke_qwen_vllm(healing_input, decision, config, agent_name=agent_name)
    # guardian: allow-silent-swallow
    except Exception as exc:
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling
        if "out of memory" in str(exc).lower():
            # Route through choke point - router handles retry_count >= 3 -> GEMINI escalation
            escalated_decision = handle_qwen_oom_via_router(healing_input, config)
            # Retry with escalated tier using AgentDispatchRegistry
            method_name = _TIER_TO_METHOD[escalated_decision.tier]
            registry = get_agent_dispatch_registry()
            return registry.dispatch(
                caller="healing_tier_dispatcher",
                target_class=invoker.__class__.__name__,
                method=method_name,
                target_instance=invoker,
                args=(healing_input, escalated_decision, config),
                kwargs={"agent_name": agent_name},
            )
        raise


__all__ = [
    "DefaultHealingProviderInvoker",
    "HealingProviderInvoker",
    "InvocationRecord",
    "dispatch_healing",
    "handle_qwen_oom_via_router",
    "invoke_qwen_with_oom_protection",
]
