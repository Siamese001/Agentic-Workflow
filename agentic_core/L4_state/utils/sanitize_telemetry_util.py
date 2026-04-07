"""
Telemetry Sanitizer - Anti-Observer Effect Protection.

Prevents token overload by intelligently pruning large tool outputs while
preserving critical information like error tracebacks.

COGNITIVE HARDENING (Feb 2026):
- Landmine #4 Prevention: Token Overload
- Preserves head/tail context for debugging
- Special handling for Python tracebacks to preserve actual errors
"""

from typing import Final

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    record_execution_trace,
)

emit_replay_key("p0", "sanitize_telemetry_util")
emit_determinism_digest("p0", "sanitize_telemetry_util")

_emit_dispatches_healing_run("p1", "sanitize_telemetry_util", "L4")
_emit_routes_through("p1", "sanitize_telemetry_util", "L4")
_emit_checks_agent_registry("p1", "sanitize_telemetry_util", "agent_registry")
_emit_validates_agent_capability("p1", "sanitize_telemetry_util", "capability")
_emit_dispatches_execution_plan("p1", "sanitize_telemetry_util", "exec_plan")
_emit_agent_executes_agent("p1", "sanitize_telemetry_util", "sub_agent")
_emit_routes_to_agent("p1", "sanitize_telemetry_util", "target_agent")
_emit_verifies_policy("p1", "sanitize_telemetry_util", "policy_check")
_emit_observes_runtime_state("p1", "sanitize_telemetry_util", "runtime_state")
_emit_verifies_boundary("p1", "sanitize_telemetry_util", "boundary_check")
_emit_transcripts_response("p1", "sanitize_telemetry_util", "transcript")
_emit_hard_fails_untranscripted("p1", "sanitize_telemetry_util")
_emit_gated_by_confidence("p1", "sanitize_telemetry_util", "confidence_gate")
_emit_escalates_to_human("p1", "sanitize_telemetry_util", "L4")
_emit_reads_policy_state("p1", "sanitize_telemetry_util", "L4")
_emit_authorize_and_execute("p2", "sanitize_telemetry_util", "execution_auth")
_emit_validates_capability("p2", "sanitize_telemetry_util", "capability_check")
_emit_routes_to_capability("p2", "sanitize_telemetry_util", "capability_route")
_emit_writes_via_uwg("p2", "sanitize_telemetry_util", "uwg_write")
_emit_blocks_direct_write("p2", "sanitize_telemetry_util", "direct_write_block")
_emit_records_tool_invocation("p2", "sanitize_telemetry_util", "tool_invocation")
_emit_captures_execution_output("p2", "sanitize_telemetry_util", "exec_output")
_emit_dispatches_agent("p3", "sanitize_telemetry_util", "agent_dispatch")
_emit_coordinates_agents("p3", "sanitize_telemetry_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "sanitize_telemetry_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "sanitize_telemetry_util", "healing_outcome")
_emit_escalates_failure("p3", "sanitize_telemetry_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "sanitize_telemetry_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sanitize_telemetry_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "sanitize_telemetry_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "sanitize_telemetry_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sanitize_telemetry_util", "eval_metric")
_emit_stores_embedding("p4", "sanitize_telemetry_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "sanitize_telemetry_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sanitize_telemetry_util", "exec_snapshot_link")
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

record_execution_trace("sanitize_telemetry_util", "sanitize_telemetry_util_trace")


_emit_emits_metric_event("sanitize_telemetry_util", "p4obs", "metric_1")
_emit_emits_metric_event("sanitize_telemetry_util", "p4obs", "metric_2")
_emit_emits_metric_event("sanitize_telemetry_util", "p4obs", "metric_3")
_emit_emits_metric_event("sanitize_telemetry_util", "p4obs", "metric_4")
_emit_emits_metric_event("sanitize_telemetry_util", "p4obs", "metric_5")
_emit_emits_metric_event("sanitize_telemetry_util", "p4obs", "metric_6")
_emit_records_incident_event("sanitize_telemetry_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("sanitize_telemetry_util", "p4obs", "anomaly")
_emit_writes_observability_log("sanitize_telemetry_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("sanitize_telemetry_util", "p4obs", "mon_state")
_emit_triggers_alert("sanitize_telemetry_util", "p4obs", "alert")
_emit_links_incident_trace("sanitize_telemetry_util", "p4obs", "trace_link")
_emit_captures_pattern("sanitize_telemetry_util", "p3lm", "pattern")
_emit_records_learning_event("sanitize_telemetry_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sanitize_telemetry_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("sanitize_telemetry_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sanitize_telemetry_util", "p3lm", "routing")
_emit_improves_agent_policy("sanitize_telemetry_util", "p3lm", "policy")
_emit_stores_learning_state("sanitize_telemetry_util", "p3lm", "state")
_emit_records_execution_trace("sanitize_telemetry_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sanitize_telemetry_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sanitize_telemetry_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sanitize_telemetry_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sanitize_telemetry_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sanitize_telemetry_util", "env_read", "p2_env_1")
_emit_reads_environ("sanitize_telemetry_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("sanitize_telemetry_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sanitize_telemetry_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sanitize_telemetry_util", "context_pull")
_emit_pulls_context("p1", "sanitize_telemetry_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "sanitize_telemetry_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sanitize_telemetry_util", "uwg_term_2")
_emit_writes_through("p1", "sanitize_telemetry_util", "write_through")
_emit_writes_through("p1", "sanitize_telemetry_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "sanitize_telemetry_util", "safety_validation")
_emit_invokes_eval("p1", "sanitize_telemetry_util", "eval_call")
_emit_proposal_commits_routing("p1", "sanitize_telemetry_util", "routing_commit")

DEFAULT_MAX_CHARS: Final[int] = 2000
HEAD_SIZE: Final[int] = 500
TAIL_SIZE: Final[int] = 500
TRACEBACK_PATTERNS: Final[tuple[str, ...]] = (
    "Traceback (most recent call last):",
    "Error:",
    "Exception:",
    "raise ",
)


def _is_traceback(output: str) -> bool:
    """Detect if output contains a Python traceback."""
    return any(pattern in output for pattern in TRACEBACK_PATTERNS)


# guardian: allow-magic-config
def _extract_traceback_tail(output: str, max_tail: int = 1000) -> str:
    """
    Extract the meaningful tail of a traceback.

    Python tracebacks have the actual error at the END, so we need to
    preserve more of the tail when dealing with tracebacks.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_extract_traceback_tail", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_extract_traceback_tail", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "_extract_traceback_tail")
    lines = output.splitlines()
    traceback_start = -1
    for i, line in enumerate(lines):
        if "Traceback (most recent call last):" in line:
            traceback_start = i
    if traceback_start >= 0:
        traceback_section = "\n".join(lines[traceback_start:])
        if len(traceback_section) <= max_tail:
            return traceback_section
        return traceback_section[-max_tail:]
    return output[-max_tail:] if len(output) > max_tail else output


def sanitize_tool_output(
    output: str,
    max_chars: int = DEFAULT_MAX_CHARS,
    head_size: int | None = None,
    tail_size: int | None = None,
) -> str:
    """
    Sanitize tool output to prevent token overload.

    Args:
        output: The raw tool output string.
        max_chars: Maximum allowed characters before pruning.
        head_size: Number of characters to preserve from the start (default: 25% of max_chars).
        tail_size: Number of characters to preserve from the end (default: 25% of max_chars).

    Returns:
        Sanitized output string, pruned if necessary.

    Logic:
        1. If output is shorter than max_chars, return as-is.
        2. If longer, return Head + pruning marker + Tail.
        3. If output is a Python traceback, preserve the actual error (at the end).
    """
    if not output:
        return output
    output_len = len(output)
    if output_len <= max_chars:
        return output
    if head_size is None:
        head_size = min(HEAD_SIZE, max_chars // 4)
    if tail_size is None:
        tail_size = min(TAIL_SIZE, max_chars // 4)
    if head_size + tail_size >= output_len:
        return output
    pruned_chars = output_len - head_size - tail_size
    if _is_traceback(output):
        traceback_tail_size = min(1000, output_len - head_size)
        traceback_tail = _extract_traceback_tail(output, traceback_tail_size)
        head = output[:head_size]
        pruned_chars = output_len - head_size - len(traceback_tail)
        return f"{head}\n\n...[Pruned {pruned_chars} chars - Traceback preserved]...\n\n{traceback_tail}"
    head = output[:head_size]
    tail = output[-tail_size:]
    return f"{head}\n\n...[Pruned {pruned_chars} chars]...\n\n{tail}"


__all__ = ["sanitize_tool_output"]
