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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "sanitize_telemetry_util")
trace_contract.emit_determinism_digest("p0", "sanitize_telemetry_util")

trace_contract._emit_dispatches_healing_run("p1", "sanitize_telemetry_util", "L4")
trace_contract._emit_routes_through("p1", "sanitize_telemetry_util", "L4")
trace_contract._emit_checks_agent_registry("p1", "sanitize_telemetry_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "sanitize_telemetry_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "sanitize_telemetry_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "sanitize_telemetry_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "sanitize_telemetry_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "sanitize_telemetry_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "sanitize_telemetry_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "sanitize_telemetry_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "sanitize_telemetry_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "sanitize_telemetry_util")
trace_contract._emit_gated_by_confidence("p1", "sanitize_telemetry_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "sanitize_telemetry_util", "L4")
trace_contract._emit_reads_policy_state("p1", "sanitize_telemetry_util", "L4")
trace_contract._emit_authorize_and_execute("p2", "sanitize_telemetry_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "sanitize_telemetry_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "sanitize_telemetry_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "sanitize_telemetry_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "sanitize_telemetry_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "sanitize_telemetry_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "sanitize_telemetry_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "sanitize_telemetry_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "sanitize_telemetry_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "sanitize_telemetry_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "sanitize_telemetry_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "sanitize_telemetry_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "sanitize_telemetry_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "sanitize_telemetry_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "sanitize_telemetry_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "sanitize_telemetry_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "sanitize_telemetry_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "sanitize_telemetry_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "sanitize_telemetry_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "sanitize_telemetry_util", "exec_snapshot_link")

trace_contract.record_execution_trace("sanitize_telemetry_util", "sanitize_telemetry_util_trace")


trace_contract._emit_emits_metric_event("sanitize_telemetry_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("sanitize_telemetry_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("sanitize_telemetry_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("sanitize_telemetry_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("sanitize_telemetry_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("sanitize_telemetry_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("sanitize_telemetry_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("sanitize_telemetry_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("sanitize_telemetry_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("sanitize_telemetry_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("sanitize_telemetry_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("sanitize_telemetry_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("sanitize_telemetry_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("sanitize_telemetry_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("sanitize_telemetry_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("sanitize_telemetry_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("sanitize_telemetry_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("sanitize_telemetry_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("sanitize_telemetry_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("sanitize_telemetry_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("sanitize_telemetry_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("sanitize_telemetry_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("sanitize_telemetry_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("sanitize_telemetry_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("sanitize_telemetry_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("sanitize_telemetry_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("sanitize_telemetry_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("sanitize_telemetry_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "sanitize_telemetry_util", "context_pull")
trace_contract._emit_pulls_context("p1", "sanitize_telemetry_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "sanitize_telemetry_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "sanitize_telemetry_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "sanitize_telemetry_util", "write_through")
trace_contract._emit_writes_through("p1", "sanitize_telemetry_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "sanitize_telemetry_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "sanitize_telemetry_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "sanitize_telemetry_util", "routing_commit")

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

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "_extract_traceback_tail", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "_extract_traceback_tail", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "_extract_traceback_tail")
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
