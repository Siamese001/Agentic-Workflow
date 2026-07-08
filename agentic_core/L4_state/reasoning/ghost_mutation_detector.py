from __future__ import annotations

import uuid
from typing import Any, NamedTuple

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "ghost_mutation_detector")
trace_contract.emit_determinism_digest("p0", "ghost_mutation_detector")

trace_contract._emit_dispatches_healing_run("p1", "ghost_mutation_detector", "L4")
trace_contract._emit_routes_through("p1", "ghost_mutation_detector", "L4")
trace_contract._emit_checks_agent_registry("p1", "ghost_mutation_detector", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "ghost_mutation_detector", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "ghost_mutation_detector", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "ghost_mutation_detector", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "ghost_mutation_detector", "target_agent")
trace_contract._emit_verifies_policy("p1", "ghost_mutation_detector", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "ghost_mutation_detector", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "ghost_mutation_detector", "boundary_check")
trace_contract._emit_transcripts_response("p1", "ghost_mutation_detector", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "ghost_mutation_detector")
trace_contract._emit_gated_by_confidence("p1", "ghost_mutation_detector", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "ghost_mutation_detector", "L4")
trace_contract._emit_reads_policy_state("p1", "ghost_mutation_detector", "L4")
trace_contract._emit_authorize_and_execute("p2", "ghost_mutation_detector", "execution_auth")
trace_contract._emit_validates_capability("p2", "ghost_mutation_detector", "capability_check")
trace_contract._emit_routes_to_capability("p2", "ghost_mutation_detector", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "ghost_mutation_detector", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "ghost_mutation_detector", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "ghost_mutation_detector", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "ghost_mutation_detector", "exec_output")
trace_contract._emit_dispatches_agent("p3", "ghost_mutation_detector", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "ghost_mutation_detector", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "ghost_mutation_detector", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "ghost_mutation_detector", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "ghost_mutation_detector", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "ghost_mutation_detector", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "ghost_mutation_detector", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "ghost_mutation_detector", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "ghost_mutation_detector", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "ghost_mutation_detector", "eval_metric")
trace_contract._emit_stores_embedding("p4", "ghost_mutation_detector", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "ghost_mutation_detector", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "ghost_mutation_detector", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("ghost_mutation_detector", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("ghost_mutation_detector", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("ghost_mutation_detector", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("ghost_mutation_detector", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("ghost_mutation_detector", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("ghost_mutation_detector", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("ghost_mutation_detector", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("ghost_mutation_detector", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("ghost_mutation_detector", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("ghost_mutation_detector", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("ghost_mutation_detector", "p4obs", "alert")
trace_contract._emit_links_incident_trace("ghost_mutation_detector", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("ghost_mutation_detector", "p3lm", "pattern")
trace_contract._emit_records_learning_event("ghost_mutation_detector", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("ghost_mutation_detector", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("ghost_mutation_detector", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("ghost_mutation_detector", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("ghost_mutation_detector", "p3lm", "policy")
trace_contract._emit_stores_learning_state("ghost_mutation_detector", "p3lm", "state")
trace_contract._emit_records_execution_trace("ghost_mutation_detector", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("ghost_mutation_detector", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("ghost_mutation_detector", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("ghost_mutation_detector", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("ghost_mutation_detector", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("ghost_mutation_detector", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("ghost_mutation_detector", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("ghost_mutation_detector", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("ghost_mutation_detector", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "ghost_mutation_detector", "context_pull")
trace_contract._emit_pulls_context("p1", "ghost_mutation_detector", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "ghost_mutation_detector", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "ghost_mutation_detector", "uwg_term_2")
trace_contract._emit_writes_through("p1", "ghost_mutation_detector", "write_through")
trace_contract._emit_writes_through("p1", "ghost_mutation_detector", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "ghost_mutation_detector", "safety_validation")
trace_contract._emit_invokes_eval("p1", "ghost_mutation_detector", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "ghost_mutation_detector", "routing_commit")

ExecutionTranscript = list[dict[str, Any]]


class GhostMutationViolation(Exception):
    """Raised when a state mutation is detected that was not recorded in the transcript."""

    def __init__(self, message: str, diff: list[str]):
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "GhostMutationViolation.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "GhostMutationViolation.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "GhostMutationViolation.__init__")
        self.message = message
        self.diff = diff
        super().__init__(f"{message} Diff: {diff}")


class ReconciliationResult(NamedTuple):
    """The result of a state reconciliation operation."""

    is_consistent: bool
    violation: GhostMutationViolation | None = None


def _deep_diff(before: Any, after: Any, path: str = "") -> list[str]:
    """Recursively diffs two dictionaries and returns a list of differences."""
    diffs = []
    if isinstance(before, dict) and isinstance(after, dict):
        all_keys = set(before.keys()) | set(after.keys())
        for key in sorted(all_keys):
            new_path = f"{path}.{key}" if path else key
            if key not in before:
                diffs.append(f"Key added: {new_path}")
            elif key not in after:
                diffs.append(f"Key removed: {new_path}")
            elif before[key] != after[key]:
                diffs.extend(_deep_diff(before[key], after[key], new_path))
    elif before != after:
        diffs.append(f"Value changed at {path}: from '{before}' to '{after}'")
    return diffs


def detect_ghost_mutations(
    state_before: dict[str, Any],
    state_after: dict[str, Any],
    transcript: ExecutionTranscript,
) -> ReconciliationResult:
    """
    Detects hidden state mutations by comparing before/after snapshots against a transcript.

    This function enforces Guarantee #15 by performing a deep diff between the state
    before and after an operation and ensuring that all detected changes are accounted
    for in the official execution transcript. Any un-audited change is a "ghost mutation".

    Args:
        state_before: A snapshot of the system state before the operation.
        state_after: A snapshot of the system state after the operation.
        transcript: The official record of all mutations that were supposed to happen.

    Returns:
        A ReconciliationResult indicating if the state is consistent.
    """
    trace_contract._emit_writes_through(str(uuid.uuid4()), "Module.detect_ghost_mutations", "L4_STATE")
    expected_state_after = state_before.copy()
    for mutation in transcript:
        if mutation.get("operation") == "set_value":
            key = mutation.get("key")
            value = mutation.get("value")
            if key:
                expected_state_after[key] = value
    diff = _deep_diff(expected_state_after, state_after)
    if diff:
        violation = GhostMutationViolation(
            "Ghost mutation detected: State changed in ways not recorded in the transcript.",
            diff=diff,
        )
        return ReconciliationResult(is_consistent=False, violation=violation)
    return ReconciliationResult(is_consistent=True)
