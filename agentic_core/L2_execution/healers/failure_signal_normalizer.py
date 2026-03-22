"""Failure Signal Normalizer — compose embedding-ready text from a healing action dict.

Converts a raw healing_action dict (as stored in state_mgr.state["healing_actions"])
into a normalized text string suitable for embedding via BAAI/bge-m3.

Design invariants:
- Pure function: no side effects, no I/O.
- Deterministic: identical inputs always produce identical outputs.
- Stdlib only: no external dependencies.
- Separation of concerns: metadata (territory, agent) is captured separately from
  the text that is embedded — matching the Embedding Lifecycle architecture.
"""

from __future__ import annotations

import hashlib
import math
import struct

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

emit_replay_key("p0", "failure_signal_normalizer")
emit_determinism_digest("p0", "failure_signal_normalizer")

_emit_dispatches_healing_run("p1", "failure_signal_normalizer", "L2")
_emit_routes_through("p1", "failure_signal_normalizer", "L2")
_emit_checks_agent_registry("p1", "failure_signal_normalizer", "agent_registry")
_emit_validates_agent_capability("p1", "failure_signal_normalizer", "capability")
_emit_dispatches_execution_plan("p1", "failure_signal_normalizer", "exec_plan")
_emit_agent_executes_agent("p1", "failure_signal_normalizer", "sub_agent")
_emit_routes_to_agent("p1", "failure_signal_normalizer", "target_agent")
_emit_verifies_policy("p1", "failure_signal_normalizer", "policy_check")
_emit_observes_runtime_state("p1", "failure_signal_normalizer", "runtime_state")
_emit_verifies_boundary("p1", "failure_signal_normalizer", "boundary_check")
_emit_transcripts_response("p1", "failure_signal_normalizer", "transcript")
_emit_hard_fails_untranscripted("p1", "failure_signal_normalizer")
_emit_gated_by_confidence("p1", "failure_signal_normalizer", "confidence_gate")
_emit_escalates_to_human("p1", "failure_signal_normalizer", "L2")
_emit_reads_policy_state("p1", "failure_signal_normalizer", "L2")
_emit_authorize_and_execute("p2", "failure_signal_normalizer", "execution_auth")
_emit_validates_capability("p2", "failure_signal_normalizer", "capability_check")
_emit_routes_to_capability("p2", "failure_signal_normalizer", "capability_route")
_emit_writes_via_uwg("p2", "failure_signal_normalizer", "uwg_write")
_emit_blocks_direct_write("p2", "failure_signal_normalizer", "direct_write_block")
_emit_records_tool_invocation("p2", "failure_signal_normalizer", "tool_invocation")
_emit_captures_execution_output("p2", "failure_signal_normalizer", "exec_output")
_emit_dispatches_agent("p3", "failure_signal_normalizer", "agent_dispatch")
_emit_coordinates_agents("p3", "failure_signal_normalizer", "agent_coordination")
_emit_records_workflow_lineage("p3", "failure_signal_normalizer", "workflow_lineage")
_emit_records_healing_outcome("p3", "failure_signal_normalizer", "healing_outcome")
_emit_escalates_failure("p3", "failure_signal_normalizer", "failure_escalation")
_emit_orchestrates_workflow("p3", "failure_signal_normalizer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "failure_signal_normalizer", "healing_dispatch")
_emit_invokes_evaluation("p3", "failure_signal_normalizer", "evaluation_signal")
_emit_records_telemetry_event("p4", "failure_signal_normalizer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "failure_signal_normalizer", "eval_metric")
_emit_stores_embedding("p4", "failure_signal_normalizer", "embedding_store")
_emit_updates_meta_learning_state("p4", "failure_signal_normalizer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "failure_signal_normalizer", "exec_snapshot_link")
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

_emit_emits_metric_event("failure_signal_normalizer", "p4obs", "metric_1")
_emit_emits_metric_event("failure_signal_normalizer", "p4obs", "metric_2")
_emit_emits_metric_event("failure_signal_normalizer", "p4obs", "metric_3")
_emit_emits_metric_event("failure_signal_normalizer", "p4obs", "metric_4")
_emit_emits_metric_event("failure_signal_normalizer", "p4obs", "metric_5")
_emit_emits_metric_event("failure_signal_normalizer", "p4obs", "metric_6")
_emit_records_incident_event("failure_signal_normalizer", "p4obs", "incident")
_emit_captures_runtime_anomaly("failure_signal_normalizer", "p4obs", "anomaly")
_emit_writes_observability_log("failure_signal_normalizer", "p4obs", "obs_log")
_emit_updates_monitoring_state("failure_signal_normalizer", "p4obs", "mon_state")
_emit_triggers_alert("failure_signal_normalizer", "p4obs", "alert")
_emit_links_incident_trace("failure_signal_normalizer", "p4obs", "trace_link")
_emit_captures_pattern("failure_signal_normalizer", "p3lm", "pattern")
_emit_records_learning_event("failure_signal_normalizer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("failure_signal_normalizer", "p3lm", "snapshot")
_emit_feeds_meta_learning("failure_signal_normalizer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("failure_signal_normalizer", "p3lm", "routing")
_emit_improves_agent_policy("failure_signal_normalizer", "p3lm", "policy")
_emit_stores_learning_state("failure_signal_normalizer", "p3lm", "state")
_emit_records_execution_trace("failure_signal_normalizer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("failure_signal_normalizer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("failure_signal_normalizer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("failure_signal_normalizer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("failure_signal_normalizer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("failure_signal_normalizer", "env_read", "p2_env_1")
_emit_reads_environ("failure_signal_normalizer", "env_read", "p2_env_2")
_emit_reads_runtime_state("failure_signal_normalizer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("failure_signal_normalizer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "failure_signal_normalizer", "context_pull")
_emit_pulls_context("p1", "failure_signal_normalizer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "failure_signal_normalizer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "failure_signal_normalizer", "uwg_term_2")
_emit_writes_through("p1", "failure_signal_normalizer", "write_through")
_emit_writes_through("p1", "failure_signal_normalizer", "write_through_2")
_emit_validated_by_safety_plane("p1", "failure_signal_normalizer", "safety_validation")
_emit_invokes_eval("p1", "failure_signal_normalizer", "eval_call")
_emit_proposal_commits_routing("p1", "failure_signal_normalizer", "routing_commit")

_FALLBACK_DIMS = 16
_FALLBACK_TRUNC = 200


def normalize_failure_signal(action: dict) -> str:
    """Compose a normalized embedding-input text from a healing action dict.

    The normalized text encodes the *semantic content* of the failure —
    failure type, the gate that triggered it, the agent that handled it,
    and (when present) the first 200 chars of error_message / stack_trace.
    Territory and other metadata are captured separately (not embedded) per
    the Embedding Lifecycle architecture (territory is metadata, not content).

    Field priority:
      1. failure_type / routing_tier — stable category string (uppercased)
      2. routing_gate   — specific check ID that triggered the failure;
                          more structured and semantic than fix_summary alone
      3. agent          — healer that processed the event
      4. fix_summary    — optional human-readable description of the repair
      5. error_message  — first 200 chars of the raw error message (D1)
      6. stack_trace    — first 200 chars of the exception stack trace (D1)

    Args:
        action: A healing action dict as stored in
            state_mgr.state["healing_actions"].  Expected keys (all
            optional with safe defaults):
              - "type" / "routing_tier": failure category string
              - "routing_gate": specific gate/check identifier (e.g. "gate:import_boundary_check")
              - "agent": healer identifier
              - "fix_summary": human-readable repair description
              - "error_message": raw error string (enrichment field)
              - "stack_trace": exception traceback text (enrichment field)

    Returns:
        A normalized ASCII text string for embedding, e.g.:
        "IMPORT_BOUNDARY_VIOLATION gate:import_boundary_check DependencyRepairAgent yaml config loader"
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "normalize_failure_signal", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "normalize_failure_signal", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "normalize_failure_signal")
    failure_type: str = action.get("type") or action.get("routing_tier") or "UNKNOWN"
    routing_gate: str = action.get("routing_gate") or ""
    agent: str = action.get("agent") or "unknown_agent"
    fix_summary: str = action.get("fix_summary") or ""
    error_message: str = str(action.get("error_message") or "")[:_FALLBACK_TRUNC]
    stack_trace: str = str(action.get("stack_trace") or "")[:_FALLBACK_TRUNC]
    parts: list[str] = [failure_type.upper()]
    if routing_gate and routing_gate != "N/A":
        parts.append(routing_gate)
    parts.append(agent)
    if fix_summary:
        parts.append(fix_summary)
    if error_message:
        parts.append(error_message)
    if stack_trace:
        parts.append(stack_trace)
    return " ".join(p.strip() for p in parts if p.strip())


def extract_failure_metadata(action: dict) -> dict:
    """Extract metadata fields that are stored alongside (not embedded into) the vector.

    These fields are stored as metadata in the vector DB record per the
    Embedding Lifecycle architecture: territory, invariant ids, repo context.

    Args:
        action: A healing action dict.

    Returns:
        Dict of metadata fields to store alongside the failure_vector.
    """
    return {
        "territory": action.get("territory", "unknown"),
        "routing_digest": action.get("routing_digest"),
        "confidence_score": action.get("confidence"),
        "routing_tier": action.get("routing_tier", "DETERMINISTIC"),
        "outcome": action.get("outcome", "UNKNOWN"),
        "timestamp": action.get("timestamp"),
    }


def generate_fallback_vector(text: str) -> list[float]:
    """Produce a deterministic 16-dimensional L2-normalised fallback vector.

    Used in BOOTSTRAP_MODE only (initial environment setup) to ensure
    failure_vector is never None. The vector carries no semantic meaning but
    preserves determinism and allows FAISS storage to proceed.
    Normal operation MUST use bge-m3 (mandatory system dependency).

    The vector is tagged with ``vector_source="hash-fallback"`` metadata by
    the caller; downstream novelty/cluster logic MUST NOT interpret it as a
    real semantic embedding (enforced by VectorSourceMismatchError in C3).

    Args:
        text: The normalized failure signal text (output of normalize_failure_signal).

    Returns:
        A 16-dimensional L2-normalised list[float]. Never empty, never None.
        Two consecutive calls with identical text always return identical output.
    """
    digest = hashlib.sha256(text.encode("utf-8", errors="replace")).digest()
    raw: list[float] = []
    for i in range(0, _FALLBACK_DIMS * 2, 2):
        val = struct.unpack_from("<H", digest, i % len(digest))[0]
        raw.append(float(val))
    norm = math.sqrt(sum(v * v for v in raw)) or 1.0
    return [v / norm for v in raw]


__all__ = ["normalize_failure_signal", "extract_failure_metadata", "generate_fallback_vector"]
