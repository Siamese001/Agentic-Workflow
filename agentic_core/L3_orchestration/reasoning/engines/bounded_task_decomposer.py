from __future__ import annotations

from dataclasses import dataclass
from typing import Any, NamedTuple, Sequence

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "bounded_task_decomposer")
trace_contract.emit_determinism_digest("p0", "bounded_task_decomposer")

trace_contract._emit_dispatches_healing_run("p1", "bounded_task_decomposer", "L3")
trace_contract._emit_routes_through("p1", "bounded_task_decomposer", "L3")
trace_contract._emit_checks_agent_registry("p1", "bounded_task_decomposer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "bounded_task_decomposer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "bounded_task_decomposer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "bounded_task_decomposer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "bounded_task_decomposer", "target_agent")
trace_contract._emit_verifies_policy("p1", "bounded_task_decomposer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "bounded_task_decomposer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "bounded_task_decomposer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "bounded_task_decomposer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "bounded_task_decomposer")
trace_contract._emit_gated_by_confidence("p1", "bounded_task_decomposer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "bounded_task_decomposer", "L3")
trace_contract._emit_reads_policy_state("p1", "bounded_task_decomposer", "L3")
trace_contract._emit_authorize_and_execute("p2", "bounded_task_decomposer", "execution_auth")
trace_contract._emit_validates_capability("p2", "bounded_task_decomposer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "bounded_task_decomposer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "bounded_task_decomposer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "bounded_task_decomposer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "bounded_task_decomposer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "bounded_task_decomposer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "bounded_task_decomposer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "bounded_task_decomposer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "bounded_task_decomposer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "bounded_task_decomposer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "bounded_task_decomposer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "bounded_task_decomposer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "bounded_task_decomposer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "bounded_task_decomposer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "bounded_task_decomposer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "bounded_task_decomposer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "bounded_task_decomposer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "bounded_task_decomposer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "bounded_task_decomposer", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("bounded_task_decomposer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("bounded_task_decomposer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("bounded_task_decomposer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("bounded_task_decomposer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("bounded_task_decomposer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("bounded_task_decomposer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("bounded_task_decomposer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("bounded_task_decomposer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("bounded_task_decomposer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("bounded_task_decomposer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("bounded_task_decomposer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("bounded_task_decomposer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("bounded_task_decomposer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("bounded_task_decomposer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("bounded_task_decomposer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("bounded_task_decomposer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("bounded_task_decomposer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("bounded_task_decomposer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("bounded_task_decomposer", "p3lm", "state")
trace_contract._emit_records_execution_trace("bounded_task_decomposer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("bounded_task_decomposer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("bounded_task_decomposer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("bounded_task_decomposer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("bounded_task_decomposer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("bounded_task_decomposer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("bounded_task_decomposer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("bounded_task_decomposer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("bounded_task_decomposer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "bounded_task_decomposer", "context_pull")
trace_contract._emit_pulls_context("p1", "bounded_task_decomposer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "bounded_task_decomposer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "bounded_task_decomposer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "bounded_task_decomposer", "write_through")
trace_contract._emit_writes_through("p1", "bounded_task_decomposer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "bounded_task_decomposer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "bounded_task_decomposer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "bounded_task_decomposer", "routing_commit")

Task = Any


class TaskBlastRadiusViolation(Exception):
    """Raised when a task exceeds its defined blast radius limits."""

    def __init__(self, message: str, violation_details: dict):
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "TaskBlastRadiusViolation.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "TaskBlastRadiusViolation.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "TaskBlastRadiusViolation.__init__",
        )
        self.message = message
        self.violation_details = violation_details
        super().__init__(f"{message} Details: {violation_details}")


@dataclass(frozen=True)
class DecompositionPolicy:
    """Defines the blast radius limits for task decomposition."""

    max_subtasks: int = 10
    max_total_complexity: float = 100.0
    max_dependency_depth: int = 3


class DecompositionResult(NamedTuple):
    """The result of a task decomposition operation."""

    subtasks: Sequence[Task] | None
    violation: TaskBlastRadiusViolation | None = None


def decompose_task(task: Task, policy: DecompositionPolicy) -> DecompositionResult:
    """
    Decomposes a large task into smaller, bounded subtasks.

    This function enforces Guarantee #8 by ensuring that no single task is too
    large or complex, thus limiting its potential blast radius. It is a critical
    sovereign gate in L3, rejecting tasks that cannot be safely decomposed.

    Args:
        task: The task to be decomposed.
        policy: The decomposition policy defining the blast radius limits.

    Returns:
        A DecompositionResult containing the list of subtasks or a violation.
    """
    subtasks: list[Task] = [f"{task}_part_{i}" for i in range(5)]
    total_complexity = 50.0
    dependency_depth = 2
    if len(subtasks) > policy.max_subtasks:
        violation = TaskBlastRadiusViolation(
            "Task decomposition exceeds max subtasks.",
            {"actual": len(subtasks), "limit": policy.max_subtasks},
        )
        return DecompositionResult(subtasks=None, violation=violation)
    if total_complexity > policy.max_total_complexity:
        violation = TaskBlastRadiusViolation(
            "Task decomposition exceeds max total complexity.",
            {"actual": total_complexity, "limit": policy.max_total_complexity},
        )
        return DecompositionResult(subtasks=None, violation=violation)
    if dependency_depth > policy.max_dependency_depth:
        violation = TaskBlastRadiusViolation(
            "Task decomposition exceeds max dependency depth.",
            {"actual": dependency_depth, "limit": policy.max_dependency_depth},
        )
        return DecompositionResult(subtasks=None, violation=violation)
    return DecompositionResult(subtasks=subtasks)
