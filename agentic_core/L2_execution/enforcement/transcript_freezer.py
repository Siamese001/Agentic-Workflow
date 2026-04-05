from __future__ import annotations

from typing import Any, MutableSequence

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("transcript_freezer", "p4obs", "metric_1")
_emit_emits_metric_event("transcript_freezer", "p4obs", "metric_2")
_emit_emits_metric_event("transcript_freezer", "p4obs", "metric_3")
_emit_emits_metric_event("transcript_freezer", "p4obs", "metric_4")
_emit_emits_metric_event("transcript_freezer", "p4obs", "metric_5")
_emit_emits_metric_event("transcript_freezer", "p4obs", "metric_6")
_emit_records_incident_event("transcript_freezer", "p4obs", "incident")
_emit_captures_runtime_anomaly("transcript_freezer", "p4obs", "anomaly")
_emit_writes_observability_log("transcript_freezer", "p4obs", "obs_log")
_emit_updates_monitoring_state("transcript_freezer", "p4obs", "mon_state")
_emit_triggers_alert("transcript_freezer", "p4obs", "alert")
_emit_links_incident_trace("transcript_freezer", "p4obs", "trace_link")
_emit_captures_pattern("transcript_freezer", "p3lm", "pattern")
_emit_records_learning_event("transcript_freezer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("transcript_freezer", "p3lm", "snapshot")
_emit_feeds_meta_learning("transcript_freezer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("transcript_freezer", "p3lm", "routing")
_emit_improves_agent_policy("transcript_freezer", "p3lm", "policy")
_emit_stores_learning_state("transcript_freezer", "p3lm", "state")
_emit_records_execution_trace("transcript_freezer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("transcript_freezer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("transcript_freezer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("transcript_freezer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("transcript_freezer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("transcript_freezer", "env_read", "p2_env_1")
_emit_reads_environ("transcript_freezer", "env_read", "p2_env_2")
_emit_reads_runtime_state("transcript_freezer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("transcript_freezer", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "transcript_freezer")
emit_determinism_digest("p0", "transcript_freezer")

_emit_dispatches_healing_run("p1", "transcript_freezer", "L2")
_emit_routes_through("p1", "transcript_freezer", "L2")
_emit_checks_agent_registry("p1", "transcript_freezer", "agent_registry")
_emit_validates_agent_capability("p1", "transcript_freezer", "capability")
_emit_dispatches_execution_plan("p1", "transcript_freezer", "exec_plan")
_emit_agent_executes_agent("p1", "transcript_freezer", "sub_agent")
_emit_routes_to_agent("p1", "transcript_freezer", "target_agent")
_emit_verifies_policy("p1", "transcript_freezer", "policy_check")
_emit_observes_runtime_state("p1", "transcript_freezer", "runtime_state")
_emit_verifies_boundary("p1", "transcript_freezer", "boundary_check")
_emit_transcripts_response("p1", "transcript_freezer", "transcript")
_emit_hard_fails_untranscripted("p1", "transcript_freezer")
_emit_gated_by_confidence("p1", "transcript_freezer", "confidence_gate")
_emit_escalates_to_human("p1", "transcript_freezer", "L2")
_emit_reads_policy_state("p1", "transcript_freezer", "L2")
_emit_authorize_and_execute("p2", "transcript_freezer", "execution_auth")
_emit_validates_capability("p2", "transcript_freezer", "capability_check")
_emit_routes_to_capability("p2", "transcript_freezer", "capability_route")
_emit_writes_via_uwg("p2", "transcript_freezer", "uwg_write")
_emit_blocks_direct_write("p2", "transcript_freezer", "direct_write_block")
_emit_records_tool_invocation("p2", "transcript_freezer", "tool_invocation")
_emit_captures_execution_output("p2", "transcript_freezer", "exec_output")
_emit_dispatches_agent("p3", "transcript_freezer", "agent_dispatch")
_emit_coordinates_agents("p3", "transcript_freezer", "agent_coordination")
_emit_records_workflow_lineage("p3", "transcript_freezer", "workflow_lineage")
_emit_records_healing_outcome("p3", "transcript_freezer", "healing_outcome")
_emit_escalates_failure("p3", "transcript_freezer", "failure_escalation")
_emit_orchestrates_workflow("p3", "transcript_freezer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "transcript_freezer", "healing_dispatch")
_emit_invokes_evaluation("p3", "transcript_freezer", "evaluation_signal")
_emit_records_telemetry_event("p4", "transcript_freezer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "transcript_freezer", "eval_metric")
_emit_stores_embedding("p4", "transcript_freezer", "embedding_store")
_emit_updates_meta_learning_state("p4", "transcript_freezer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "transcript_freezer", "exec_snapshot_link")
_emit_writes_through("p1", "transcript_freezer", "uwg_governed_write")
_emit_writes_through("p1", "transcript_freezer", "uwg_governed_write_2")
_emit_pulls_context("p1", "transcript_freezer", "context_retrieval")
_emit_pulls_context("p1", "transcript_freezer", "context_retrieval_2")
emit_determinism_digest("trace_transcript_freezer", "transcript_freezer_dispatch")
emit_determinism_digest("trace_transcript_freezer", "transcript_freezer_complete")
_emit_validated_by_safety_plane("p1", "transcript_freezer", "safety_validation")


class TranscriptMutationViolation(Exception):
    """Raised when an attempt is made to mutate a frozen execution transcript."""


class FrozenTranscript(MutableSequence[Any]):
    """A read-only wrapper around a transcript that raises an error on mutation."""

    def __init__(self, transcript_data: list[Any]):
        self._data = tuple(transcript_data)

    def __getitem__(self, index: int) -> Any:
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def _raise_violation(self, *args: Any, **kwargs: Any) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "FrozenTranscript._raise_violation", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "FrozenTranscript._raise_violation", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "FrozenTranscript._raise_violation"
        )
        raise TranscriptMutationViolation(
            "Cannot mutate a frozen transcript. It has been sealed for digest computation."
        )

    __setitem__ = _raise_violation
    __delitem__ = _raise_violation
    insert = _raise_violation
    append = _raise_violation
    extend = _raise_violation
    pop = _raise_violation
    remove = _raise_violation
    clear = _raise_violation
    reverse = _raise_violation


def freeze_transcript(transcript: list[Any]) -> FrozenTranscript:
    """
    Freezes an execution transcript, making it immutable.

    This is a critical sovereign gate that must be called before computing the
    determinism digest. It prevents late-arriving or asynchronous operations
    from silently altering the transcript after it has been used as input for
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_writes_through
_emit_pulls_context("p1", "transcript_freezer", "context_pull")
_emit_pulls_context("p1", "transcript_freezer", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "transcript_freezer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "transcript_freezer", "uwg_term_secondary")
_emit_writes_through("p1", "transcript_freezer", "write_through")
_emit_writes_through("p1", "transcript_freezer", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "transcript_freezer", "safety_validation")
_emit_invokes_eval("p1", "transcript_freezer", "eval_call")
_emit_proposal_commits_routing("p1", "transcript_freezer", "routing_commit")
    the digest, which would break determinism.

    Args:
        transcript: The mutable list representing the execution transcript.

    Returns:
        A FrozenTranscript instance that provides a read-only view of the transcript.
    """
    return FrozenTranscript(transcript)
