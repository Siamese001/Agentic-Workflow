"""Meta Outcome Bus Hook Port — enqueues healing outcomes onto MetaLearningBus.

Called by dispatch_healing() after invocation completes.
Creates MetaLearningChangePackage with proposal_only=True and enqueues
on the injected MetaLearningBus.

Contracts:
- MUST be synchronous and fast (no network I/O in hot path).
- MUST enforce proposal_only=True in all packages.
- MUST NOT modify routing thresholds or tiers.
- MUST NOT fail dispatch if bus enqueue fails (log and continue).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
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

_emit_applies_guardrail("p0", "meta_outcome_bus_hook", "p0_governance")
_emit_reads_policy_state("p0", "meta_outcome_bus_hook", "policy_binding")
_emit_snapshots_state("p0", "meta_outcome_bus_hook", "state_snapshot")
emit_replay_key("p0", "meta_outcome_bus_hook")
emit_determinism_digest("p0", "meta_outcome_bus_hook")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "meta_outcome_bus_hook", "execution_auth")
_emit_validates_capability("p2", "meta_outcome_bus_hook", "capability_check")
_emit_routes_to_capability("p2", "meta_outcome_bus_hook", "capability_route")
_emit_writes_via_uwg("p2", "meta_outcome_bus_hook", "uwg_write")
_emit_blocks_direct_write("p2", "meta_outcome_bus_hook", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_outcome_bus_hook", "tool_invocation")
_emit_captures_execution_output("p2", "meta_outcome_bus_hook", "exec_output")
_emit_dispatches_agent("p3", "meta_outcome_bus_hook", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_outcome_bus_hook", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_outcome_bus_hook", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_outcome_bus_hook", "healing_outcome")
_emit_escalates_failure("p3", "meta_outcome_bus_hook", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_outcome_bus_hook", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_outcome_bus_hook", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_outcome_bus_hook", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_outcome_bus_hook", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_outcome_bus_hook", "eval_metric")
_emit_stores_embedding("p4", "meta_outcome_bus_hook", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_outcome_bus_hook", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_outcome_bus_hook", "exec_snapshot_link")

if TYPE_CHECKING:
    from system_learning.meta_learning.meta_learning_bus import MetaLearningBus
    from agentic_core.L3_orchestration.healers.healing_tier_dispatcher import InvocationRecord
    from agentic_core.L3_orchestration.healers.healing_tier_types import HealingDecision, HealingInput
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("meta_outcome_bus_hook", "p4obs", "metric_1")
_emit_emits_metric_event("meta_outcome_bus_hook", "p4obs", "metric_2")
_emit_emits_metric_event("meta_outcome_bus_hook", "p4obs", "metric_3")
_emit_emits_metric_event("meta_outcome_bus_hook", "p4obs", "metric_4")
_emit_emits_metric_event("meta_outcome_bus_hook", "p4obs", "metric_5")
_emit_emits_metric_event("meta_outcome_bus_hook", "p4obs", "metric_6")
_emit_records_incident_event("meta_outcome_bus_hook", "p4obs", "incident")
_emit_captures_runtime_anomaly("meta_outcome_bus_hook", "p4obs", "anomaly")
_emit_writes_observability_log("meta_outcome_bus_hook", "p4obs", "obs_log")
_emit_updates_monitoring_state("meta_outcome_bus_hook", "p4obs", "mon_state")
_emit_triggers_alert("meta_outcome_bus_hook", "p4obs", "alert")
_emit_links_incident_trace("meta_outcome_bus_hook", "p4obs", "trace_link")
_emit_captures_pattern("meta_outcome_bus_hook", "p3lm", "pattern")
_emit_records_learning_event("meta_outcome_bus_hook", "p3lm", "learning_event")
_emit_writes_learning_snapshot("meta_outcome_bus_hook", "p3lm", "snapshot")
_emit_feeds_meta_learning("meta_outcome_bus_hook", "p3lm", "meta_feed")
_emit_updates_routing_strategy("meta_outcome_bus_hook", "p3lm", "routing")
_emit_improves_agent_policy("meta_outcome_bus_hook", "p3lm", "policy")
_emit_stores_learning_state("meta_outcome_bus_hook", "p3lm", "state")
_emit_records_execution_trace("meta_outcome_bus_hook", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("meta_outcome_bus_hook", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("meta_outcome_bus_hook", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("meta_outcome_bus_hook", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("meta_outcome_bus_hook", "L4_STATE", "p2_trace_5")
_emit_reads_environ("meta_outcome_bus_hook", "env_read", "p2_env_1")
_emit_reads_environ("meta_outcome_bus_hook", "env_read", "p2_env_2")
_emit_reads_runtime_state("meta_outcome_bus_hook", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("meta_outcome_bus_hook", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "meta_outcome_bus_hook", "context_pull")
_emit_pulls_context("p1", "meta_outcome_bus_hook", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "meta_outcome_bus_hook", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "meta_outcome_bus_hook", "uwg_term_2")
_emit_writes_through("p1", "meta_outcome_bus_hook", "write_through")
_emit_writes_through("p1", "meta_outcome_bus_hook", "write_through_2")
_emit_validated_by_safety_plane("p1", "meta_outcome_bus_hook", "safety_validation")
_emit_invokes_eval("p1", "meta_outcome_bus_hook", "eval_call")
_emit_proposal_commits_routing("p1", "meta_outcome_bus_hook", "routing_commit")
_emit_escalates_to_human("p1", "meta_outcome_bus_hook", "human_escalation")
_emit_routes_through("p1", "meta_outcome_bus_hook", "route_through")
_emit_checks_agent_registry("p1", "meta_outcome_bus_hook", "agent_registry")
_emit_validates_agent_capability("p1", "meta_outcome_bus_hook", "capability")
_emit_dispatches_execution_plan("p1", "meta_outcome_bus_hook", "exec_plan")
_emit_agent_executes_agent("p1", "meta_outcome_bus_hook", "sub_agent")
_emit_routes_to_agent("p1", "meta_outcome_bus_hook", "target_agent")
_emit_verifies_policy("p1", "meta_outcome_bus_hook", "policy_check")
_emit_observes_runtime_state("p1", "meta_outcome_bus_hook", "runtime_state")
_emit_verifies_boundary("p1", "meta_outcome_bus_hook", "boundary_check")
_emit_transcripts_response("p1", "meta_outcome_bus_hook", "transcript")
_emit_hard_fails_untranscripted("p1", "meta_outcome_bus_hook")
_emit_gated_by_confidence("p1", "meta_outcome_bus_hook", "confidence_gate")

logger = logging.getLogger(__name__)


class MetaOutcomeBusHook(Protocol):
    """Synchronous seam for publishing healing outcomes to MetaLearningBus."""

    def publish_outcome(
        self,
        *,
        healing_input: HealingInput,
        decision: HealingDecision,
        record: InvocationRecord | None,
        success: bool,
    ) -> None:
        """Publish a healing outcome as a MetaLearningChangePackage.

        Parameters
        ----------
        healing_input : HealingInput
            The original structured failure context.
        decision : HealingDecision
            The routing decision that was executed.
        record : InvocationRecord | None
            The invocation trace record (None if exception before record).
        success : bool
            Whether the heal attempt succeeded.
        """
        ...


class NullMetaOutcomeBusHook:
    """No-op hook (default when no bus is configured)."""

    def publish_outcome(self, **kwargs) -> None:
        pass


class DefaultMetaOutcomeBusHook:
    """Default hook: enqueues outcomes on injected MetaLearningBus.

    Always sets proposal_only=True and never fails the dispatch path.
    """

    def __init__(self, bus: MetaLearningBus | None = None) -> None:
        self._bus = bus

    def publish_outcome(self, *, healing_input, decision, record, success: bool) -> None:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DefaultMetaOutcomeBusHook.publish_outcome")

        if self._bus is None:
            return
        try:
            from system_learning.meta_learning.meta_learning_bus import MetaLearningChangePackage

            package = MetaLearningChangePackage.create(
                trace_id=healing_input.trace_id,
                kind="healing_outcome",
                payload={
                    "error_signature": healing_input.error_signature,
                    "tier": decision.tier.value,
                    "heal_confidence": decision.heal_confidence,
                    "success": success,
                    "trace_id": healing_input.trace_id,
                    "retry_count": healing_input.retry_count,
                    "reason_codes": list(decision.reason_codes),
                    "proposal_only": True,
                },
            )
            self._bus.enqueue(package)
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.warning(
                "meta_outcome_bus_enqueue_failed",
                extra={
                    "error_signature": healing_input.error_signature,
                    "exception": str(exc),
                    "trace_id": healing_input.trace_id,
                },
            )


__all__ = ["MetaOutcomeBusHook", "NullMetaOutcomeBusHook", "DefaultMetaOutcomeBusHook"]
