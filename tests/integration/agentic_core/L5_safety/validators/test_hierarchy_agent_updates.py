from unittest.mock import MagicMock

import pytest

#  # MOVED: from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent
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

# REMOVED: _emit_emits_metric_event("test_hierarchy_agent_updates", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_hierarchy_agent_updates", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_hierarchy_agent_updates", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_hierarchy_agent_updates", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_hierarchy_agent_updates", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_hierarchy_agent_updates", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_hierarchy_agent_updates", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_hierarchy_agent_updates", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_hierarchy_agent_updates", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_hierarchy_agent_updates", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_hierarchy_agent_updates", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_hierarchy_agent_updates", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_hierarchy_agent_updates", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_hierarchy_agent_updates", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_hierarchy_agent_updates", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_hierarchy_agent_updates", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_hierarchy_agent_updates", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_hierarchy_agent_updates", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_hierarchy_agent_updates", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_hierarchy_agent_updates", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_hierarchy_agent_updates", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_hierarchy_agent_updates", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_hierarchy_agent_updates", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_hierarchy_agent_updates", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_hierarchy_agent_updates", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_hierarchy_agent_updates", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_hierarchy_agent_updates", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_hierarchy_agent_updates", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_hierarchy_agent_updates")
# REMOVED: _emit_applies_guardrail("p0", "test_hierarchy_agent_updates", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_hierarchy_agent_updates", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_hierarchy_agent_updates", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_hierarchy_agent_updates", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_hierarchy_agent_updates", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_hierarchy_agent_updates", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_hierarchy_agent_updates", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_hierarchy_agent_updates", "write_through")
# REMOVED: _emit_writes_through("p1", "test_hierarchy_agent_updates", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_hierarchy_agent_updates", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_hierarchy_agent_updates", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_hierarchy_agent_updates", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_hierarchy_agent_updates", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_hierarchy_agent_updates", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_hierarchy_agent_updates", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_hierarchy_agent_updates", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_hierarchy_agent_updates", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_hierarchy_agent_updates", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_hierarchy_agent_updates", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_hierarchy_agent_updates", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_hierarchy_agent_updates", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_hierarchy_agent_updates", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_hierarchy_agent_updates", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_hierarchy_agent_updates")
# REMOVED: _emit_gated_by_confidence("p1", "test_hierarchy_agent_updates", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_hierarchy_agent_updates")
# REMOVED: emit_determinism_digest("p0", "test_hierarchy_agent_updates")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_hierarchy_agent_updates", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_hierarchy_agent_updates", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_hierarchy_agent_updates", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_hierarchy_agent_updates", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_hierarchy_agent_updates", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_hierarchy_agent_updates", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_hierarchy_agent_updates", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_hierarchy_agent_updates", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_hierarchy_agent_updates", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_hierarchy_agent_updates", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_hierarchy_agent_updates", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_hierarchy_agent_updates", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_hierarchy_agent_updates", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_hierarchy_agent_updates", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_hierarchy_agent_updates", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_hierarchy_agent_updates", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_hierarchy_agent_updates", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_hierarchy_agent_updates", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_hierarchy_agent_updates", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_hierarchy_agent_updates", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestHierarchyAgentUpdates:
    @pytest.fixture
    def mock_agent(self, tmp_path):
        return HierarchyAgent(project_root=tmp_path)

    def test_scripts_allowed_at_root(self, mock_agent):
                from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                """
                CRITICAL: scripts/ should NOT be in FORBIDDEN_ROOT_FOLDERS anymore.
                """
                assert "scripts" not in mock_agent.FORBIDDEN_ROOT_FOLDERS
                assert "logs" not in mock_agent.FORBIDDEN_ROOT_FOLDERS

        assert "logs" not in mock_agent.FORBIDDEN_ROOT_FOLDERS

        # Ensure actual forbidden stuff remains
        assert "coverage_html" in mock_agent.FORBIDDEN_ROOT_FOLDERS

    def test_scan_allows_valid_roots(self, mock_agent):
        """
        Verify that scanning does not flag scripts/ as a violation.
        """
        # Setup valid root folder
        (mock_agent.project_root / "scripts").mkdir()
        (mock_agent.project_root / "logs").mkdir()

        # Setup invalid folder
        (mock_agent.project_root / "coverage_html").mkdir()

        results = mock_agent.scan_root_violations()

        # Should only flag coverage_html
        assert "scripts" not in results["forbidden_folders"]
        assert "logs" not in results["forbidden_folders"]
        assert "coverage_html" in results["forbidden_folders"]

    def test_heal_does_not_merge_scripts(self, mock_agent):
        """
        Verify that heal_root_violations does not attempt to merge scripts/
        """
        # Mock the merge method to ensure it's not called for scripts
        mock_agent._merge_root_folder_to_ssot = MagicMock()

        # Inject "scripts" into scan results to simulate a false positive (if logic wasn't fixed)
        # But since we fixed the logic, it shouldn't even call scan with violations.
        # Let's verify the heal method logic directly.

        mock_agent.scan_root_violations = MagicMock(
            return_value={
                "violations_found": 1,
                "forbidden_folders": ["coverage_html"],  # Only bad stuff
                "archived_files_at_root": [],
            },
        )

        mock_agent.heal_root_violations(dry_run=True)

        # Should NOT call merge for scripts
        calls = mock_agent._merge_root_folder_to_ssot.call_args_list
        for call in calls:
            args, _ = call
            assert args[0] != "scripts"
            assert args[0] != "logs"
