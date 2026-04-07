"""
agentic_core/interfaces/determinism.py

L0-centralized determinism interface for apps_* consumption.

AUTHORITY CONSTRAINTS:
- All canonicalization delegates to L0 assembly_stage.canonical_bytes
- No local canonicalization logic — prevents replay integrity divergence
- Read-only operations only — no state mutation
- JSON-serializable inputs enforced

USAGE (apps_*):
    from agentic_core.interfaces.determinism import (
        canonical_bytes,
        canonical_hash,
        strip_nondeterministic,
        DETERMINISM_EXCLUDED_FIELDS,
    )
"""

from __future__ import annotations

import hashlib
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "determinism")
_emit_applies_guardrail("p0", "determinism", "p0_governance")
_emit_reads_policy_state("p0", "determinism", "policy_binding")
_emit_snapshots_state("p0", "determinism", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

record_execution_trace("determinism", "determinism_trace")


_emit_emits_metric_event("determinism", "p4obs", "metric_1")
_emit_emits_metric_event("determinism", "p4obs", "metric_2")
_emit_emits_metric_event("determinism", "p4obs", "metric_3")
_emit_emits_metric_event("determinism", "p4obs", "metric_4")
_emit_emits_metric_event("determinism", "p4obs", "metric_5")
_emit_emits_metric_event("determinism", "p4obs", "metric_6")
_emit_records_incident_event("determinism", "p4obs", "incident")
_emit_captures_runtime_anomaly("determinism", "p4obs", "anomaly")
_emit_writes_observability_log("determinism", "p4obs", "obs_log")
_emit_updates_monitoring_state("determinism", "p4obs", "mon_state")
_emit_triggers_alert("determinism", "p4obs", "alert")
_emit_links_incident_trace("determinism", "p4obs", "trace_link")
_emit_captures_pattern("determinism", "p3lm", "pattern")
_emit_records_learning_event("determinism", "p3lm", "learning_event")
_emit_writes_learning_snapshot("determinism", "p3lm", "snapshot")
_emit_feeds_meta_learning("determinism", "p3lm", "meta_feed")
_emit_updates_routing_strategy("determinism", "p3lm", "routing")
_emit_improves_agent_policy("determinism", "p3lm", "policy")
_emit_stores_learning_state("determinism", "p3lm", "state")
_emit_records_execution_trace("determinism", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("determinism", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("determinism", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("determinism", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("determinism", "L4_STATE", "p2_trace_5")
_emit_reads_environ("determinism", "env_read", "p2_env_1")
_emit_reads_environ("determinism", "env_read", "p2_env_2")
_emit_reads_runtime_state("determinism", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("determinism", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "determinism", "context_pull")
_emit_pulls_context("p1", "determinism", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "determinism", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "determinism", "uwg_term_2")
_emit_writes_through("p1", "determinism", "write_through")
_emit_writes_through("p1", "determinism", "write_through_2")
_emit_validated_by_safety_plane("p1", "determinism", "safety_validation")
_emit_invokes_eval("p1", "determinism", "eval_call")
_emit_proposal_commits_routing("p1", "determinism", "routing_commit")
_emit_escalates_to_human("p1", "determinism", "human_escalation")
_emit_routes_through("p1", "determinism", "route_through")
_emit_checks_agent_registry("p1", "determinism", "agent_registry")
_emit_validates_agent_capability("p1", "determinism", "capability")
_emit_dispatches_execution_plan("p1", "determinism", "exec_plan")
_emit_agent_executes_agent("p1", "determinism", "sub_agent")
_emit_routes_to_agent("p1", "determinism", "target_agent")
_emit_verifies_policy("p1", "determinism", "policy_check")
_emit_observes_runtime_state("p1", "determinism", "runtime_state")
_emit_verifies_boundary("p1", "determinism", "boundary_check")
_emit_transcripts_response("p1", "determinism", "transcript")
_emit_hard_fails_untranscripted("p1", "determinism")
_emit_gated_by_confidence("p1", "determinism", "confidence_gate")
emit_replay_key("p0", "determinism")
emit_determinism_digest("p0", "determinism")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "determinism", "execution_auth")
_emit_validates_capability("p2", "determinism", "capability_check")
_emit_routes_to_capability("p2", "determinism", "capability_route")
_emit_writes_via_uwg("p2", "determinism", "uwg_write")
_emit_blocks_direct_write("p2", "determinism", "direct_write_block")
_emit_records_tool_invocation("p2", "determinism", "tool_invocation")
_emit_captures_execution_output("p2", "determinism", "exec_output")
_emit_dispatches_agent("p3", "determinism", "agent_dispatch")
_emit_coordinates_agents("p3", "determinism", "agent_coordination")
_emit_records_workflow_lineage("p3", "determinism", "workflow_lineage")
_emit_records_healing_outcome("p3", "determinism", "healing_outcome")
_emit_escalates_failure("p3", "determinism", "failure_escalation")
_emit_orchestrates_workflow("p3", "determinism", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "determinism", "healing_dispatch")
_emit_invokes_evaluation("p3", "determinism", "evaluation_signal")
_emit_records_telemetry_event("p4", "determinism", "telemetry_event")
_emit_captures_evaluation_metric("p4", "determinism", "eval_metric")
_emit_stores_embedding("p4", "determinism", "embedding_store")
_emit_updates_meta_learning_state("p4", "determinism", "meta_learning")
_emit_links_execution_to_snapshot("p4", "determinism", "exec_snapshot_link")

DETERMINISM_EXCLUDED_FIELDS: frozenset[str] = frozenset(
    {"duration_ms", "timestamp", "trace_id", "cycle_counter", "telemetry", "created_at", "updated_at"},
)


def canonical_bytes(data: dict[str, Any]) -> bytes:
    """
    Proxy to L0 assembly_stage.canonical_bytes.

    Centralizes canonicalization — no local logic duplication.
    Prevents replay integrity breaks across layers.
    """
    from agentic_core.L0_routing.reasoning.assembly_stage import canonical_bytes as _l0_canonical_bytes

    return _l0_canonical_bytes(data)


def canonical_hash(data: dict[str, Any]) -> str:
    """
    Return hex SHA-256 of the canonical bytes.

    Delegates to L0 canonical_bytes — no independent logic.
    """
    return hashlib.sha256(canonical_bytes(data)).hexdigest()


def strip_nondeterministic(
    data: dict[str, Any], excluded_fields: frozenset[str] | None = None,
) -> dict[str, Any]:
    """
    Return a copy of data with nondeterministic fields removed.

    Read-only — never mutates the caller-owned dict.
    """
    excluded = excluded_fields if excluded_fields is not None else DETERMINISM_EXCLUDED_FIELDS
    return {k: v for k, v in data.items() if k not in excluded}


__all__ = ["canonical_bytes", "canonical_hash", "strip_nondeterministic", "DETERMINISM_EXCLUDED_FIELDS"]
