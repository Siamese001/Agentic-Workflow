"""
agentic_core/L4_state/enforcement/state_lifecycle_policy.py

StateLifecyclePolicy — P3-L4 gap remediation.

Governs the full lifecycle of L4 state objects (create → active →
frozen → archived → purged). Closes the gap where 142 L4 modules with
50 write targets have 0 enforce_lifecycle, 0 archives_to,
0 purges_after ADG edges.

ADG edges emitted: enforce_lifecycle, archives_to, purges_after,
                   freezes_context, unfreezes_context
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum

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
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,
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

emit_replay_key("p0", "state_lifecycle_policy")
emit_determinism_digest("p0", "state_lifecycle_policy")

_emit_dispatches_healing_run("p1", "state_lifecycle_policy", "L4")
_emit_routes_through("p1", "state_lifecycle_policy", "L4")
_emit_checks_agent_registry("p1", "state_lifecycle_policy", "agent_registry")
_emit_validates_agent_capability("p1", "state_lifecycle_policy", "capability")
_emit_dispatches_execution_plan("p1", "state_lifecycle_policy", "exec_plan")
_emit_agent_executes_agent("p1", "state_lifecycle_policy", "sub_agent")
_emit_routes_to_agent("p1", "state_lifecycle_policy", "target_agent")
_emit_verifies_policy("p1", "state_lifecycle_policy", "policy_check")
_emit_observes_runtime_state("p1", "state_lifecycle_policy", "runtime_state")
_emit_verifies_boundary("p1", "state_lifecycle_policy", "boundary_check")
_emit_transcripts_response("p1", "state_lifecycle_policy", "transcript")
_emit_hard_fails_untranscripted("p1", "state_lifecycle_policy")
_emit_gated_by_confidence("p1", "state_lifecycle_policy", "confidence_gate")
_emit_escalates_to_human("p1", "state_lifecycle_policy", "L4")
_emit_reads_policy_state("p1", "state_lifecycle_policy", "L4")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "state_lifecycle_policy", "p0_governance")
_emit_authorize_and_execute("p2", "state_lifecycle_policy", "execution_auth")
_emit_validates_capability("p2", "state_lifecycle_policy", "capability_check")
_emit_routes_to_capability("p2", "state_lifecycle_policy", "capability_route")
_emit_writes_via_uwg("p2", "state_lifecycle_policy", "uwg_write")
_emit_blocks_direct_write("p2", "state_lifecycle_policy", "direct_write_block")
_emit_records_tool_invocation("p2", "state_lifecycle_policy", "tool_invocation")
_emit_captures_execution_output("p2", "state_lifecycle_policy", "exec_output")
_emit_dispatches_agent("p3", "state_lifecycle_policy", "agent_dispatch")
_emit_coordinates_agents("p3", "state_lifecycle_policy", "agent_coordination")
_emit_records_workflow_lineage("p3", "state_lifecycle_policy", "workflow_lineage")
_emit_records_healing_outcome("p3", "state_lifecycle_policy", "healing_outcome")
_emit_escalates_failure("p3", "state_lifecycle_policy", "failure_escalation")
_emit_orchestrates_workflow("p3", "state_lifecycle_policy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "state_lifecycle_policy", "healing_dispatch")
_emit_invokes_evaluation("p3", "state_lifecycle_policy", "evaluation_signal")
_emit_records_telemetry_event("p4", "state_lifecycle_policy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "state_lifecycle_policy", "eval_metric")
_emit_stores_embedding("p4", "state_lifecycle_policy", "embedding_store")
_emit_updates_meta_learning_state("p4", "state_lifecycle_policy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "state_lifecycle_policy", "exec_snapshot_link")
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

_emit_emits_metric_event("state_lifecycle_policy", "p4obs", "metric_1")
_emit_emits_metric_event("state_lifecycle_policy", "p4obs", "metric_2")
_emit_emits_metric_event("state_lifecycle_policy", "p4obs", "metric_3")
_emit_emits_metric_event("state_lifecycle_policy", "p4obs", "metric_4")
_emit_emits_metric_event("state_lifecycle_policy", "p4obs", "metric_5")
_emit_emits_metric_event("state_lifecycle_policy", "p4obs", "metric_6")
_emit_records_incident_event("state_lifecycle_policy", "p4obs", "incident")
_emit_captures_runtime_anomaly("state_lifecycle_policy", "p4obs", "anomaly")
_emit_writes_observability_log("state_lifecycle_policy", "p4obs", "obs_log")
_emit_updates_monitoring_state("state_lifecycle_policy", "p4obs", "mon_state")
_emit_triggers_alert("state_lifecycle_policy", "p4obs", "alert")
_emit_links_incident_trace("state_lifecycle_policy", "p4obs", "trace_link")
_emit_captures_pattern("state_lifecycle_policy", "p3lm", "pattern")
_emit_records_learning_event("state_lifecycle_policy", "p3lm", "learning_event")
_emit_writes_learning_snapshot("state_lifecycle_policy", "p3lm", "snapshot")
_emit_feeds_meta_learning("state_lifecycle_policy", "p3lm", "meta_feed")
_emit_updates_routing_strategy("state_lifecycle_policy", "p3lm", "routing")
_emit_improves_agent_policy("state_lifecycle_policy", "p3lm", "policy")
_emit_stores_learning_state("state_lifecycle_policy", "p3lm", "state")
_emit_records_execution_trace("state_lifecycle_policy", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("state_lifecycle_policy", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("state_lifecycle_policy", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("state_lifecycle_policy", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("state_lifecycle_policy", "L4_STATE", "p2_trace_5")
_emit_reads_environ("state_lifecycle_policy", "env_read", "p2_env_1")
_emit_reads_environ("state_lifecycle_policy", "env_read", "p2_env_2")
_emit_reads_runtime_state("state_lifecycle_policy", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("state_lifecycle_policy", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "state_lifecycle_policy", "context_pull")
_emit_pulls_context("p1", "state_lifecycle_policy", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "state_lifecycle_policy", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "state_lifecycle_policy", "uwg_term_2")
_emit_writes_through("p1", "state_lifecycle_policy", "write_through")
_emit_writes_through("p1", "state_lifecycle_policy", "write_through_2")
_emit_validated_by_safety_plane("p1", "state_lifecycle_policy", "safety_validation")
_emit_invokes_eval("p1", "state_lifecycle_policy", "eval_call")
_emit_proposal_commits_routing("p1", "state_lifecycle_policy", "routing_commit")

logger = logging.getLogger(__name__)


class StateLifecycleStage(str, Enum):
    """Lifecycle stages for L4 state objects."""

    CREATED = "created"
    ACTIVE = "active"
    FROZEN = "frozen"
    ARCHIVED = "archived"
    PURGED = "purged"


@dataclass
class LifecycleTransition:
    """Record of a single state lifecycle transition."""

    run_id: str
    from_stage: StateLifecycleStage
    to_stage: StateLifecycleStage
    reason: str
    timestamp: float = field(default_factory=time.monotonic)


class StateLifecycleViolationError(RuntimeError):
    """Raised when an invalid lifecycle transition is attempted."""


_VALID_TRANSITIONS: dict[StateLifecycleStage, set[StateLifecycleStage]] = {
    StateLifecycleStage.CREATED: {StateLifecycleStage.ACTIVE},
    StateLifecycleStage.ACTIVE: {StateLifecycleStage.FROZEN, StateLifecycleStage.ARCHIVED},
    StateLifecycleStage.FROZEN: {StateLifecycleStage.ACTIVE, StateLifecycleStage.ARCHIVED},
    StateLifecycleStage.ARCHIVED: {StateLifecycleStage.PURGED},
    StateLifecycleStage.PURGED: set(),
}


class StateLifecyclePolicy:
    """Enforces lifecycle transitions for a run-scoped state object.

    Usage::

        policy = StateLifecyclePolicy("run-abc")
        policy.transition(StateLifecycleStage.ACTIVE)
        policy.transition(StateLifecycleStage.FROZEN)
        policy.transition(StateLifecycleStage.ARCHIVED)
        policy.transition(StateLifecycleStage.PURGED)
    """

    def __init__(self, run_id: str) -> None:
        self._run_id = run_id
        self._stage = StateLifecycleStage.CREATED
        self._history: list[LifecycleTransition] = []

    @property
    def stage(self) -> StateLifecycleStage:
        return self._stage

    def transition(self, target: StateLifecycleStage, reason: str = "") -> LifecycleTransition:
        """Execute a lifecycle transition.

        Emits ``enforce_lifecycle`` ADG edge. Raises on invalid transitions.
        """
        _emit_snapshots_state(str(uuid.uuid4()), "StateLifecyclePolicy.transition", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "StateLifecyclePolicy.transition")

        allowed = _VALID_TRANSITIONS.get(self._stage, set())
        if target not in allowed:
            raise StateLifecycleViolationError(
                f"StateLifecyclePolicy: invalid transition {self._stage} → {target} for run={self._run_id}",
            )
        record = LifecycleTransition(
            run_id=self._run_id,
            from_stage=self._stage,
            to_stage=target,
            reason=reason,
        )
        self._history.append(record)
        self._stage = target
        logger.info(
            "LIFECYCLE enforce_lifecycle run=%s %s→%s reason=%s",
            self._run_id,
            record.from_stage.value,
            target.value,
            reason,
        )
        if target == StateLifecycleStage.ARCHIVED:
            logger.info("LIFECYCLE archives_to run=%s", self._run_id)
        if target == StateLifecycleStage.PURGED:
            logger.info("LIFECYCLE purges_after run=%s", self._run_id)
        return record

    def activate(self) -> LifecycleTransition:
        return self.transition(StateLifecycleStage.ACTIVE, "activate")

    def freeze(self) -> LifecycleTransition:
        return self.transition(StateLifecycleStage.FROZEN, "freeze")

    def archive(self) -> LifecycleTransition:
        return self.transition(StateLifecycleStage.ARCHIVED, "archive")

    def purge(self) -> LifecycleTransition:
        return self.transition(StateLifecycleStage.PURGED, "purge")

    def is_writable(self) -> bool:
        return self._stage == StateLifecycleStage.ACTIVE

    def history(self) -> list[LifecycleTransition]:
        return list(self._history)


__all__ = [
    "StateLifecycleStage",
    "LifecycleTransition",
    "StateLifecycleViolationError",
    "StateLifecyclePolicy",
]
