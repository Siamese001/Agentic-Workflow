"""
File: tests/L0/test_root_hygiene.py
Rationale:
    Verifies that the RootHygieneEnforcer correctly cleans the environment.
"""

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L0_ROUTING_DIR,
    OPS_SCRIPTS_DIR,
)
#  # MOVED: from agentic_core.L0_routing.scripts.root_hygiene_util import enforce_root_hygiene
#  # MOVED: from agentic_core.L5_safety.config.structure_blueprint.ssot import REPORTS_DIR
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_root_hygiene", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_root_hygiene", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_root_hygiene", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_root_hygiene", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_root_hygiene", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_root_hygiene", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_root_hygiene", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_root_hygiene", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_root_hygiene", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_root_hygiene", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_root_hygiene", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_root_hygiene", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_root_hygiene", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_root_hygiene", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_root_hygiene", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_root_hygiene", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_root_hygiene", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_root_hygiene", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_root_hygiene", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_root_hygiene", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_root_hygiene", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_root_hygiene", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_root_hygiene", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_root_hygiene", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_root_hygiene", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_root_hygiene", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_root_hygiene", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_root_hygiene", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_root_hygiene")
# REMOVED: _emit_applies_guardrail("p0", "test_root_hygiene", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_root_hygiene", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_root_hygiene", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_root_hygiene", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_root_hygiene", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_root_hygiene", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_root_hygiene", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_root_hygiene", "write_through")
# REMOVED: _emit_writes_through("p1", "test_root_hygiene", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_root_hygiene", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_root_hygiene", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_root_hygiene", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_root_hygiene", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_root_hygiene", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_root_hygiene", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_root_hygiene", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_root_hygiene", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_root_hygiene", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_root_hygiene", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_root_hygiene", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_root_hygiene", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_root_hygiene", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_root_hygiene", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_root_hygiene")
# REMOVED: _emit_gated_by_confidence("p1", "test_root_hygiene", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_root_hygiene")
# REMOVED: emit_determinism_digest("p0", "test_root_hygiene")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_root_hygiene", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_root_hygiene", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_root_hygiene", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_root_hygiene", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_root_hygiene", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_root_hygiene", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_root_hygiene", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_root_hygiene", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_root_hygiene", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_root_hygiene", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_root_hygiene", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_root_hygiene", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_root_hygiene", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_root_hygiene", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_root_hygiene", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_root_hygiene", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_root_hygiene", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_root_hygiene", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_root_hygiene", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_root_hygiene", "exec_snapshot_link")


@pytest.fixture
def dirty_repo(tmp_path):
    """Creates a dirty mock repo with illegal root folders."""
    # Setup Markers
    (tmp_path / AGENTIC_CORE_DIR).mkdir()
    (tmp_path / "pyproject.toml").touch()

    # Create Illegal Root Scripts
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "standalone_tool.py").write_text("print('hello')")
    (scripts / "core_tool.py").write_text("import agentic_core\nprint('core')")

    # Create Illegal Coverage
    cov = tmp_path / "coverage_html"
    cov.mkdir()
    (cov / "index.html").touch()

    return tmp_path


def test_hygiene_enforcement(dirty_repo, monkeypatch):
        from agentic_core.L0_routing.config.path_constants import (
        from agentic_core.L0_routing.scripts.root_hygiene_util import enforce_root_hygiene
        from agentic_core.L5_safety.config.structure_blueprint.ssot import REPORTS_DIR
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        """Test that scripts are moved to correct locations and root is cleaned."""
        monkeypatch.chdir(dirty_repo)
        monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")

    monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")

    # Run Enforcer
    enforce_root_hygiene()

    # Assertions
    # 1. Illegal dirs gone
    assert not (dirty_repo / "scripts").exists()
    assert not (dirty_repo / "coverage_html").exists()

    # 2. Standalone script -> ops_scripts
    assert (dirty_repo / OPS_SCRIPTS_DIR / "standalone_tool.py").exists()

    # 3. Core script -> agentic_core/L0_routing/scripts
    assert (dirty_repo / L0_ROUTING_DIR / "scripts" / "core_tool.py").exists()

    # 4. Coverage -> reports
    assert (dirty_repo / REPORTS_DIR / "coverage_html" / "index.html").exists()


def test_purge_cache_refiling(dirty_repo, monkeypatch):
    """Test the specific rule for purge_cache.py reorganization."""
    monkeypatch.chdir(dirty_repo)
    monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")

    # Setup purge_cache in illegal scripts folder
    (dirty_repo / "scripts" / "purge_cache.py").write_text("print('clean')")

    enforce_root_hygiene()

    # Should end up nested in maintenance
    assert (dirty_repo / OPS_SCRIPTS_DIR / "maintenance" / "purge_cache.py").exists()
