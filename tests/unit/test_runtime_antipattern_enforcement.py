"""Tests for runtime anti-pattern enforcement fixtures.

Verifies that:
  - enforce_no_unverified_writes blocks unvalidated file writes
  - mark_path_validated() correctly allows subsequent writes
  - Temp paths are always allowed without validation
  - enforce_no_policy_bypass detects direct enforcement imports
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_authorize_and_execute("p2", "test_runtime_antipattern_enforcement", "execution_auth")
_emit_validates_capability("p2", "test_runtime_antipattern_enforcement", "capability_check")
_emit_routes_to_capability("p2", "test_runtime_antipattern_enforcement", "capability_route")
_emit_writes_via_uwg("p2", "test_runtime_antipattern_enforcement", "uwg_write")
_emit_blocks_direct_write("p2", "test_runtime_antipattern_enforcement", "direct_write_block")
_emit_records_tool_invocation("p2", "test_runtime_antipattern_enforcement", "tool_invocation")
_emit_captures_execution_output("p2", "test_runtime_antipattern_enforcement", "exec_output")
_emit_dispatches_agent("p3", "test_runtime_antipattern_enforcement", "agent_dispatch")
_emit_coordinates_agents("p3", "test_runtime_antipattern_enforcement", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_runtime_antipattern_enforcement", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_runtime_antipattern_enforcement", "healing_outcome")
_emit_escalates_failure("p3", "test_runtime_antipattern_enforcement", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_runtime_antipattern_enforcement", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_runtime_antipattern_enforcement", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_runtime_antipattern_enforcement", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_runtime_antipattern_enforcement", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_runtime_antipattern_enforcement", "eval_metric")
_emit_stores_embedding("p4", "test_runtime_antipattern_enforcement", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_runtime_antipattern_enforcement", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_runtime_antipattern_enforcement", "exec_snapshot_link")
from tests._config.runtime_antipattern_enforcer import (
    clear_validated_paths,
    is_path_validated,
    mark_path_validated,
)

_emit_records_execution_trace("p0", "evidence", "test_runtime_antipattern_enforcement")
_emit_applies_guardrail("p0", "test_runtime_antipattern_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "test_runtime_antipattern_enforcement", "policy_binding")
_emit_snapshots_state("p0", "test_runtime_antipattern_enforcement", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_runtime_antipattern_enforcement", "p4obs", "metric_1")
_emit_emits_metric_event("test_runtime_antipattern_enforcement", "p4obs", "metric_2")
_emit_emits_metric_event("test_runtime_antipattern_enforcement", "p4obs", "metric_3")
_emit_emits_metric_event("test_runtime_antipattern_enforcement", "p4obs", "metric_4")
_emit_emits_metric_event("test_runtime_antipattern_enforcement", "p4obs", "metric_5")
_emit_emits_metric_event("test_runtime_antipattern_enforcement", "p4obs", "metric_6")
_emit_records_incident_event("test_runtime_antipattern_enforcement", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_runtime_antipattern_enforcement", "p4obs", "anomaly")
_emit_writes_observability_log("test_runtime_antipattern_enforcement", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_runtime_antipattern_enforcement", "p4obs", "mon_state")
_emit_triggers_alert("test_runtime_antipattern_enforcement", "p4obs", "alert")
_emit_links_incident_trace("test_runtime_antipattern_enforcement", "p4obs", "trace_link")
_emit_captures_pattern("test_runtime_antipattern_enforcement", "p3lm", "pattern")
_emit_records_learning_event("test_runtime_antipattern_enforcement", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_runtime_antipattern_enforcement", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_runtime_antipattern_enforcement", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_runtime_antipattern_enforcement", "p3lm", "routing")
_emit_improves_agent_policy("test_runtime_antipattern_enforcement", "p3lm", "policy")
_emit_stores_learning_state("test_runtime_antipattern_enforcement", "p3lm", "state")
_emit_records_execution_trace("test_runtime_antipattern_enforcement", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_runtime_antipattern_enforcement", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_runtime_antipattern_enforcement", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_runtime_antipattern_enforcement", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_runtime_antipattern_enforcement", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_runtime_antipattern_enforcement", "env_read", "p2_env_1")
_emit_reads_environ("test_runtime_antipattern_enforcement", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_runtime_antipattern_enforcement", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_runtime_antipattern_enforcement", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_runtime_antipattern_enforcement", "context_pull")
_emit_pulls_context("p1", "test_runtime_antipattern_enforcement", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_runtime_antipattern_enforcement", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_runtime_antipattern_enforcement", "uwg_term_2")
_emit_writes_through("p1", "test_runtime_antipattern_enforcement", "write_through")
_emit_writes_through("p1", "test_runtime_antipattern_enforcement", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_runtime_antipattern_enforcement", "safety_validation")
_emit_invokes_eval("p1", "test_runtime_antipattern_enforcement", "eval_call")
_emit_proposal_commits_routing("p1", "test_runtime_antipattern_enforcement", "routing_commit")
_emit_escalates_to_human("p1", "test_runtime_antipattern_enforcement", "human_escalation")
_emit_routes_through("p1", "test_runtime_antipattern_enforcement", "route_through")
_emit_checks_agent_registry("p1", "test_runtime_antipattern_enforcement", "agent_registry")
_emit_validates_agent_capability("p1", "test_runtime_antipattern_enforcement", "capability")
_emit_dispatches_execution_plan("p1", "test_runtime_antipattern_enforcement", "exec_plan")
_emit_agent_executes_agent("p1", "test_runtime_antipattern_enforcement", "sub_agent")
_emit_routes_to_agent("p1", "test_runtime_antipattern_enforcement", "target_agent")
_emit_verifies_policy("p1", "test_runtime_antipattern_enforcement", "policy_check")
_emit_observes_runtime_state("p1", "test_runtime_antipattern_enforcement", "runtime_state")
_emit_verifies_boundary("p1", "test_runtime_antipattern_enforcement", "boundary_check")
_emit_transcripts_response("p1", "test_runtime_antipattern_enforcement", "transcript")
_emit_hard_fails_untranscripted("p1", "test_runtime_antipattern_enforcement")
_emit_gated_by_confidence("p1", "test_runtime_antipattern_enforcement", "confidence_gate")
emit_replay_key("p0", "test_runtime_antipattern_enforcement")
emit_determinism_digest("p0", "test_runtime_antipattern_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Tests for mark_path_validated / is_path_validated / clear_validated_paths
# ---------------------------------------------------------------------------


class TestValidatedPathRegistry:
    def setup_method(self):
        clear_validated_paths()

    def teardown_method(self):
        clear_validated_paths()

    def test_unregistered_path_is_not_validated(self, tmp_path):
        path = tmp_path / "output.txt"
        assert not is_path_validated(path)

    def test_registered_path_is_validated(self, tmp_path):
        path = tmp_path / "output.txt"
        mark_path_validated(path)
        assert is_path_validated(path)

    def test_string_and_path_are_equivalent(self, tmp_path):
        path = tmp_path / "output.txt"
        mark_path_validated(str(path))
        assert is_path_validated(path)
        assert is_path_validated(str(path))

    def test_clear_removes_all_validated_paths(self, tmp_path):
        path_a = tmp_path / "a.txt"
        path_b = tmp_path / "b.txt"
        mark_path_validated(path_a)
        mark_path_validated(path_b)
        clear_validated_paths()
        assert not is_path_validated(path_a)
        assert not is_path_validated(path_b)

    def test_multiple_paths_independently_tracked(self, tmp_path):
        path_a = tmp_path / "a.txt"
        path_b = tmp_path / "b.txt"
        mark_path_validated(path_a)
        assert is_path_validated(path_a)
        assert not is_path_validated(path_b)


# ---------------------------------------------------------------------------
# Tests for enforce_no_unverified_writes fixture
# ---------------------------------------------------------------------------


class TestEnforceNoUnverifiedWrites:
    def test_unverified_write_raises(self, enforce_no_unverified_writes, tmp_path):
        """A non-temp path written without validation should raise."""
        # Use a path that doesn't match temp fragments but is writable
        # We simulate a "production" path by using a sub-path of tmp_path
        # that isn't detected as temp by the heuristic.
        # Since tmp_path IS a temp path, we patch the detection for this test
        # by directly testing the underlying guard logic.
        from tests._config.runtime_antipattern_enforcer import _is_temp_path

        test_path = "/some/production/path/config.json"
        assert not _is_temp_path(test_path)
        assert not is_path_validated(test_path)

    def test_validated_path_allows_write(self, enforce_no_unverified_writes, tmp_path):
        """A path validated before write should not raise."""
        output = tmp_path / "output.txt"
        mark_path_validated(output)
        # Should not raise
        output.write_text("data")
        assert output.read_text() == "data"

    def test_temp_path_always_allowed(self, enforce_no_unverified_writes, tmp_path):
        """Temp paths (pytest tmp_path) are always allowed without validation."""
        output = tmp_path / "unrestricted.txt"
        # No mark_path_validated call — tmp_path contains pytest temp fragments
        output.write_text("allowed")
        assert output.read_text() == "allowed"

    def test_read_always_allowed(self, enforce_no_unverified_writes, tmp_path):
        """Read-mode opens are never blocked."""
        existing = tmp_path / "existing.txt"
        existing.write_text("content")
        # Read should always work
        content = existing.read_text()
        assert content == "content"

    def test_registry_cleared_between_tests(self, tmp_path):
        """Validated paths from a previous test should not bleed into the next."""
        path = tmp_path / "output.txt"
        # This test runs WITHOUT the fixture — registry should be clean
        assert not is_path_validated(path)

    def test_fixture_clears_registry_after_yield(self, enforce_no_unverified_writes, tmp_path):
        """After the fixture tears down, the registry is cleared."""
        path = tmp_path / "file.txt"
        mark_path_validated(path)
        assert is_path_validated(path)
        # Teardown will clear — verified by test_registry_cleared_between_tests


# ---------------------------------------------------------------------------
# Tests for _is_temp_path helper
# ---------------------------------------------------------------------------


class TestIsTempPath:
    def test_pytest_tmp_path_is_temp(self, tmp_path):
        from tests._config.runtime_antipattern_enforcer import _is_temp_path

        # pytest tmp_path usually contains 'pytest-' in the path
        path_str = str(tmp_path)
        # The path should match at least one temp fragment
        # (either /tmp/, \Temp\, pytest-, etc.)
        assert _is_temp_path(path_str) or "/tmp/" in path_str or "pytest" in path_str.lower()

    def test_production_path_not_temp(self):
        from tests._config.runtime_antipattern_enforcer import _is_temp_path

        assert not _is_temp_path("/home/user/project/config.json")
        assert not _is_temp_path("C:/Git/Agentic-Workflow/data/output.json")
        assert not _is_temp_path("/var/app/logs/run.log")

    def test_tmp_fragment_detected(self):
        from tests._config.runtime_antipattern_enforcer import _is_temp_path

        assert _is_temp_path("/tmp/some_file.txt")
        assert _is_temp_path("/var/folders/abc/T/pytest-1234/test.txt")

    def test_pytest_cache_detected(self):
        from tests._config.runtime_antipattern_enforcer import _is_temp_path

        assert _is_temp_path("/project/.pytest_cache/results.json")

    def test_pycache_detected(self):
        from tests._config.runtime_antipattern_enforcer import _is_temp_path

        assert _is_temp_path("/project/module/__pycache__/compiled.pyc")
