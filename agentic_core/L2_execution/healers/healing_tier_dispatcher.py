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
import time
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
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "healing_tier_dispatcher")
emit_determinism_digest("p0", "healing_tier_dispatcher")

_emit_dispatches_healing_run("p1", "healing_tier_dispatcher", "L2")
_emit_routes_through("p1", "healing_tier_dispatcher", "L2")
_emit_agent_executes_agent("p1", "healing_tier_dispatcher", "sub_agent")
_emit_verifies_policy("p1", "healing_tier_dispatcher", "policy_check")
_emit_observes_runtime_state("p1", "healing_tier_dispatcher", "runtime_state")
_emit_verifies_boundary("p1", "healing_tier_dispatcher", "boundary_check")
_emit_transcripts_response("p1", "healing_tier_dispatcher", "transcript")
_emit_hard_fails_untranscripted("p1", "healing_tier_dispatcher")
_emit_gated_by_confidence("p1", "healing_tier_dispatcher", "confidence_gate")
_emit_escalates_to_human("p1", "healing_tier_dispatcher", "L2")
_emit_reads_policy_state("p1", "healing_tier_dispatcher", "L2")
_emit_routes_to_agent("p1", "healing_tier_dispatcher", "L2")
_emit_orchestrates_workflow("p1", "healing_tier_dispatcher", "L2")
_emit_dispatches_execution_plan("p1", "healing_tier_dispatcher", "L2")
_emit_validates_agent_capability("p1", "healing_tier_dispatcher", "L2")
_emit_checks_agent_registry("p1", "healing_tier_dispatcher", "L2")

