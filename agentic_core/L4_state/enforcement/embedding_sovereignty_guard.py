from __future__ import annotations

from typing import Any

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

from agentic_core.runtime.lifecycle_trace_contract import (
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
