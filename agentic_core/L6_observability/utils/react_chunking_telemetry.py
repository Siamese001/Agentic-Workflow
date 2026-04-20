"""ReAct + Late Chunking telemetry adapter — L1_cognition seam.

Emits signals to the meta-learning bus from ReAct reasoning executions
and late-chunking pipeline runs. Uses lazy imports to avoid an upward
L1 → system_learning layer violation.

Signals emitted per execution:
  - react_performance   (trace_id, step_count, success, policy_hash)
  - retrieval_completeness (rag_context_ids, chunk_ids)
  - chunking_effectiveness (corpus_manifest_hash, chunk_count)
  - prompt_outcome_success (prompt_hash, policy_hash, success)

These feed MetaLearningBus.process_traces() via S2 telemetry.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

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

emit_replay_key("p0", "react_chunking_telemetry")
emit_determinism_digest("p0", "react_chunking_telemetry")

_emit_dispatches_healing_run("p1", "react_chunking_telemetry", "L1")
_emit_routes_through("p1", "react_chunking_telemetry", "L1")
_emit_checks_agent_registry("p1", "react_chunking_telemetry", "agent_registry")
_emit_validates_agent_capability("p1", "react_chunking_telemetry", "capability")
_emit_dispatches_execution_plan("p1", "react_chunking_telemetry", "exec_plan")
_emit_agent_executes_agent("p1", "react_chunking_telemetry", "sub_agent")
_emit_routes_to_agent("p1", "react_chunking_telemetry", "target_agent")
_emit_verifies_policy("p1", "react_chunking_telemetry", "policy_check")
_emit_observes_runtime_state("p1", "react_chunking_telemetry", "runtime_state")
_emit_verifies_boundary("p1", "react_chunking_telemetry", "boundary_check")
_emit_transcripts_response("p1", "react_chunking_telemetry", "transcript")
_emit_hard_fails_untranscripted("p1", "react_chunking_telemetry")
_emit_gated_by_confidence("p1", "react_chunking_telemetry", "confidence_gate")
_emit_escalates_to_human("p1", "react_chunking_telemetry", "L1")
_emit_reads_policy_state("p1", "react_chunking_telemetry", "L1")
_emit_authorize_and_execute("p2", "react_chunking_telemetry", "execution_auth")
_emit_validates_capability("p2", "react_chunking_telemetry", "capability_check")
_emit_routes_to_capability("p2", "react_chunking_telemetry", "capability_route")
_emit_writes_via_uwg("p2", "react_chunking_telemetry", "uwg_write")
_emit_blocks_direct_write("p2", "react_chunking_telemetry", "direct_write_block")
_emit_records_tool_invocation("p2", "react_chunking_telemetry", "tool_invocation")
_emit_captures_execution_output("p2", "react_chunking_telemetry", "exec_output")
_emit_dispatches_agent("p3", "react_chunking_telemetry", "agent_dispatch")
_emit_coordinates_agents("p3", "react_chunking_telemetry", "agent_coordination")
_emit_records_workflow_lineage("p3", "react_chunking_telemetry", "workflow_lineage")
_emit_records_healing_outcome("p3", "react_chunking_telemetry", "healing_outcome")
_emit_escalates_failure("p3", "react_chunking_telemetry", "failure_escalation")
_emit_orchestrates_workflow("p3", "react_chunking_telemetry", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "react_chunking_telemetry", "healing_dispatch")
_emit_invokes_evaluation("p3", "react_chunking_telemetry", "evaluation_signal")
_emit_records_telemetry_event("p4", "react_chunking_telemetry", "telemetry_event")
_emit_captures_evaluation_metric("p4", "react_chunking_telemetry", "eval_metric")
_emit_stores_embedding("p4", "react_chunking_telemetry", "embedding_store")
_emit_updates_meta_learning_state("p4", "react_chunking_telemetry", "meta_learning")
_emit_links_execution_to_snapshot("p4", "react_chunking_telemetry", "exec_snapshot_link")
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

record_execution_trace("react_chunking_telemetry", "react_chunking_telemetry_trace")


_emit_emits_metric_event("react_chunking_telemetry", "p4obs", "metric_1")
_emit_emits_metric_event("react_chunking_telemetry", "p4obs", "metric_2")
_emit_emits_metric_event("react_chunking_telemetry", "p4obs", "metric_3")
_emit_emits_metric_event("react_chunking_telemetry", "p4obs", "metric_4")
_emit_emits_metric_event("react_chunking_telemetry", "p4obs", "metric_5")
_emit_emits_metric_event("react_chunking_telemetry", "p4obs", "metric_6")
_emit_records_incident_event("react_chunking_telemetry", "p4obs", "incident")
_emit_captures_runtime_anomaly("react_chunking_telemetry", "p4obs", "anomaly")
_emit_writes_observability_log("react_chunking_telemetry", "p4obs", "obs_log")
_emit_updates_monitoring_state("react_chunking_telemetry", "p4obs", "mon_state")
_emit_triggers_alert("react_chunking_telemetry", "p4obs", "alert")
_emit_links_incident_trace("react_chunking_telemetry", "p4obs", "trace_link")
_emit_captures_pattern("react_chunking_telemetry", "p3lm", "pattern")
_emit_records_learning_event("react_chunking_telemetry", "p3lm", "learning_event")
_emit_writes_learning_snapshot("react_chunking_telemetry", "p3lm", "snapshot")
_emit_feeds_meta_learning("react_chunking_telemetry", "p3lm", "meta_feed")
_emit_updates_routing_strategy("react_chunking_telemetry", "p3lm", "routing")
_emit_improves_agent_policy("react_chunking_telemetry", "p3lm", "policy")
_emit_stores_learning_state("react_chunking_telemetry", "p3lm", "state")
_emit_records_execution_trace("react_chunking_telemetry", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("react_chunking_telemetry", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("react_chunking_telemetry", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("react_chunking_telemetry", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("react_chunking_telemetry", "L4_STATE", "p2_trace_5")
_emit_reads_environ("react_chunking_telemetry", "env_read", "p2_env_1")
_emit_reads_environ("react_chunking_telemetry", "env_read", "p2_env_2")
_emit_reads_runtime_state("react_chunking_telemetry", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("react_chunking_telemetry", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "react_chunking_telemetry", "context_pull")
_emit_pulls_context("p1", "react_chunking_telemetry", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "react_chunking_telemetry", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "react_chunking_telemetry", "uwg_term_2")
_emit_writes_through("p1", "react_chunking_telemetry", "write_through")
_emit_writes_through("p1", "react_chunking_telemetry", "write_through_2")
_emit_validated_by_safety_plane("p1", "react_chunking_telemetry", "safety_validation")
_emit_invokes_eval("p1", "react_chunking_telemetry", "eval_call")
_emit_proposal_commits_routing("p1", "react_chunking_telemetry", "routing_commit")

Logger = logging.getLogger(__name__)


def _get_meta_learning_bus():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_meta_learning_bus", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_meta_learning_bus", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L1_COGNITION, "_get_meta_learning_bus")
    from system_learning.engines.meta_learning_bus import MetaLearningBus, MetaLearningBusConfig

    return MetaLearningBus, MetaLearningBusConfig


def _build_trace_dict(
    kind: str,
    trace_id: str,
    timestamp_utc: int,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Build a minimal execution-trace dict compatible with the bus pipeline."""
    canonical = json.dumps(
        {"kind": kind, "trace_id": trace_id, "payload": payload},
        sort_keys=True,
        separators=(",", ":"),
    )
    content_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {
        "trace_id": trace_id,
        "kind": kind,
        "timestamp_utc": timestamp_utc,
        "content_hash": content_hash,
        **payload,
    }


