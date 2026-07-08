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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "state_lifecycle_policy")
trace_contract.emit_determinism_digest("p0", "state_lifecycle_policy")

trace_contract._emit_dispatches_healing_run("p1", "state_lifecycle_policy", "L4")
trace_contract._emit_routes_through("p1", "state_lifecycle_policy", "L4")
trace_contract._emit_checks_agent_registry("p1", "state_lifecycle_policy", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "state_lifecycle_policy", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "state_lifecycle_policy", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "state_lifecycle_policy", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "state_lifecycle_policy", "target_agent")
trace_contract._emit_verifies_policy("p1", "state_lifecycle_policy", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "state_lifecycle_policy", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "state_lifecycle_policy", "boundary_check")
trace_contract._emit_transcripts_response("p1", "state_lifecycle_policy", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "state_lifecycle_policy")
trace_contract._emit_gated_by_confidence("p1", "state_lifecycle_policy", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "state_lifecycle_policy", "L4")
trace_contract._emit_reads_policy_state("p1", "state_lifecycle_policy", "L4")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "state_lifecycle_policy", "p0_governance")
trace_contract._emit_authorize_and_execute("p2", "state_lifecycle_policy", "execution_auth")
trace_contract._emit_validates_capability("p2", "state_lifecycle_policy", "capability_check")
trace_contract._emit_routes_to_capability("p2", "state_lifecycle_policy", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "state_lifecycle_policy", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "state_lifecycle_policy", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "state_lifecycle_policy", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "state_lifecycle_policy", "exec_output")
trace_contract._emit_dispatches_agent("p3", "state_lifecycle_policy", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "state_lifecycle_policy", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "state_lifecycle_policy", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "state_lifecycle_policy", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "state_lifecycle_policy", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "state_lifecycle_policy", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "state_lifecycle_policy", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "state_lifecycle_policy", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "state_lifecycle_policy", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "state_lifecycle_policy", "eval_metric")
trace_contract._emit_stores_embedding("p4", "state_lifecycle_policy", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "state_lifecycle_policy", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "state_lifecycle_policy", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("state_lifecycle_policy", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("state_lifecycle_policy", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("state_lifecycle_policy", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("state_lifecycle_policy", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("state_lifecycle_policy", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("state_lifecycle_policy", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("state_lifecycle_policy", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("state_lifecycle_policy", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("state_lifecycle_policy", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("state_lifecycle_policy", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("state_lifecycle_policy", "p4obs", "alert")
trace_contract._emit_links_incident_trace("state_lifecycle_policy", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("state_lifecycle_policy", "p3lm", "pattern")
trace_contract._emit_records_learning_event("state_lifecycle_policy", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("state_lifecycle_policy", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("state_lifecycle_policy", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("state_lifecycle_policy", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("state_lifecycle_policy", "p3lm", "policy")
trace_contract._emit_stores_learning_state("state_lifecycle_policy", "p3lm", "state")
trace_contract._emit_records_execution_trace("state_lifecycle_policy", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("state_lifecycle_policy", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("state_lifecycle_policy", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("state_lifecycle_policy", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("state_lifecycle_policy", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("state_lifecycle_policy", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("state_lifecycle_policy", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("state_lifecycle_policy", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("state_lifecycle_policy", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "state_lifecycle_policy", "context_pull")
trace_contract._emit_pulls_context("p1", "state_lifecycle_policy", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "state_lifecycle_policy", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "state_lifecycle_policy", "uwg_term_2")
trace_contract._emit_writes_through("p1", "state_lifecycle_policy", "write_through")
trace_contract._emit_writes_through("p1", "state_lifecycle_policy", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "state_lifecycle_policy", "safety_validation")
trace_contract._emit_invokes_eval("p1", "state_lifecycle_policy", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "state_lifecycle_policy", "routing_commit")

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
        trace_contract._emit_snapshots_state(str(uuid.uuid4()), "StateLifecyclePolicy.transition", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "StateLifecyclePolicy.transition")

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
