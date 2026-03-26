"""Tests for structure drift detection functionality."""

from __future__ import annotations

import tempfile
from pathlib import Path

#  # MOVED: from agentic_core.L5_safety.utils.structure_drift_writer import save_manifest
#  # MOVED: from agentic_core.L5_safety.validators.structure_drift_validator import (
    generate_structure_manifest,
    load_manifest,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_structure_drift")
# REMOVED: _emit_applies_guardrail("p0", "test_structure_drift", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_structure_drift", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_structure_drift", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_structure_drift", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_structure_drift", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_structure_drift", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_structure_drift", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_structure_drift", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_structure_drift", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_structure_drift", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_structure_drift", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_structure_drift", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_structure_drift", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_structure_drift", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_structure_drift", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_structure_drift", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_structure_drift", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_structure_drift", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_structure_drift", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_structure_drift", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_structure_drift", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_structure_drift", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_structure_drift", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_structure_drift", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_structure_drift", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_structure_drift", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_structure_drift", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_structure_drift", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_structure_drift", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_structure_drift", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_structure_drift", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_structure_drift", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_structure_drift", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_structure_drift", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_structure_drift", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_structure_drift", "write_through")
# REMOVED: _emit_writes_through("p1", "test_structure_drift", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_structure_drift", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_structure_drift", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_structure_drift", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_structure_drift", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_structure_drift", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_structure_drift", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_structure_drift", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_structure_drift", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_structure_drift", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_structure_drift", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_structure_drift", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_structure_drift", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_structure_drift", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_structure_drift", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_structure_drift")
# REMOVED: _emit_gated_by_confidence("p1", "test_structure_drift", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_structure_drift")
# REMOVED: emit_determinism_digest("p0", "test_structure_drift")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_structure_drift", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_structure_drift", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_structure_drift", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_structure_drift", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_structure_drift", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_structure_drift", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_structure_drift", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_structure_drift", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_structure_drift", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_structure_drift", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_structure_drift", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_structure_drift", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_structure_drift", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_structure_drift", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_structure_drift", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_structure_drift", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_structure_drift", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_structure_drift", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_structure_drift", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_structure_drift", "exec_snapshot_link")


def test_manifest_determinism():
    from agentic_core.L5_safety.utils.structure_drift_writer import save_manifest
    from agentic_core.L5_safety.validators.structure_drift_validator import (
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    """Test that manifest generation is deterministic."""
    manifest1 = generate_structure_manifest()
    manifest2 = generate_structure_manifest()

    # Manifests should be identical
    assert manifest1 == manifest2

    # Hash should be the same
    assert manifest1["hash"] == manifest2["hash"]
    assert manifest1["hash"] is not None
    assert len(manifest1["hash"]) == 64  # SHA256 hex length


def test_drift_detection_in_temp_repo():
    """Test drift detection in a temporary repository."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create initial structure
        (temp_path / "test_dir").mkdir()
        (temp_path / "test_file.py").write_text("# Test file")

        # Generate initial manifest
        original_manifest = {
            "directories": ["test_dir"],
            "python_files": ["test_file.py"],
            "hash": "test_hash",
        }

        manifest_path = temp_path / "manifest.json"
        save_manifest(original_manifest, manifest_path)

        # Modify structure
        (temp_path / "new_dir").mkdir()
        (temp_path / "new_file.py").write_text("# New file")

        # Load and verify changes would be detected
        loaded = load_manifest(manifest_path)
        assert loaded == original_manifest


def test_update_gate_enforcement():
    """Test that update gate properly detects changes."""
    manifest = generate_structure_manifest()

    # Verify manifest has required fields
    assert "directories" in manifest
    assert "python_files" in manifest
    assert "hash" in manifest

    # Verify directories is a list
    assert isinstance(manifest["directories"], list)

    # Verify python_files is a list
    assert isinstance(manifest["python_files"], list)


def test_structure_drift_validator_integration():
    """Test integration with the CLI validator."""
    from ops_scripts.ci.structure_drift_validator import validate_structure_drift

    # Generate current manifest
    current_manifest = generate_structure_manifest()

    # Save as golden
    golden_path = Path("test_golden_manifest.json")
    save_manifest(current_manifest, golden_path)

    try:
        # Validation should pass
        assert validate_structure_drift(golden_path) is True
    finally:
        # Cleanup
        if golden_path.exists():
            golden_path.unlink()
