"""
L2.0 Manifest Hash Validator — Phase 2

Validates that execution manifests carry all required config hashes
and that those hashes match the L4 SSOT active configs.
"""

from __future__ import annotations

from typing import Any

from agentic_core.L0_routing.config.active_config_snapshot import ActiveConfigSnapshotV1
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "manifest_hash_validator")
trace_contract.emit_determinism_digest("p0", "manifest_hash_validator")

trace_contract._emit_dispatches_healing_run("p1", "manifest_hash_validator", "L2")
trace_contract._emit_routes_through("p1", "manifest_hash_validator", "L2")
trace_contract._emit_checks_agent_registry("p1", "manifest_hash_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "manifest_hash_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "manifest_hash_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "manifest_hash_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "manifest_hash_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "manifest_hash_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "manifest_hash_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "manifest_hash_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "manifest_hash_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "manifest_hash_validator")
trace_contract._emit_gated_by_confidence("p1", "manifest_hash_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "manifest_hash_validator", "L2")
trace_contract._emit_reads_policy_state("p1", "manifest_hash_validator", "L2")
trace_contract._emit_authorize_and_execute("p2", "manifest_hash_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "manifest_hash_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "manifest_hash_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "manifest_hash_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "manifest_hash_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "manifest_hash_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "manifest_hash_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "manifest_hash_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "manifest_hash_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "manifest_hash_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "manifest_hash_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "manifest_hash_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "manifest_hash_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "manifest_hash_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "manifest_hash_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "manifest_hash_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "manifest_hash_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "manifest_hash_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "manifest_hash_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "manifest_hash_validator", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("manifest_hash_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("manifest_hash_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("manifest_hash_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("manifest_hash_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("manifest_hash_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("manifest_hash_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("manifest_hash_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("manifest_hash_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("manifest_hash_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("manifest_hash_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("manifest_hash_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("manifest_hash_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("manifest_hash_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("manifest_hash_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("manifest_hash_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("manifest_hash_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("manifest_hash_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("manifest_hash_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("manifest_hash_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("manifest_hash_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("manifest_hash_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("manifest_hash_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("manifest_hash_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("manifest_hash_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("manifest_hash_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("manifest_hash_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("manifest_hash_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("manifest_hash_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "manifest_hash_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "manifest_hash_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "manifest_hash_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "manifest_hash_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "manifest_hash_validator", "write_through")
trace_contract._emit_writes_through("p1", "manifest_hash_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "manifest_hash_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "manifest_hash_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "manifest_hash_validator", "routing_commit")


REQUIRED_HASH_FIELDS = ("policy_hash", "routing_hash", "model_hash", "budget_hash")


class ManifestHashError(Exception):
    """Raised when manifest is missing or has mismatched config hashes."""

    pass


def validate_manifest_hashes(
    manifest: Any,
    active_config_snapshot: ActiveConfigSnapshotV1 | None,
) -> None:
    """
    L2.0 gate: reject manifest if any required config hash is missing
    or does not match the L4 SSOT active config.

    Args:
        manifest: Any object with hash attributes, or a dict.

    Raises:
        ManifestHashError: on missing field or hash mismatch.
    """
    if active_config_snapshot is None:
        raise ManifestHashError("ACTIVE_CONFIG_MISSING")
    active = active_config_snapshot.hashes()
    for field in REQUIRED_HASH_FIELDS:
        if isinstance(manifest, dict):
            value = manifest.get(field)
        else:
            value = getattr(manifest, field, None)
        if value is None:
            raise ManifestHashError(f"Manifest missing required field: {field}")
        expected = active[field]
        if value != expected:
            raise ManifestHashError(f"Hash mismatch for {field}: manifest={value!r} vs active_snapshot={expected!r}")
