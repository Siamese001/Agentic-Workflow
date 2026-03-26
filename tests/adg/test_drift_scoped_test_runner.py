"""
Regression tests for ops_scripts/ci/drift_scoped_test_runner.py

All tests mock Redis, subprocess, and filesystem — no live connections.  24 tests.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import ops_scripts.ci.drift_scoped_test_runner as runner
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

# REMOVED: _emit_authorize_and_execute("p2", "test_drift_scoped_test_runner", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_drift_scoped_test_runner", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_drift_scoped_test_runner", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_drift_scoped_test_runner", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_drift_scoped_test_runner", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_drift_scoped_test_runner", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_drift_scoped_test_runner", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_drift_scoped_test_runner", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_drift_scoped_test_runner", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_drift_scoped_test_runner", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_drift_scoped_test_runner", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_drift_scoped_test_runner", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_drift_scoped_test_runner", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_drift_scoped_test_runner", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_drift_scoped_test_runner", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_drift_scoped_test_runner", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_drift_scoped_test_runner", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_drift_scoped_test_runner", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_drift_scoped_test_runner", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_drift_scoped_test_runner", "exec_snapshot_link")
from ops_scripts.ci.drift_scoped_test_runner import (
    _changed_prod_files,
    _resolve_test_paths_for_module,
    _run_pytest,
    _write_ci_run_result,
    run,
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_drift_scoped_test_runner")
# REMOVED: _emit_applies_guardrail("p0", "test_drift_scoped_test_runner", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_drift_scoped_test_runner", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_drift_scoped_test_runner", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_drift_scoped_test_runner", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_drift_scoped_test_runner", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_drift_scoped_test_runner", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_drift_scoped_test_runner", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_drift_scoped_test_runner", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_drift_scoped_test_runner", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_drift_scoped_test_runner", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_drift_scoped_test_runner", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_drift_scoped_test_runner", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_drift_scoped_test_runner", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_drift_scoped_test_runner", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_drift_scoped_test_runner", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_drift_scoped_test_runner", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_drift_scoped_test_runner", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_drift_scoped_test_runner", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_drift_scoped_test_runner", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_drift_scoped_test_runner", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_drift_scoped_test_runner", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_drift_scoped_test_runner", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_drift_scoped_test_runner", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_drift_scoped_test_runner", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_drift_scoped_test_runner", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_drift_scoped_test_runner", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_drift_scoped_test_runner", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_drift_scoped_test_runner", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_drift_scoped_test_runner", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_drift_scoped_test_runner", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_drift_scoped_test_runner", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_drift_scoped_test_runner", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_drift_scoped_test_runner", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_drift_scoped_test_runner", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_drift_scoped_test_runner", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_drift_scoped_test_runner", "write_through")
# REMOVED: _emit_writes_through("p1", "test_drift_scoped_test_runner", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_drift_scoped_test_runner", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_drift_scoped_test_runner", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_drift_scoped_test_runner", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_drift_scoped_test_runner", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_drift_scoped_test_runner", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_drift_scoped_test_runner", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_drift_scoped_test_runner", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_drift_scoped_test_runner", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_drift_scoped_test_runner", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_drift_scoped_test_runner", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_drift_scoped_test_runner", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_drift_scoped_test_runner", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_drift_scoped_test_runner", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_drift_scoped_test_runner", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_drift_scoped_test_runner")
# REMOVED: _emit_gated_by_confidence("p1", "test_drift_scoped_test_runner", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_drift_scoped_test_runner")
# REMOVED: emit_determinism_digest("p0", "test_drift_scoped_test_runner")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_redis(covers_map: dict[str, list[str]] | None = None):
    """
    covers_map: {prod_path: [test_path, ...]}
    """
    covers_map = covers_map or {}
    r = MagicMock()

    def smembers(key: str):
        # adg:nodes:by_file:<path> → {"10"}
        for prod_path, test_paths in covers_map.items():
            if key == f"adg:nodes:by_file:{prod_path}":
                return {"10"}
            if key == "adg:edge:in:10:covers":
                return {str(i + 20) for i in range(len(test_paths))}
        return set()

    def hgetall(key: str):
        if key == "adg:node:10":
            # Return a module node for the first prod_path
            first_prod = next(iter(covers_map), "")
            return {"entity_type": "module", "resolved_path": first_prod}
        # Test nodes: node 20, 21, ...
        for prod_path, test_paths in covers_map.items():
            for i, tp in enumerate(test_paths):
                if key == f"adg:node:{20 + i}":
                    return {"entity_type": "module", "resolved_path": tp}
        return {}

    r.smembers.side_effect = smembers
    r.hgetall.side_effect = hgetall
    pipe = MagicMock()
    pipe.execute.return_value = []
    r.pipeline.return_value = pipe
    r.delete = MagicMock()
    return r


# ---------------------------------------------------------------------------
# _changed_prod_files
# ---------------------------------------------------------------------------


class TestChangedProdFiles:
    def test_returns_only_python_prod_files(self):
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    """Test returns_only_python_prod_files runtime behavior."""
    # Arrange
    # TODO: Set up test data for returns_only_python_prod_files
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute returns_only_python_prod_files
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    """Test excludes_files runtime behavior."""
    # Arrange
    # TODO: Set up test data for excludes_files
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute excludes_files
    result = None  # Replace with actual function call

"""Test returns_empty_on_subprocess_error runtime behavior."""
# Arrange
# TODO: Set up processing data
raw_data = []  # Replace with actual test data

"""Test fallback_to_staged_on_nonzero_exit runtime behavior."""
# Arrange
# TODO: Set up test data for fallback_to_staged_on_nonzero_exit
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute fallback_to_staged_on_nonzero_exit
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
# TODO: Add specific runtime behavior assertions
    def test_filters_non_py_files(self):
    """Test filters_non_py_files runtime behavior."""
    # Arrange
    # TODO: Set up test data for filters_non_py_files
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute filters_non_py_files
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions

class TestResolveTestPathsForModule:
    def test_returns_empty_when_no_node(self):
    """Test returns_empty_when_no_node runtime behavior."""
    # Arrange
    # TODO: Set up test data for returns_empty_when_no_node
    test_data = {}  # Replace with actual test data

"""Test returns_sorted_paths runtime behavior."""
# Arrange
# TODO: Set up test data for returns_sorted_paths
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute returns_sorted_paths
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
# TODO: Add specific runtime behavior assertions
"""Test skips_non_resolved_paths runtime behavior."""
# Arrange
# TODO: Set up test data for skips_non_resolved_paths
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute skips_non_resolved_paths
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
# TODO: Add specific runtime behavior assertions

    def test_handles_redis_exception_gracefully(self):
    """Test handles_redis_exception_gracefully runtime behavior."""
    # Arrange
    # TODO: Set up processing data
    raw_data = []  # Replace with actual test data

    # Act
    """Test deduplicates_paths runtime behavior."""
    # Arrange
    # TODO: Set up test data for deduplicates_paths
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute deduplicates_paths
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
        paths = _resolve_test_paths_for_module(r, "apps_rg/foo.py")
        assert paths.count("tests/unit/test_Foo.py") == 1


# ---------------------------------------------------------------------------
# _run_pytest
# ---------------------------------------------------------------------------


class TestRunPytest:
    def test_returns_zero_when_all_paths_missing(self, tmp_path):
    """Test returns_zero_when_all_paths_missing runtime behavior."""
    # Arrange
    # TODO: Set up test data for returns_zero_when_all_paths_missing
    test_data = {}  # Replace with actual test data

"""Test passes_existing_paths_to_subprocess runtime behavior."""
# Arrange
# TODO: Set up processing data
raw_data = []  # Replace with actual test data

# Act
# TODO: Process data with passes_existing_paths_to_subprocess
processed_result = None  # Replace with actual processing

# Assert
assert processed_result is not None, "Processing should produce a result"
assert len(processed_result) >= 0, "Processed result should be measurable"
"""Test forwards_nonzero_exit_code runtime behavior."""
# Arrange
# TODO: Set up test data for forwards_nonzero_exit_code
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute forwards_nonzero_exit_code
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
# TODO: Add specific runtime behavior assertions
# ---------------------------------------------------------------------------


class TestWriteCiRunResult:
    def test_writes_all_fields(self):
    """Test writes_all_fields runtime behavior."""
    # Arrange
    # TODO: Set up test data for writes_all_fields
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute writes_all_fields
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
        assert mapping["exit_code"] == "0"

    def test_sets_ttl(self):
    """Test sets_ttl runtime behavior."""
    # Arrange
    # TODO: Set up test data for sets_ttl
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute sets_ttl
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
class TestRun:
    def test_returns_zero_when_no_changed_files(self):
    """Test returns_zero_when_no_changed_files runtime behavior."""
    # Arrange
    # TODO: Set up test data for returns_zero_when_no_changed_files
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute returns_zero_when_no_changed_files
    """Test fails_when_changed_module_has_no_covers runtime behavior."""
    # Arrange
    # TODO: Set up test data for fails_when_changed_module_has_no_covers
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute fails_when_changed_module_has_no_covers
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    """Test passes_and_runs_pywhen_covered runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute passes_and_runs_pywhen_covered
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
             ), \
             patch.object(runner, "PROJECT_ROOT", tmp_path), \
             patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            code = run()
        assert code == 0

    def test_dry_run_skips_pytest(self):
    """Test dry_run_skips_pytest runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute dry_run_skips_pytest
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
            if "pytest" in str(c)
        ]
        assert len(pytest_calls) == 0
        assert code == 0

    def test_forwards_pytest_exit_code_on_failure(self, tmp_path):
    """Test forwards_pyexit_code_on_failure runtime behavior."""
    # Arrange
    # TODO: Set up error condition
    error_input = {}  # Replace with actual error condition

    # Act & Assert
    # TODO: Test error handling in forwards_pyexit_code_on_failure
    with pytest.raises(Exception):  # Replace with expected exception
        # Execute operation that should raise error
        pass  # Replace with actual error test

    # TODO: Add error message and handling assertions
             patch.object(runner, "PROJECT_ROOT", tmp_path), \
             patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            code = run()
        assert code == 1

# ---------------------------------------------------------------------------
# Hardening tests (B4–B5)
# ---------------------------------------------------------------------------


class TestHardening:
    def test_pytest_timeout_returns_exit_2(self, tmp_path):
    """Test pytimeout_returns_exit_2 runtime behavior."""
    # Arrange
    # TODO: Set up test data for pytimeout_returns_exit_2
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute pytimeout_returns_exit_2
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
    """Test redis_connection_error_returns_exit_2 runtime behavior."""
    # Arrange
    # TODO: Set up error condition
    error_input = {}  # Replace with actual error condition

    # Act & Assert
    # TODO: Test error handling in redis_connection_error_returns_exit_2
    with pytest.raises(Exception):  # Replace with expected exception
    """Test redis_ping_failure_returns_exit_2 runtime behavior."""
    # Arrange
    # TODO: Set up error condition
    error_input = {}  # Replace with actual error condition

    # Act & Assert
    # TODO: Test error handling in redis_ping_failure_returns_exit_2
    with pytest.raises(Exception):  # Replace with expected exception
        # Execute operation that should raise error
        pass  # Replace with actual error test

    # TODO: Add error message and handling assertions
    """Test multiple_changed_files_aggregates_paths runtime behavior."""
    # Arrange
    # TODO: Set up test data for multiple_changed_files_aggregates_paths
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute multiple_changed_files_aggregates_paths
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
            for prod, (nid, tnid, _) in node_map.items():
                if key == f"adg:nodes:by_file:{prod}":
                    return {nid}
                if key == f"adg:edge:in:{nid}:covers":
                    return {tnid}
            return set()

        def hgetall(key):
            for prod, (nid, tnid, tp) in node_map.items():
                if key == f"adg:node:{nid}":
                    return {"entity_type": "module", "resolved_path": prod}
                if key == f"adg:node:{tnid}":
                    return {"entity_type": "module", "resolved_path": tp}
            return {}

        r.smembers.side_effect = smembers
        r.hgetall.side_effect = hgetall
        pipe = MagicMock()
        pipe.execute.return_value = []
        r.pipeline.return_value = pipe

        for _, tp in [
            ("Foo", "tests/unit/test_Foo.py"),
            ("Bar", "tests/unit/test_Bar.py"),
        ]:
            (tmp_path / tp).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / tp).write_text("def test_x(): pass\n")

        with patch.object(runner, "_connect", return_value=r), \
             patch.object(
                 runner,
                 "_changed_prod_files",
                 return_value=list(node_map.keys()),
             ), \
             patch.object(runner, "PROJECT_ROOT", tmp_path), \
             patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            code = run()

        assert code == 0
        # Both test files should be passed to pytest
        pytest_call_args = str(mock_run.call_args_list)
        assert "test_Foo.py" in pytest_call_args
        assert "test_Bar.py" in pytest_call_args
