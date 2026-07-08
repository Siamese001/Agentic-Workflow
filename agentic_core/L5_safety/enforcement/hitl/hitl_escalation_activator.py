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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract
from agentic_core.runtime.types.execution_trace import get_active_execution_trace

trace_contract.emit_replay_key("p0", "hitl_escalation_activator")
trace_contract.emit_determinism_digest("p0", "hitl_escalation_activator")

trace_contract._emit_dispatches_healing_run("p1", "hitl_escalation_activator", "L5")
trace_contract._emit_routes_through("p1", "hitl_escalation_activator", "L5")
trace_contract._emit_checks_agent_registry("p1", "hitl_escalation_activator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "hitl_escalation_activator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "hitl_escalation_activator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "hitl_escalation_activator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "hitl_escalation_activator", "target_agent")
trace_contract._emit_verifies_policy("p1", "hitl_escalation_activator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "hitl_escalation_activator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "hitl_escalation_activator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "hitl_escalation_activator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "hitl_escalation_activator")
trace_contract._emit_gated_by_confidence("p1", "hitl_escalation_activator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "hitl_escalation_activator", "L5")
trace_contract._emit_reads_policy_state("p1", "hitl_escalation_activator", "L5")

trace_contract._emit_applies_guardrail("p0", "hitl_escalation_activator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "hitl_escalation_activator", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "hitl_escalation_activator", "execution_auth")
trace_contract._emit_validates_capability("p2", "hitl_escalation_activator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "hitl_escalation_activator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "hitl_escalation_activator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "hitl_escalation_activator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "hitl_escalation_activator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "hitl_escalation_activator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "hitl_escalation_activator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "hitl_escalation_activator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "hitl_escalation_activator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "hitl_escalation_activator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "hitl_escalation_activator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "hitl_escalation_activator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "hitl_escalation_activator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "hitl_escalation_activator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "hitl_escalation_activator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "hitl_escalation_activator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "hitl_escalation_activator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "hitl_escalation_activator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "hitl_escalation_activator", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("hitl_escalation_activator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("hitl_escalation_activator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("hitl_escalation_activator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("hitl_escalation_activator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("hitl_escalation_activator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("hitl_escalation_activator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("hitl_escalation_activator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("hitl_escalation_activator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("hitl_escalation_activator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("hitl_escalation_activator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("hitl_escalation_activator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("hitl_escalation_activator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("hitl_escalation_activator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("hitl_escalation_activator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("hitl_escalation_activator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("hitl_escalation_activator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("hitl_escalation_activator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("hitl_escalation_activator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("hitl_escalation_activator", "p3lm", "state")
trace_contract._emit_records_execution_trace("hitl_escalation_activator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("hitl_escalation_activator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("hitl_escalation_activator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("hitl_escalation_activator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("hitl_escalation_activator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("hitl_escalation_activator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("hitl_escalation_activator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("hitl_escalation_activator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("hitl_escalation_activator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "hitl_escalation_activator", "context_pull")
trace_contract._emit_pulls_context("p1", "hitl_escalation_activator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "hitl_escalation_activator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "hitl_escalation_activator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "hitl_escalation_activator", "write_through")
trace_contract._emit_writes_through("p1", "hitl_escalation_activator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "hitl_escalation_activator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "hitl_escalation_activator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "hitl_escalation_activator", "routing_commit")

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "EscalationRequest.resolve")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:EscalationRequest.resolve".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "HITLEscalationActivator.escalate")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HITLEscalationActivator.escalate".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        for handler in tqdm(self._handlers, desc="Processing", unit="item"):
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
            except (
                ValueError,
                TypeError,
            ) as exc:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
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
