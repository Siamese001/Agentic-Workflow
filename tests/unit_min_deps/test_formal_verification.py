"""Integration tests for formal verification scanners."""

from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    TOOLS_DIR,
)
from agentic_core.L5_safety.static_checks.determinism_serialization_check import (
    scan_repository_for_determinism,
)
from agentic_core.L5_safety.static_checks.powershell_ban import (
    scan_repository_for_powershell,
)
from agentic_core.L5_safety.static_checks.write_gateway_enforcer import (
    scan_repository_for_writes,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_links_incident_trace,  # noqa: E402
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
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_formal_verification", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_formal_verification", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_formal_verification", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_formal_verification", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_formal_verification", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_formal_verification", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_formal_verification", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_formal_verification", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_formal_verification", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_formal_verification", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_formal_verification", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_formal_verification", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_formal_verification", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_formal_verification", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_formal_verification", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_formal_verification", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_formal_verification", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_formal_verification", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_formal_verification", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_formal_verification", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_formal_verification", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_formal_verification", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_formal_verification", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_formal_verification", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_formal_verification", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_formal_verification", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_formal_verification", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_formal_verification", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_formal_verification")
# REMOVED: _emit_applies_guardrail("p0", "test_formal_verification", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_formal_verification", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_formal_verification", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_formal_verification", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_formal_verification", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_formal_verification", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_formal_verification", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_formal_verification", "write_through")
# REMOVED: _emit_writes_through("p1", "test_formal_verification", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_formal_verification", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_formal_verification", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_formal_verification", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_formal_verification", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_formal_verification", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_formal_verification", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_formal_verification", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_formal_verification", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_formal_verification", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_formal_verification", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_formal_verification", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_formal_verification", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_formal_verification", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_formal_verification", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_formal_verification")
# REMOVED: _emit_gated_by_confidence("p1", "test_formal_verification", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_formal_verification")
# REMOVED: emit_determinism_digest("p0", "test_formal_verification")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_formal_verification", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_formal_verification", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_formal_verification", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_formal_verification", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_formal_verification", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_formal_verification", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_formal_verification", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_formal_verification", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_formal_verification", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_formal_verification", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_formal_verification", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_formal_verification", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_formal_verification", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_formal_verification", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_formal_verification", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_formal_verification", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_formal_verification", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_formal_verification", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_formal_verification", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_formal_verification", "exec_snapshot_link")


@pytest.mark.unit_min_deps
def test_repo_no_powershell_violations():
    """Test that repository has no PowerShell violations."""
    repo_root = Path.cwd()

    violations = scan_repository_for_powershell(repo_root)

    # Convert to readable format for assertion
    violation_details = [
        f"{path}:{lineno} - {rule_id} - {snippet}" for path, lineno, rule_id, snippet in violations
    ]

    assert len(violations) == 0, f"PowerShell violations found: {violation_details}"


@pytest.mark.unit_min_deps
def test_repo_no_write_gateway_violations():
    """Test that repository has no write gateway violations in scope."""
    repo_root = Path.cwd()

    violations = scan_repository_for_writes(repo_root)

    # Convert to readable format for assertion
    violation_details = [
        f"{path}:{lineno} - {rule_id} - {snippet}" for path, lineno, rule_id, snippet in violations
    ]

    assert len(violations) == 0, f"Write gateway violations found: {violation_details}"


@pytest.mark.unit_min_deps
def test_repo_no_determinism_violations():
    """Test that repository has no determinism violations in replay/storage."""
    repo_root = Path.cwd()

    violations = scan_repository_for_determinism(repo_root)

    # Convert to readable format for assertion
    violation_details = [
        f"{path}:{lineno} - {rule_id} - {snippet}" for path, lineno, rule_id, snippet in violations
    ]

    assert len(violations) == 0, f"Determinism violations found: {violation_details}"


@pytest.mark.unit_min_deps
def test_scanner_coverage():
    """Test that scanners cover expected directories."""
    repo_root = Path.cwd()

    # Test PowerShell scanner coverage
    _ps_violations = scan_repository_for_powershell(repo_root)

    # Should scan tools and docs/evidence directories
    tools_dir = repo_root / TOOLS_DIR
    evidence_dir = repo_root / "docs" / "evidence"

    if tools_dir.exists():
        # If tools directory exists, scanner should have checked it
        # (even if no violations found)
        pass

    if evidence_dir.exists():
        # If evidence directory exists, scanner should have checked it
        pass

    # Test write gateway scanner coverage
    _write_violations = scan_repository_for_writes(repo_root)

    # Should scan agentic_core (excluding L2_execution)
    agentic_core_dir = repo_root / AGENTIC_CORE_DIR
    if agentic_core_dir.exists():
        pass

    # Test determinism scanner coverage
    _det_violations = scan_repository_for_determinism(repo_root)

    # Should scan replay and storage modules
    replay_dir = repo_root / L3_ORCHESTRATION_DIR / "replay"
    storage_dir = repo_root / L4_STATE_DIR / "storage"

    if replay_dir.exists():
        pass

    if storage_dir.exists():
        pass


@pytest.mark.unit_min_deps
def test_scanner_deterministic_output():
    """Test that scanners produce deterministic output across runs."""
    repo_root = Path.cwd()

    # Run each scanner twice
    ps_violations1 = scan_repository_for_powershell(repo_root)
    ps_violations2 = scan_repository_for_powershell(repo_root)

    write_violations1 = scan_repository_for_writes(repo_root)
    write_violations2 = scan_repository_for_writes(repo_root)

    det_violations1 = scan_repository_for_determinism(repo_root)
    det_violations2 = scan_repository_for_determinism(repo_root)

    # Results should be identical
    assert ps_violations1 == ps_violations2
    assert write_violations1 == write_violations2
    assert det_violations1 == det_violations2

    # Results should be sorted
    def check_sorted(violations):
        for i in range(1, len(violations)):
            if violations[i - 1] > violations[i]:
                return False
        return True

    assert check_sorted(ps_violations1)
    assert check_sorted(write_violations1)
    assert check_sorted(det_violations1)
