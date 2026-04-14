"""
Shared determinism utility for apps_lic and apps_rg.

Provides canonical hashing and recursive nondeterminism stripping
bound to the canonical_bytes() function from the L0 spine.

All hashing delegates to:
    agentic_core.L0_routing.engines.assembly_stage.canonical_bytes

No local canonicalization is performed here.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from agentic_core.interfaces.determinism import canonical_bytes
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
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
    record_execution_trace,
)

record_execution_trace("determinism_util", "determinism_util_trace")


_emit_emits_metric_event("determinism_util", "p4obs", "metric_1")
_emit_emits_metric_event("determinism_util", "p4obs", "metric_2")
_emit_emits_metric_event("determinism_util", "p4obs", "metric_3")
_emit_emits_metric_event("determinism_util", "p4obs", "metric_4")
_emit_emits_metric_event("determinism_util", "p4obs", "metric_5")
_emit_emits_metric_event("determinism_util", "p4obs", "metric_6")
_emit_records_incident_event("determinism_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("determinism_util", "p4obs", "anomaly")
_emit_writes_observability_log("determinism_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("determinism_util", "p4obs", "mon_state")
_emit_triggers_alert("determinism_util", "p4obs", "alert")
_emit_links_incident_trace("determinism_util", "p4obs", "trace_link")
_emit_captures_pattern("determinism_util", "p3lm", "pattern")
_emit_records_learning_event("determinism_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("determinism_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("determinism_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("determinism_util", "p3lm", "routing")
_emit_improves_agent_policy("determinism_util", "p3lm", "policy")
_emit_stores_learning_state("determinism_util", "p3lm", "state")
_emit_records_execution_trace("determinism_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("determinism_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("determinism_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("determinism_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("determinism_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("determinism_util", "env_read", "p2_env_1")
_emit_reads_environ("determinism_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("determinism_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("determinism_util", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "determinism_util")
_emit_applies_guardrail("p0", "determinism_util", "p0_governance")
_emit_reads_policy_state("p0", "determinism_util", "policy_binding")
_emit_snapshots_state("p0", "determinism_util", "state_snapshot")
_emit_pulls_context("p1", "determinism_util", "context_pull")
_emit_pulls_context("p1", "determinism_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "determinism_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "determinism_util", "uwg_term_secondary")
_emit_writes_through("p1", "determinism_util", "write_through")
_emit_writes_through("p1", "determinism_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "determinism_util", "safety_validation")
_emit_invokes_eval("p1", "determinism_util", "eval_call")
_emit_proposal_commits_routing("p1", "determinism_util", "routing_commit")
_emit_escalates_to_human("p1", "determinism_util", "human_escalation")
_emit_routes_through("p1", "determinism_util", "route_through")
_emit_checks_agent_registry("p1", "determinism_util", "agent_registry")
_emit_validates_agent_capability("p1", "determinism_util", "capability")
_emit_dispatches_execution_plan("p1", "determinism_util", "exec_plan")
_emit_agent_executes_agent("p1", "determinism_util", "sub_agent")
_emit_routes_to_agent("p1", "determinism_util", "target_agent")
_emit_verifies_policy("p1", "determinism_util", "policy_check")
_emit_observes_runtime_state("p1", "determinism_util", "runtime_state")
_emit_verifies_boundary("p1", "determinism_util", "boundary_check")
_emit_transcripts_response("p1", "determinism_util", "transcript")
_emit_hard_fails_untranscripted("p1", "determinism_util")
_emit_gated_by_confidence("p1", "determinism_util", "confidence_gate")
emit_replay_key("p0", "determinism_util")
emit_determinism_digest("p0", "determinism_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "determinism_util", "execution_auth")
_emit_validates_capability("p2", "determinism_util", "capability_check")
_emit_routes_to_capability("p2", "determinism_util", "capability_route")
_emit_writes_via_uwg("p2", "determinism_util", "uwg_write")
_emit_blocks_direct_write("p2", "determinism_util", "direct_write_block")
_emit_records_tool_invocation("p2", "determinism_util", "tool_invocation")
_emit_captures_execution_output("p2", "determinism_util", "exec_output")
_emit_dispatches_agent("p3", "determinism_util", "agent_dispatch")
_emit_coordinates_agents("p3", "determinism_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "determinism_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "determinism_util", "healing_outcome")
_emit_escalates_failure("p3", "determinism_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "determinism_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "determinism_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "determinism_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "determinism_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "determinism_util", "eval_metric")
_emit_stores_embedding("p4", "determinism_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "determinism_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "determinism_util", "exec_snapshot_link")

DETERMINISM_EXCLUDED_FIELDS: frozenset[str] = frozenset(
    {"duration_ms", "timestamp", "trace_id", "cycle_counter", "telemetry", "created_at", "updated_at"},
)


def strip_nondeterministic(obj: Any) -> Any:
    """Recursively strip nondeterministic fields from obj.

    Rules:
    - dict: drop keys in DETERMINISM_EXCLUDED_FIELDS at any depth; recurse values.
    - list/tuple: recurse each element, preserve order and type.
    - anything else: return as-is.

    This function is recursion-safe and deterministic.
    It never introduces wall-clock time or randomness.
    """
    if isinstance(obj, dict):
        return {k: strip_nondeterministic(v) for k, v in obj.items() if k not in DETERMINISM_EXCLUDED_FIELDS}
    if isinstance(obj, tuple):
        return tuple(strip_nondeterministic(item) for item in obj)
    if isinstance(obj, list):
        return [strip_nondeterministic(item) for item in obj]
    return obj


def canonical_hash(obj: Any) -> str:
    """Return sha256 hexdigest of canonical_bytes(strip_nondeterministic(obj)).

    obj must be a dict (or list/tuple of dicts) serialisable by canonical_bytes.
    Excluded fields are stripped recursively before hashing.
    """
    stripped = strip_nondeterministic(obj)
    return hashlib.sha256(canonical_bytes(stripped)).hexdigest()


def file_hash(path: str | Path) -> str:
    """Return sha256 hexdigest of the raw bytes of the file at path."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
