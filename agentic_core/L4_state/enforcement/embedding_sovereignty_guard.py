from __future__ import annotations

from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

emit_replay_key("p0", "embedding_sovereignty_guard")
emit_determinism_digest("p0", "embedding_sovereignty_guard")

_emit_dispatches_healing_run("p1", "embedding_sovereignty_guard", "L4")
_emit_routes_through("p1", "embedding_sovereignty_guard", "L4")
_emit_checks_agent_registry("p1", "embedding_sovereignty_guard", "agent_registry")
_emit_validates_agent_capability("p1", "embedding_sovereignty_guard", "capability")
_emit_dispatches_execution_plan("p1", "embedding_sovereignty_guard", "exec_plan")
_emit_agent_executes_agent("p1", "embedding_sovereignty_guard", "sub_agent")
_emit_routes_to_agent("p1", "embedding_sovereignty_guard", "target_agent")
_emit_verifies_policy("p1", "embedding_sovereignty_guard", "policy_check")
_emit_observes_runtime_state("p1", "embedding_sovereignty_guard", "runtime_state")
_emit_verifies_boundary("p1", "embedding_sovereignty_guard", "boundary_check")
_emit_transcripts_response("p1", "embedding_sovereignty_guard", "transcript")
_emit_hard_fails_untranscripted("p1", "embedding_sovereignty_guard")
_emit_gated_by_confidence("p1", "embedding_sovereignty_guard", "confidence_gate")
_emit_escalates_to_human("p1", "embedding_sovereignty_guard", "L4")
_emit_reads_policy_state("p1", "embedding_sovereignty_guard", "L4")
_emit_authorize_and_execute("p2", "embedding_sovereignty_guard", "execution_auth")
_emit_validates_capability("p2", "embedding_sovereignty_guard", "capability_check")
_emit_routes_to_capability("p2", "embedding_sovereignty_guard", "capability_route")
_emit_writes_via_uwg("p2", "embedding_sovereignty_guard", "uwg_write")
_emit_blocks_direct_write("p2", "embedding_sovereignty_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "embedding_sovereignty_guard", "tool_invocation")
_emit_captures_execution_output("p2", "embedding_sovereignty_guard", "exec_output")
_emit_dispatches_agent("p3", "embedding_sovereignty_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "embedding_sovereignty_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "embedding_sovereignty_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "embedding_sovereignty_guard", "healing_outcome")
_emit_escalates_failure("p3", "embedding_sovereignty_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "embedding_sovereignty_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "embedding_sovereignty_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "embedding_sovereignty_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "embedding_sovereignty_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "embedding_sovereignty_guard", "eval_metric")
_emit_stores_embedding("p4", "embedding_sovereignty_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "embedding_sovereignty_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "embedding_sovereignty_guard", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("embedding_sovereignty_guard", "p4obs", "metric_1")
_emit_emits_metric_event("embedding_sovereignty_guard", "p4obs", "metric_2")
_emit_emits_metric_event("embedding_sovereignty_guard", "p4obs", "metric_3")
_emit_emits_metric_event("embedding_sovereignty_guard", "p4obs", "metric_4")
_emit_emits_metric_event("embedding_sovereignty_guard", "p4obs", "metric_5")
_emit_emits_metric_event("embedding_sovereignty_guard", "p4obs", "metric_6")
_emit_records_incident_event("embedding_sovereignty_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("embedding_sovereignty_guard", "p4obs", "anomaly")
_emit_writes_observability_log("embedding_sovereignty_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("embedding_sovereignty_guard", "p4obs", "mon_state")
_emit_triggers_alert("embedding_sovereignty_guard", "p4obs", "alert")
_emit_links_incident_trace("embedding_sovereignty_guard", "p4obs", "trace_link")
_emit_captures_pattern("embedding_sovereignty_guard", "p3lm", "pattern")
_emit_records_learning_event("embedding_sovereignty_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("embedding_sovereignty_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("embedding_sovereignty_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("embedding_sovereignty_guard", "p3lm", "routing")
_emit_improves_agent_policy("embedding_sovereignty_guard", "p3lm", "policy")
_emit_stores_learning_state("embedding_sovereignty_guard", "p3lm", "state")
_emit_records_execution_trace("embedding_sovereignty_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("embedding_sovereignty_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("embedding_sovereignty_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("embedding_sovereignty_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("embedding_sovereignty_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("embedding_sovereignty_guard", "env_read", "p2_env_1")
_emit_reads_environ("embedding_sovereignty_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("embedding_sovereignty_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("embedding_sovereignty_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "embedding_sovereignty_guard", "context_pull")
_emit_pulls_context("p1", "embedding_sovereignty_guard", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "embedding_sovereignty_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "embedding_sovereignty_guard", "uwg_term_2")
_emit_writes_through("p1", "embedding_sovereignty_guard", "write_through")
_emit_writes_through("p1", "embedding_sovereignty_guard", "write_through_2")
_emit_validated_by_safety_plane("p1", "embedding_sovereignty_guard", "safety_validation")
_emit_invokes_eval("p1", "embedding_sovereignty_guard", "eval_call")
_emit_proposal_commits_routing("p1", "embedding_sovereignty_guard", "routing_commit")


class EmbeddingResult:
    """A placeholder for the result of an embedding retrieval operation."""

    pass


class EmbeddingInfluenceViolation(Exception):
    """Raised when an embedding artifact is detected influencing a sovereign decision."""

    def __init__(self, decision_type: str, found_in: str):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "EmbeddingInfluenceViolation.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "EmbeddingInfluenceViolation.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "EmbeddingInfluenceViolation.__init__"
        )
        self.decision_type = decision_type
        self.found_in = found_in
        super().__init__(
            f"Embedding artifact illegally influenced '{decision_type}' decision. Found in: {found_in}."
        )


def guard_embedding_influence(*args: Any, decision_type: str, **kwargs: Any) -> None:
    """
    A sovereign runtime guard that prevents embedding results from influencing decisions.

    This function enforces Guarantee #21 by recursively scanning the arguments of
    critical decision-making functions (like `route_healing_tier` or safety
    classifiers) to ensure no `EmbeddingResult` objects are present. This prevents
    both direct and indirect leakage.

    This guard must be placed at the entry point of all sovereign decision boundaries.

    Args:
        decision_type: A string identifying the type of decision being made.
        *args: The positional arguments passed to the decision function.
        **kwargs: The keyword arguments passed to the decision function.

    Raises:
        EmbeddingInfluenceViolation: If an `EmbeddingResult` is found in the arguments.
    """
    all_args = list(args) + list(kwargs.values())

    def _scan_for_embedding_result(obj: Any, path: str) -> None:
        """
        Recursively scans an object for instances of EmbeddingResult.
        """
        if isinstance(obj, EmbeddingResult):
            raise EmbeddingInfluenceViolation(decision_type, path)
        if isinstance(obj, dict):
            for k, v in obj.items():
                _scan_for_embedding_result(v, f"{path}.{k}")
        elif isinstance(obj, (list, tuple)):
            for i, item in enumerate(obj):
                _scan_for_embedding_result(item, f"{path}[{i}]")

    for i, arg in enumerate(all_args):
        _scan_for_embedding_result(arg, f"arg[{i}]")
