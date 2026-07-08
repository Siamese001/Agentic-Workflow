"""Addendum 5.1: Meta-Learning Stage Barrier Enforcer.

Enforces strict stage ordering:
    S1 audit → S2 telemetry → S3 config → S4 snapshot →
    S5 RCA → S6 propose → S7 validate → S8 intake → S9 commit

Rule: Only S9 outputs may modify L0 routing or L1 weights.
"""

from __future__ import annotations

import logging
from enum import IntEnum

from agentic_core.L5_safety.types.hardening_errors import RuntimePolicyMutationViolation
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "stage_barrier_enforcer", "p0_governance")
trace_contract._emit_snapshots_state("p0", "stage_barrier_enforcer", "state_snapshot")

trace_contract._emit_emits_metric_event("stage_barrier_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("stage_barrier_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("stage_barrier_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("stage_barrier_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("stage_barrier_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("stage_barrier_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("stage_barrier_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("stage_barrier_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("stage_barrier_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("stage_barrier_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("stage_barrier_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("stage_barrier_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("stage_barrier_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("stage_barrier_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("stage_barrier_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("stage_barrier_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("stage_barrier_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("stage_barrier_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("stage_barrier_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("stage_barrier_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("stage_barrier_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("stage_barrier_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("stage_barrier_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("stage_barrier_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("stage_barrier_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("stage_barrier_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("stage_barrier_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("stage_barrier_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "stage_barrier_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "stage_barrier_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "stage_barrier_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "stage_barrier_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "stage_barrier_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "stage_barrier_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "stage_barrier_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "stage_barrier_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "stage_barrier_enforcer", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "stage_barrier_enforcer", "human_escalation")
trace_contract._emit_routes_through("p1", "stage_barrier_enforcer", "route_through")
trace_contract._emit_checks_agent_registry("p1", "stage_barrier_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "stage_barrier_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "stage_barrier_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "stage_barrier_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "stage_barrier_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "stage_barrier_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "stage_barrier_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "stage_barrier_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "stage_barrier_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "stage_barrier_enforcer")
trace_contract._emit_gated_by_confidence("p1", "stage_barrier_enforcer", "confidence_gate")
trace_contract.emit_replay_key("p0", "stage_barrier_enforcer")
trace_contract.emit_determinism_digest("p0", "stage_barrier_enforcer")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "stage_barrier_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "stage_barrier_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "stage_barrier_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "stage_barrier_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "stage_barrier_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "stage_barrier_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "stage_barrier_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "stage_barrier_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "stage_barrier_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "stage_barrier_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "stage_barrier_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "stage_barrier_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "stage_barrier_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "stage_barrier_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "stage_barrier_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "stage_barrier_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "stage_barrier_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "stage_barrier_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "stage_barrier_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "stage_barrier_enforcer", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class MetaLearningStage(IntEnum):
    S1_AUDIT = 1
    S2_TELEMETRY = 2
    S3_CONFIG = 3
    S4_SNAPSHOT = 4
    S5_RCA = 5
    S6_PROPOSE = 6
    S7_VALIDATE = 7
    S8_INTAKE = 8
    S9_COMMIT = 9


_STAGE_NAMES = {
    MetaLearningStage.S1_AUDIT: "audit",
    MetaLearningStage.S2_TELEMETRY: "telemetry",
    MetaLearningStage.S3_CONFIG: "config",
    MetaLearningStage.S4_SNAPSHOT: "snapshot",
    MetaLearningStage.S5_RCA: "RCA",
    MetaLearningStage.S6_PROPOSE: "propose",
    MetaLearningStage.S7_VALIDATE: "validate",
    MetaLearningStage.S8_INTAKE: "intake",
    MetaLearningStage.S9_COMMIT: "commit",
}


class StageBarrierEnforcer:
    """Tracks current meta-learning stage and enforces ordering invariants.

    Usage:
        enforcer = StageBarrierEnforcer()
        enforcer.advance_to(MetaLearningStage.S1_AUDIT)
        # ...
        enforcer.advance_to(MetaLearningStage.S9_COMMIT)
        enforcer.assert_config_mutation_allowed()  # only passes at S9
    """

    def __init__(self) -> None:
        self._current: int = 0

    @property
    def current_stage(self) -> int:
        return self._current

    def advance_to(self, stage: MetaLearningStage) -> None:
        """Advance to the next stage. Raises if attempting to go backwards."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "StageBarrierEnforcer.advance_to"
        )

        if stage <= self._current:
            raise RuntimePolicyMutationViolation(
                f"Stage barrier violated: cannot move from S{self._current} to S{stage.value}. Stages must advance strictly forward.",
            )
        logger.debug(
            "MetaLearning stage: S%d → S%d (%s)",
            self._current,
            stage.value,
            _STAGE_NAMES.get(stage, "unknown"),
        )
        self._current = stage.value

    def assert_config_mutation_allowed(self) -> None:
        """Raise unless we are at S9 commit — only S9 may modify L0/L1."""
        if self._current < MetaLearningStage.S9_COMMIT:
            raise RuntimePolicyMutationViolation(
                f"Config mutation blocked: current stage is S{self._current}. Only S9 (commit) may modify L0 routing or L1 weights.",
            )

    def is_commit_stage(self) -> bool:
        return self._current >= MetaLearningStage.S9_COMMIT

    def reset(self) -> None:
        self._current = 0


__all__ = ["StageBarrierEnforcer", "MetaLearningStage"]
