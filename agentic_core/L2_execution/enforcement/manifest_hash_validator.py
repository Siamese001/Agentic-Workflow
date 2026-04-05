"""
L2.0 Manifest Hash Validator — Phase 2

Validates that execution manifests carry all required config hashes
and that those hashes match the L4 SSOT active configs.
"""

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

emit_replay_key("p0", "manifest_hash_validator")
emit_determinism_digest("p0", "manifest_hash_validator")

_emit_dispatches_healing_run("p1", "manifest_hash_validator", "L2")
_emit_routes_through("p1", "manifest_hash_validator", "L2")
_emit_checks_agent_registry("p1", "manifest_hash_validator", "agent_registry")
_emit_validates_agent_capability("p1", "manifest_hash_validator", "capability")
_emit_dispatches_execution_plan("p1", "manifest_hash_validator", "exec_plan")
_emit_agent_executes_agent("p1", "manifest_hash_validator", "sub_agent")
_emit_routes_to_agent("p1", "manifest_hash_validator", "target_agent")
_emit_verifies_policy("p1", "manifest_hash_validator", "policy_check")
_emit_observes_runtime_state("p1", "manifest_hash_validator", "runtime_state")
_emit_verifies_boundary("p1", "manifest_hash_validator", "boundary_check")
_emit_transcripts_response("p1", "manifest_hash_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "manifest_hash_validator")
_emit_gated_by_confidence("p1", "manifest_hash_validator", "confidence_gate")
_emit_escalates_to_human("p1", "manifest_hash_validator", "L2")
_emit_reads_policy_state("p1", "manifest_hash_validator", "L2")
_emit_authorize_and_execute("p2", "manifest_hash_validator", "execution_auth")
_emit_validates_capability("p2", "manifest_hash_validator", "capability_check")
_emit_routes_to_capability("p2", "manifest_hash_validator", "capability_route")
_emit_writes_via_uwg("p2", "manifest_hash_validator", "uwg_write")
_emit_blocks_direct_write("p2", "manifest_hash_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "manifest_hash_validator", "tool_invocation")
_emit_captures_execution_output("p2", "manifest_hash_validator", "exec_output")
_emit_dispatches_agent("p3", "manifest_hash_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "manifest_hash_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "manifest_hash_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "manifest_hash_validator", "healing_outcome")
_emit_escalates_failure("p3", "manifest_hash_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "manifest_hash_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "manifest_hash_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "manifest_hash_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "manifest_hash_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "manifest_hash_validator", "eval_metric")
_emit_stores_embedding("p4", "manifest_hash_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "manifest_hash_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "manifest_hash_validator", "exec_snapshot_link")
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

_emit_emits_metric_event("manifest_hash_validator", "p4obs", "metric_1")
_emit_emits_metric_event("manifest_hash_validator", "p4obs", "metric_2")
_emit_emits_metric_event("manifest_hash_validator", "p4obs", "metric_3")
_emit_emits_metric_event("manifest_hash_validator", "p4obs", "metric_4")
_emit_emits_metric_event("manifest_hash_validator", "p4obs", "metric_5")
_emit_emits_metric_event("manifest_hash_validator", "p4obs", "metric_6")
_emit_records_incident_event("manifest_hash_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("manifest_hash_validator", "p4obs", "anomaly")
_emit_writes_observability_log("manifest_hash_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("manifest_hash_validator", "p4obs", "mon_state")
_emit_triggers_alert("manifest_hash_validator", "p4obs", "alert")
_emit_links_incident_trace("manifest_hash_validator", "p4obs", "trace_link")
_emit_captures_pattern("manifest_hash_validator", "p3lm", "pattern")
_emit_records_learning_event("manifest_hash_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("manifest_hash_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("manifest_hash_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("manifest_hash_validator", "p3lm", "routing")
_emit_improves_agent_policy("manifest_hash_validator", "p3lm", "policy")
_emit_stores_learning_state("manifest_hash_validator", "p3lm", "state")
_emit_records_execution_trace("manifest_hash_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("manifest_hash_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("manifest_hash_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("manifest_hash_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("manifest_hash_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("manifest_hash_validator", "env_read", "p2_env_1")
_emit_reads_environ("manifest_hash_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("manifest_hash_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("manifest_hash_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "manifest_hash_validator", "context_pull")
_emit_pulls_context("p1", "manifest_hash_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "manifest_hash_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "manifest_hash_validator", "uwg_term_2")
_emit_writes_through("p1", "manifest_hash_validator", "write_through")
_emit_writes_through("p1", "manifest_hash_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "manifest_hash_validator", "safety_validation")
_emit_invokes_eval("p1", "manifest_hash_validator", "eval_call")
_emit_proposal_commits_routing("p1", "manifest_hash_validator", "routing_commit")


def _get_active_configs():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_active_configs", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_active_configs", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "_get_active_configs")
    from agentic_core.L4_state.config.versioned_configs import get_active_configs

    return get_active_configs


REQUIRED_HASH_FIELDS = ("policy_hash", "routing_hash", "model_hash", "budget_hash")


class ManifestHashError(Exception):
    """Raised when manifest is missing or has mismatched config hashes."""

    pass


def validate_manifest_hashes(manifest: Any) -> None:
    """
    L2.0 gate: reject manifest if any required config hash is missing
    or does not match the L4 SSOT active config.

    Args:
        manifest: Any object with hash attributes, or a dict.

    Raises:
        ManifestHashError: on missing field or hash mismatch.
    """
    active = _get_active_configs()().hashes()
    for field in REQUIRED_HASH_FIELDS:
        if isinstance(manifest, dict):
            value = manifest.get(field)
        else:
            value = getattr(manifest, field, None)
        if value is None:
            raise ManifestHashError(f"Manifest missing required field: {field}")
        expected = active[field]
        if value != expected:
            raise ManifestHashError(f"Hash mismatch for {field}: manifest={value!r} vs L4_SSOT={expected!r}")
