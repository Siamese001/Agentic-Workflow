import pytest

from agentic_core.L5_safety.reasoning.HygieneGuardianAgent import HygieneGuardianAgent
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

# REMOVED: _emit_emits_metric_event("test_hygiene_guardian_enhanced", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_hygiene_guardian_enhanced", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_hygiene_guardian_enhanced", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_hygiene_guardian_enhanced", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_hygiene_guardian_enhanced", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_hygiene_guardian_enhanced", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_hygiene_guardian_enhanced", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_hygiene_guardian_enhanced", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_hygiene_guardian_enhanced", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_hygiene_guardian_enhanced", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_hygiene_guardian_enhanced", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_hygiene_guardian_enhanced", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_hygiene_guardian_enhanced", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_hygiene_guardian_enhanced", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_hygiene_guardian_enhanced", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_hygiene_guardian_enhanced", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_hygiene_guardian_enhanced", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_hygiene_guardian_enhanced", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_hygiene_guardian_enhanced", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_hygiene_guardian_enhanced", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_hygiene_guardian_enhanced", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_hygiene_guardian_enhanced", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_hygiene_guardian_enhanced", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_hygiene_guardian_enhanced", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_hygiene_guardian_enhanced", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_hygiene_guardian_enhanced", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_hygiene_guardian_enhanced", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_hygiene_guardian_enhanced", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_hygiene_guardian_enhanced")
# REMOVED: _emit_applies_guardrail("p0", "test_hygiene_guardian_enhanced", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_hygiene_guardian_enhanced", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_hygiene_guardian_enhanced", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_hygiene_guardian_enhanced", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_hygiene_guardian_enhanced", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_hygiene_guardian_enhanced", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_hygiene_guardian_enhanced", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_hygiene_guardian_enhanced", "write_through")
# REMOVED: _emit_writes_through("p1", "test_hygiene_guardian_enhanced", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_hygiene_guardian_enhanced", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_hygiene_guardian_enhanced", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_hygiene_guardian_enhanced", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_hygiene_guardian_enhanced", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_hygiene_guardian_enhanced", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_hygiene_guardian_enhanced", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_hygiene_guardian_enhanced", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_hygiene_guardian_enhanced", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_hygiene_guardian_enhanced", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_hygiene_guardian_enhanced", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_hygiene_guardian_enhanced", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_hygiene_guardian_enhanced", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_hygiene_guardian_enhanced", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_hygiene_guardian_enhanced", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_hygiene_guardian_enhanced")
# REMOVED: _emit_gated_by_confidence("p1", "test_hygiene_guardian_enhanced", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_hygiene_guardian_enhanced")
# REMOVED: emit_determinism_digest("p0", "test_hygiene_guardian_enhanced")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_hygiene_guardian_enhanced", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_hygiene_guardian_enhanced", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_hygiene_guardian_enhanced", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_hygiene_guardian_enhanced", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_hygiene_guardian_enhanced", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_hygiene_guardian_enhanced", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_hygiene_guardian_enhanced", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_hygiene_guardian_enhanced", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_hygiene_guardian_enhanced", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_hygiene_guardian_enhanced", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_hygiene_guardian_enhanced", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_hygiene_guardian_enhanced", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_hygiene_guardian_enhanced", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_hygiene_guardian_enhanced", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_hygiene_guardian_enhanced", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_hygiene_guardian_enhanced", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_hygiene_guardian_enhanced", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_hygiene_guardian_enhanced", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_hygiene_guardian_enhanced", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_hygiene_guardian_enhanced", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# MANDATORY: 100% TEST PASS REQUIRED


@pytest.fixture
def disable_path_shield():
    return True