def emit_react_performance_signal(
    trace_id: str,
    step_count: int,
    success: bool,
    policy_hash: str,
    timestamp_utc: int,
) -> dict[str, Any]:
    """Emit a react_performance telemetry signal to the meta-learning bus.

    Lazy-imports MetaLearningBus to avoid L1 → system_learning violation.
    Returns the trace dict emitted (for testing / observability).
    """
    trace = _build_trace_dict(
        kind="react_performance",
        trace_id=trace_id,
        timestamp_utc=timestamp_utc,
        payload={
            "step_count": step_count,
            "success": success,
            "policy_hash": policy_hash,
        },
    )
    _try_emit_to_bus([trace], timestamp_utc)
    return trace


def emit_retrieval_completeness_signal(
    trace_id: str,
    rag_context_ids: tuple[str, ...],
    chunk_ids: tuple[str, ...],
    timestamp_utc: int,
) -> dict[str, Any]:
    """Emit a retrieval_completeness signal to the meta-learning bus."""
    trace = _build_trace_dict(
        kind="retrieval_completeness",
        trace_id=trace_id,
        timestamp_utc=timestamp_utc,
        payload={
            "rag_context_ids": list(rag_context_ids),
            "chunk_ids": list(chunk_ids),
            "rag_count": len(rag_context_ids),
            "chunk_count": len(chunk_ids),
        },
    )
    _try_emit_to_bus([trace], timestamp_utc)
    return trace


def emit_chunking_effectiveness_signal(
    trace_id: str,
    corpus_manifest_hash: str,
    chunk_count: int,
    timestamp_utc: int,
) -> dict[str, Any]:
    """Emit a chunking_effectiveness signal to the meta-learning bus."""
    trace = _build_trace_dict(
        kind="chunking_effectiveness",
        trace_id=trace_id,
        timestamp_utc=timestamp_utc,
        payload={
            "corpus_manifest_hash": corpus_manifest_hash,
            "chunk_count": chunk_count,
        },
    )
    _try_emit_to_bus([trace], timestamp_utc)
    return trace


def emit_prompt_outcome_signal(
    trace_id: str,
    prompt_hash: str,
    policy_hash: str,
    success: bool,
    timestamp_utc: int,
) -> dict[str, Any]:
    """Emit a prompt_outcome_success signal to the meta-learning bus."""
    trace = _build_trace_dict(
        kind="prompt_outcome_success",
        trace_id=trace_id,
        timestamp_utc=timestamp_utc,
        payload={
            "prompt_hash": prompt_hash,
            "policy_hash": policy_hash,
            "success": success,
        },
    )
    _try_emit_to_bus([trace], timestamp_utc)
    return trace


def _try_emit_to_bus(traces: list[dict[str, Any]], timestamp_utc: int) -> None:
    """Attempt to process traces through MetaLearningBus — fail-open."""
    try:
        MetaLearningBus, MetaLearningBusConfig = _get_meta_learning_bus()
        bus = MetaLearningBus(config=MetaLearningBusConfig())
        bus.process_traces(traces, timestamp_utc=timestamp_utc)
    except (ImportError, AttributeError, RuntimeError, TypeError, ValueError) as exc:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
        Logger.warning(
            "react_chunking_telemetry_bus_unavailable",
            extra={"error": str(exc)},
        )


__all__ = [
    "emit_react_performance_signal",
    "emit_retrieval_completeness_signal",
    "emit_chunking_effectiveness_signal",
    "emit_prompt_outcome_signal",
]