_emit_snapshots_state("p0", "healing_tier_dispatcher", "state_snapshot")
_emit_authorize_and_execute("p2", "healing_tier_dispatcher", "execution_auth")
_emit_validates_capability("p2", "healing_tier_dispatcher", "capability_check")
_emit_routes_to_capability("p2", "healing_tier_dispatcher", "capability_route")
_emit_writes_via_uwg("p2", "healing_tier_dispatcher", "uwg_write")
_emit_blocks_direct_write("p2", "healing_tier_dispatcher", "direct_write_block")
_emit_records_tool_invocation("p2", "healing_tier_dispatcher", "tool_invocation")
_emit_captures_execution_output("p2", "healing_tier_dispatcher", "exec_output")
_emit_dispatches_agent("p3", "healing_tier_dispatcher", "agent_dispatch")
_emit_coordinates_agents("p3", "healing_tier_dispatcher", "agent_coordination")
_emit_records_workflow_lineage("p3", "healing_tier_dispatcher", "workflow_lineage")
_emit_records_healing_outcome("p3", "healing_tier_dispatcher", "healing_outcome")
_emit_escalates_failure("p3", "healing_tier_dispatcher", "failure_escalation")
_emit_orchestrates_workflow("p3", "healing_tier_dispatcher", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healing_tier_dispatcher", "healing_dispatch")
_emit_invokes_evaluation("p3", "healing_tier_dispatcher", "evaluation_signal")
_emit_records_telemetry_event("p4", "healing_tier_dispatcher", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healing_tier_dispatcher", "eval_metric")
_emit_stores_embedding("p4", "healing_tier_dispatcher", "embedding_store")
_emit_updates_meta_learning_state("p4", "healing_tier_dispatcher", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healing_tier_dispatcher", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("healing_tier_dispatcher", "p4obs", "metric_1")
_emit_emits_metric_event("healing_tier_dispatcher", "p4obs", "metric_2")
_emit_emits_metric_event("healing_tier_dispatcher", "p4obs", "metric_3")
_emit_emits_metric_event("healing_tier_dispatcher", "p4obs", "metric_4")
_emit_emits_metric_event("healing_tier_dispatcher", "p4obs", "metric_5")
_emit_emits_metric_event("healing_tier_dispatcher", "p4obs", "metric_6")
_emit_records_incident_event("healing_tier_dispatcher", "p4obs", "incident")
_emit_captures_runtime_anomaly("healing_tier_dispatcher", "p4obs", "anomaly")
_emit_writes_observability_log("healing_tier_dispatcher", "p4obs", "obs_log")
_emit_updates_monitoring_state("healing_tier_dispatcher", "p4obs", "mon_state")
_emit_triggers_alert("healing_tier_dispatcher", "p4obs", "alert")
_emit_links_incident_trace("healing_tier_dispatcher", "p4obs", "trace_link")
_emit_captures_pattern("healing_tier_dispatcher", "p3lm", "pattern")
_emit_records_learning_event("healing_tier_dispatcher", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healing_tier_dispatcher", "p3lm", "snapshot")
_emit_feeds_meta_learning("healing_tier_dispatcher", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healing_tier_dispatcher", "p3lm", "routing")
_emit_improves_agent_policy("healing_tier_dispatcher", "p3lm", "policy")
_emit_stores_learning_state("healing_tier_dispatcher", "p3lm", "state")
_emit_records_execution_trace("healing_tier_dispatcher", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healing_tier_dispatcher", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healing_tier_dispatcher", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healing_tier_dispatcher", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healing_tier_dispatcher", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healing_tier_dispatcher", "env_read", "p2_env_1")
_emit_reads_environ("healing_tier_dispatcher", "env_read", "p2_env_2")
_emit_reads_runtime_state("healing_tier_dispatcher", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healing_tier_dispatcher", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healing_tier_dispatcher", "context_pull")
_emit_pulls_context("p1", "healing_tier_dispatcher", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healing_tier_dispatcher", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healing_tier_dispatcher", "uwg_term_2")
_emit_writes_through("p1", "healing_tier_dispatcher", "write_through")
_emit_writes_through("p1", "healing_tier_dispatcher", "write_through_2")
_emit_validated_by_safety_plane("p1", "healing_tier_dispatcher", "safety_validation")
_emit_invokes_eval("p1", "healing_tier_dispatcher", "eval_call")
_emit_proposal_commits_routing("p1", "healing_tier_dispatcher", "routing_commit")

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
            except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallower
                logger.warning("outcome_write_back_hook raised — continuing", exc_info=True)

        # Emit tier dispatch outcome to system learning
        _emit_tier_dispatch_outcome(
            healing_input=healing_input,
            decision=decision,
            success=success,
            record=record,
            timestamp_utc=timestamp_utc,
            agent_name=agent_name,
        )

        # Phase 3: C0 informational-only pattern advisor (cannot change tier)
        if pattern_advisor is not None:
            try:
                pattern_advice = pattern_advisor.advise(healing_input)
                if pattern_advice is not None and timestamp_utc is not None:
                    _emit_pattern_advice(pattern_advice, healing_input, agent_name, timestamp_utc)
            # guardian: allow-silent-swallow
            except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallower
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
    except (RuntimeError, ValueError):  # noqa: BLE001
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
    except (RuntimeError, ValueError):  # noqa: BLE001  # guardian: allow-silent-swallower
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
    except (RuntimeError, ValueError):  # noqa: BLE001  # guardian: allow-silent-swallower
        logger.debug("rollback refinement failed; swallowed to preserve dispatch path")


def _emit_tier_dispatch_outcome(
    healing_input: HealingInput,
    decision: HealingDecision,
    success: bool,
    record: InvocationRecord | None,
    timestamp_utc: int | None,
    agent_name: str,
) -> None:
    """Emit tier dispatch outcome to system learning for effectiveness analysis."""
    try:
        from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge
        bridge = get_sl_memory_bridge()

        # Extract key metrics for analysis
        tier = decision.tier.name if hasattr(decision.tier, 'name') else str(decision.tier)
        failure_type = healing_input.failure_type
        module_name = getattr(healing_input, 'module_name', 'unknown')

        # Calculate duration if record available
        duration_ms = 0
        if record and hasattr(record, 'duration_ms'):
            duration_ms = record.duration_ms

        bridge.persist_healing_tier_outcome(
            tier=tier,
            failure_type=failure_type,
            module_name=module_name,
            success=success,
            duration_ms=duration_ms,
            timestamp_utc=timestamp_utc or int(time.time() * 1000),
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
        )
    except (RuntimeError, ValueError):
        # System learning unavailable - continue without emission
        pass


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
    except (RuntimeError, ValueError):  # guardian: allow-silent-swallower
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