class TestHygieneGuardianNamingEnhanced:
    def setup_method(self):
        self.tmp_path = None

    def test_camel_case_splitting(self, tmp_path, disable_path_shield):
        """
        Ensures CamelCase files are counted correctly.
        'MyVeryLongFileNameDetector.py' should be 6 words, not 1.
        """
        guardian = HygieneGuardianAgent(project_root=tmp_path)

        # "My", "Very", "Long", "File", "Name", "Detector" = 6 words
        filename = "MyVeryLongFileNameDetector.py"
        test_file = tmp_path / filename
        test_file.write_text("# Test", encoding="utf-8")

        guardian._check_filename_length(test_file)

        assert len(guardian.naming_violations) == 1, "Failed to detect violation in CamelCase file"
        assert guardian.naming_violations[0]["current_count"] == 6
        print("✅ PASS: CamelCase Splitting")

    def test_mixed_delimiters(self, tmp_path, disable_path_shield):
        """
        Ensures mixed delimiters (hyphens and underscores) are handled.
        """
        guardian = HygieneGuardianAgent(project_root=tmp_path)

        # "scripts", "deploy", "cluster", "east", "us", "region" = 6 words
        filename = "scripts-deploy_cluster-east_us_region.py"
        test_file = tmp_path / filename
        test_file.write_text("# Test", encoding="utf-8")

        guardian._check_filename_length(test_file)

        assert len(guardian.naming_violations) == 1, "Failed to detect violation in mixed delimiter file"
        assert guardian.naming_violations[0]["current_count"] == 6
        print("✅ PASS: Mixed Delimiters")

    def test_test_file_leniency(self, tmp_path, disable_path_shield):
        """
        Ensures test files have a higher word limit (8) than standard files (5).
        """
        guardian = HygieneGuardianAgent(project_root=tmp_path)

        # 7 words: "test", "user", "login", "fails", "with", "invalid", "password"
        # Standard limit (5) would fail, Test limit (8) should pass.
        filename = "test_user_login_fails_with_invalid_password.py"
        test_file = tmp_path / filename
        test_file.write_text("# Test", encoding="utf-8")

        guardian._check_filename_length(test_file)
        assert len(guardian.naming_violations) == 0, (
            "Test file flagged incorrectly. Should allow 7 words with limit 8"
        )

        # 10 words: should fail (exceeds limit of 8)
        long_filename = "test_user_login_fails_with_invalid_password_and_username_retry.py"
        long_file = tmp_path / long_filename
        long_file.write_text("# Test", encoding="utf-8")

        guardian._check_filename_length(long_file)
        assert len(guardian.naming_violations) == 1
        assert guardian.naming_violations[0]["current_count"] == 10
        print("✅ PASS: Test File Leniency")

    def test_smart_suggestion_preservation(self, tmp_path, disable_path_shield):
        """
        Verifies that the suggestion engine removes stop words before truncation.
        """
        guardian = HygieneGuardianAgent(project_root=tmp_path)

        # 6 words: "payment", "gateway", "service", "implementation", "stripe", "connector"
        # "service" and "implementation" are in REDUNDANT_TERMS
        words = ["payment", "gateway", "service", "implementation", "stripe", "connector"]
        suggestion = guardian._generate_concise_suggestion(words, ".py")

        assert "service" not in suggestion
        assert "implementation" not in suggestion
        assert suggestion == "payment_gateway_stripe_connector.py"
        print("✅ PASS: Smart Suggestion Logic")

    def test_standard_file_strict_limit(self, tmp_path, disable_path_shield):
        """
        Verifies that non-test files are held to the 5-word limit.
        """
        guardian = HygieneGuardianAgent(project_root=tmp_path)

        # 6 words: should fail for standard files
        filename = "user_authentication_service_manager_handler_utils.py"
        test_file = tmp_path / filename
        test_file.write_text("# Test", encoding="utf-8")

        guardian._check_filename_length(test_file)

        assert len(guardian.naming_violations) == 1
        assert guardian.naming_violations[0]["current_count"] == 6
        assert guardian.naming_violations[0]["limit"] == 5
        print("✅ PASS: Standard File Strict Limit")

    def test_redundant_term_removal(self, tmp_path, disable_path_shield):
        """
        Verifies that redundant terms are removed from suggestions.
        """
        guardian = HygieneGuardianAgent(project_root=tmp_path)

        # Test with multiple redundant terms
        words = ["data", "management", "service", "implementation", "utility", "handler"]
        # Should remove: management, service, implementation, utility
        # Remaining: data, handler (2 words)
        suggestion = guardian._generate_concise_suggestion(words, ".py")

        assert "management" not in suggestion
        assert "service" not in suggestion
        assert "implementation" not in suggestion
        assert "utility" not in suggestion
        assert suggestion == "data_handler.py"
        print("✅ PASS: Redundant Term Removal")


# MANDATORY: 100% TEST PASS REQUIRED
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
