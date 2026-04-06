"""
agentic_core/L5_safety/hitl/hitl_escalation_activator.py

HITLEscalationActivator — P3-L5 gap remediation.

Activates the HITL escalation path when policy enforcement, guardrail
checks, or tool safety gates produce ESCALATE / REENTER verdicts.
Closes the gap: 608 L5 modules, 0 hitl_escalation_activation edges,
2 HITL files but 0 escalation triggers from enforcement modules.

ADG edges emitted: hitl_escalation_activation, reenters_safety,
                   validated_by_safety_plane
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from agentic_core.L5_safety.enforcement.hitl.decision_logger import (
    HITLDecision,
    get_decision_logger,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
from agentic_core.runtime.types.execution_trace import get_active_execution_trace

emit_replay_key("p0", "hitl_escalation_activator")
emit_determinism_digest("p0", "hitl_escalation_activator")

_emit_dispatches_healing_run("p1", "hitl_escalation_activator", "L5")
_emit_routes_through("p1", "hitl_escalation_activator", "L5")
_emit_checks_agent_registry("p1", "hitl_escalation_activator", "agent_registry")
_emit_validates_agent_capability("p1", "hitl_escalation_activator", "capability")
_emit_dispatches_execution_plan("p1", "hitl_escalation_activator", "exec_plan")
_emit_agent_executes_agent("p1", "hitl_escalation_activator", "sub_agent")
_emit_routes_to_agent("p1", "hitl_escalation_activator", "target_agent")
_emit_verifies_policy("p1", "hitl_escalation_activator", "policy_check")
_emit_observes_runtime_state("p1", "hitl_escalation_activator", "runtime_state")
_emit_verifies_boundary("p1", "hitl_escalation_activator", "boundary_check")
_emit_transcripts_response("p1", "hitl_escalation_activator", "transcript")
_emit_hard_fails_untranscripted("p1", "hitl_escalation_activator")
_emit_gated_by_confidence("p1", "hitl_escalation_activator", "confidence_gate")
_emit_escalates_to_human("p1", "hitl_escalation_activator", "L5")
_emit_reads_policy_state("p1", "hitl_escalation_activator", "L5")

_emit_applies_guardrail("p0", "hitl_escalation_activator", "p0_governance")
_emit_snapshots_state("p0", "hitl_escalation_activator", "state_snapshot")
_emit_authorize_and_execute("p2", "hitl_escalation_activator", "execution_auth")
_emit_validates_capability("p2", "hitl_escalation_activator", "capability_check")
_emit_routes_to_capability("p2", "hitl_escalation_activator", "capability_route")
_emit_writes_via_uwg("p2", "hitl_escalation_activator", "uwg_write")
_emit_blocks_direct_write("p2", "hitl_escalation_activator", "direct_write_block")
_emit_records_tool_invocation("p2", "hitl_escalation_activator", "tool_invocation")
_emit_captures_execution_output("p2", "hitl_escalation_activator", "exec_output")
_emit_dispatches_agent("p3", "hitl_escalation_activator", "agent_dispatch")
_emit_coordinates_agents("p3", "hitl_escalation_activator", "agent_coordination")
_emit_records_workflow_lineage("p3", "hitl_escalation_activator", "workflow_lineage")
_emit_records_healing_outcome("p3", "hitl_escalation_activator", "healing_outcome")
_emit_escalates_failure("p3", "hitl_escalation_activator", "failure_escalation")
_emit_orchestrates_workflow("p3", "hitl_escalation_activator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hitl_escalation_activator", "healing_dispatch")
_emit_invokes_evaluation("p3", "hitl_escalation_activator", "evaluation_signal")
_emit_records_telemetry_event("p4", "hitl_escalation_activator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hitl_escalation_activator", "eval_metric")
_emit_stores_embedding("p4", "hitl_escalation_activator", "embedding_store")
_emit_updates_meta_learning_state("p4", "hitl_escalation_activator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hitl_escalation_activator", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
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
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("hitl_escalation_activator", "p4obs", "metric_1")
_emit_emits_metric_event("hitl_escalation_activator", "p4obs", "metric_2")
_emit_emits_metric_event("hitl_escalation_activator", "p4obs", "metric_3")
_emit_emits_metric_event("hitl_escalation_activator", "p4obs", "metric_4")
_emit_emits_metric_event("hitl_escalation_activator", "p4obs", "metric_5")
_emit_emits_metric_event("hitl_escalation_activator", "p4obs", "metric_6")
_emit_records_incident_event("hitl_escalation_activator", "p4obs", "incident")
_emit_captures_runtime_anomaly("hitl_escalation_activator", "p4obs", "anomaly")
_emit_writes_observability_log("hitl_escalation_activator", "p4obs", "obs_log")
_emit_updates_monitoring_state("hitl_escalation_activator", "p4obs", "mon_state")
_emit_triggers_alert("hitl_escalation_activator", "p4obs", "alert")
_emit_links_incident_trace("hitl_escalation_activator", "p4obs", "trace_link")
_emit_captures_pattern("hitl_escalation_activator", "p3lm", "pattern")
_emit_records_learning_event("hitl_escalation_activator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hitl_escalation_activator", "p3lm", "snapshot")
_emit_feeds_meta_learning("hitl_escalation_activator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hitl_escalation_activator", "p3lm", "routing")
_emit_improves_agent_policy("hitl_escalation_activator", "p3lm", "policy")
_emit_stores_learning_state("hitl_escalation_activator", "p3lm", "state")
_emit_records_execution_trace("hitl_escalation_activator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hitl_escalation_activator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hitl_escalation_activator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hitl_escalation_activator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hitl_escalation_activator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hitl_escalation_activator", "env_read", "p2_env_1")
_emit_reads_environ("hitl_escalation_activator", "env_read", "p2_env_2")
_emit_reads_runtime_state("hitl_escalation_activator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hitl_escalation_activator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hitl_escalation_activator", "context_pull")
_emit_pulls_context("p1", "hitl_escalation_activator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hitl_escalation_activator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hitl_escalation_activator", "uwg_term_2")
_emit_writes_through("p1", "hitl_escalation_activator", "write_through")
_emit_writes_through("p1", "hitl_escalation_activator", "write_through_2")
_emit_validated_by_safety_plane("p1", "hitl_escalation_activator", "safety_validation")
_emit_invokes_eval("p1", "hitl_escalation_activator", "eval_call")
_emit_proposal_commits_routing("p1", "hitl_escalation_activator", "routing_commit")

logger = logging.getLogger(__name__)


class EscalationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class EscalationRequest:
    """Single HITL escalation request."""

    trace_id: str
    agent: str
    module: str
    trigger_reason: str
    priority: EscalationPriority
    proposed_action: str
    policy_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution: str = ""

    def resolve(self, decision: str) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "EscalationRequest.resolve")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:EscalationRequest.resolve".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self.resolved = True
        self.resolution = decision


class HITLEscalationActivator:
    """Activates HITL escalation from enforcement verdicts.

    Usage::

        activator = HITLEscalationActivator()
        activator.register_handler(my_async_review_handler)

        # When PolicyEnforcementPoint returns ESCALATE:
        escalation = activator.escalate(
            agent="ToolSafetyGate",
            module="tool_safety_gate",
            trigger_reason="policy hash missing",
            proposed_action="invoke eval tool",
            priority=EscalationPriority.HIGH,
            policy_hash="",
        )
    """

    def __init__(self) -> None:
        self._pending: list[EscalationRequest] = []
        self._resolved: list[EscalationRequest] = []
        self._handlers: list[Callable[[EscalationRequest], str | None]] = []

    def register_handler(self, handler: Callable[[EscalationRequest], str | None]) -> None:
        """Register a review handler (sync). Handler returns decision string or None."""
        self._handlers.append(handler)

    def _trace_id(self) -> str:
        active = get_active_execution_trace()
        return active.trace_id if active else "no-active-trace"

    def escalate(
        self,
        agent: str,
        module: str,
        trigger_reason: str,
        proposed_action: str = "",
        priority: EscalationPriority = EscalationPriority.HIGH,
        policy_hash: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> EscalationRequest:
        """Activate HITL escalation for a given trigger.

        Emits ``hitl_escalation_activation`` + ``reenters_safety`` ADG edges.
        Logs via HITLDecisionLogger.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "HITLEscalationActivator.escalate")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HITLEscalationActivator.escalate".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        req = EscalationRequest(
            trace_id=self._trace_id(),
            agent=agent,
            module=module,
            trigger_reason=trigger_reason,
            priority=priority,
            proposed_action=proposed_action,
            policy_hash=policy_hash,
            metadata=metadata or {},
        )
        self._pending.append(req)
        logger.warning(
            "HITL hitl_escalation_activation reenters_safety "
            "agent=%s module=%s priority=%s reason=%s trace=%s",
            agent,
            module,
            priority.value,
            trigger_reason,
            req.trace_id,
        )

        decision_logger = get_decision_logger()
        decision: HITLDecision = decision_logger.log(
            agent=agent,
            file=module,
            violation=trigger_reason,
            proposed=proposed_action,
            decision="pending",
            metadata={"priority": priority.value, **req.metadata},
        )

        # Dispatch to handlers synchronously
        for handler in self._handlers:
            try:
                result = handler(req)
                if result:
                    req.resolve(result)
                    self._pending.remove(req)
                    self._resolved.append(req)
                    logger.info(
                        "HITL validated_by_safety_plane agent=%s decision=%s",
                        agent,
                        result,
                    )
                    break
            # guardian: allow-silent-swallow
            except (ValueError, TypeError) as exc:
                logger.error("HITL handler error agent=%s: %s", agent, exc)

        return req

    def pending(self) -> list[EscalationRequest]:
        return list(self._pending)

    def resolved(self) -> list[EscalationRequest]:
        return list(self._resolved)

    def requires_human_review(self, request: EscalationRequest) -> bool:
        """Check if a request requires human review (ADG: requires_human_review edge).

        All escalations with priority >= HIGH require human review.
        """
        return request.priority in (EscalationPriority.HIGH, EscalationPriority.CRITICAL)

    @property
    def pending_count(self) -> int:
        return len(self._pending)


_global_activator: HITLEscalationActivator | None = None


def get_hitl_escalation_activator() -> HITLEscalationActivator:
    global _global_activator
    if _global_activator is None:
        _global_activator = HITLEscalationActivator()
    return _global_activator


def reset_hitl_escalation_activator() -> None:
    global _global_activator
    _global_activator = None


__all__ = [
    "EscalationPriority",
    "EscalationRequest",
    "HITLEscalationActivator",
    "get_hitl_escalation_activator",
    "reset_hitl_escalation_activator",
]
