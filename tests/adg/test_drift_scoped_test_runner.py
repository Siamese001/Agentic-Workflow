"""
Regression tests for ops_scripts/ci/drift_scoped_test_runner.py

All tests mock Redis, subprocess, and filesystem — no live connections.  24 tests.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import ops_scripts.ci.drift_scoped_test_runner as runner
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="apps_rg/reasoning/Foo.py\ntests/unit/test_Foo.py\nREADME.md\n",
            )
            files = _changed_prod_files("origin/main")
        assert "apps_rg/reasoning/Foo.py" in files
        assert "tests/unit/test_Foo.py" not in files
        assert "README.md" not in files

    def test_excludes_test_files(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="tests/adg/test_drift.py\n",
            )
            files = _changed_prod_files("origin/main")
        assert files == []

    def test_returns_empty_on_subprocess_error(self):
        with patch("subprocess.run", side_effect=OSError("git not found")):
            files = _changed_prod_files("origin/main")
        assert files == []

    def test_fallback_to_staged_on_nonzero_exit(self):
        call_count = [0]

        def mock_run_side(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return MagicMock(returncode=1, stdout="")
            return MagicMock(returncode=0, stdout="apps_rg/foo.py\n")

        with patch("subprocess.run", side_effect=mock_run_side):
            files = _changed_prod_files("origin/main")
        assert call_count[0] == 2
        assert "apps_rg/foo.py" in files

    def test_filters_non_py_files(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="apps_rg/foo.py\napps_rg/config.json\napps_rg/README.md\n",
            )
            files = _changed_prod_files("origin/main")
        assert files == ["apps_rg/foo.py"]


# ---------------------------------------------------------------------------
# _resolve_test_paths_for_module
# ---------------------------------------------------------------------------


class TestResolveTestPathsForModule:
    def test_returns_empty_when_no_node(self):
        r = _mock_redis({})
        paths = _resolve_test_paths_for_module(r, "apps_rg/reasoning/Foo.py")
        assert paths == []

    def test_returns_sorted_test_paths(self):
        r = _mock_redis(
            {
                "apps_rg/reasoning/Foo.py": [
                    "tests/unit/apps_rg/test_Foo_adg.py",
                    "tests/adg/test_coverage.py",
                ]
            }
        )
        paths = _resolve_test_paths_for_module(r, "apps_rg/reasoning/Foo.py")
        assert "tests/unit/apps_rg/test_Foo_adg.py" in paths
        assert paths == sorted(paths)

    def test_skips_non_test_resolved_paths(self):
        r = MagicMock()
        r.smembers.side_effect = lambda k: (
            {"10"} if "by_file" in k else {"20"} if "covers" in k else set()
        )
        r.hgetall.side_effect = lambda k: (
            {"entity_type": "module"}
            if k == "adg:node:10"
            else {"entity_type": "module", "resolved_path": "apps_rg/prod.py"}
            if k == "adg:node:20"
            else {}
        )
        paths = _resolve_test_paths_for_module(r, "apps_rg/reasoning/Foo.py")
        assert paths == []  # resolved_path doesn't start with "tests/"

    def test_handles_redis_exception_gracefully(self):
        r = MagicMock()
        r.smembers.side_effect = Exception("connection refused")
        paths = _resolve_test_paths_for_module(r, "apps_rg/reasoning/Foo.py")
        assert paths == []

    def test_deduplicates_paths(self):
        r = MagicMock()
        # Two module nodes pointing to same test
        r.smembers.side_effect = lambda k: (
            {"10", "11"} if "by_file" in k
            else {"20"} if "covers" in k
            else set()
        )
        r.hgetall.side_effect = lambda k: (
            {"entity_type": "module"} if k in ("adg:node:10", "adg:node:11")
            else {"entity_type": "module", "resolved_path": "tests/unit/test_Foo.py"}
            if k == "adg:node:20"
            else {}
        )
        paths = _resolve_test_paths_for_module(r, "apps_rg/foo.py")
        assert paths.count("tests/unit/test_Foo.py") == 1


# ---------------------------------------------------------------------------
# _run_pytest
# ---------------------------------------------------------------------------


class TestRunPytest:
    def test_returns_zero_when_all_paths_missing(self, tmp_path):
        with patch.object(runner, "PROJECT_ROOT", tmp_path):
            code = _run_pytest(["tests/nonexistent.py"])
        assert code == 0

    def test_passes_existing_paths_to_subprocess(self, tmp_path):
        test_file = tmp_path / "tests" / "dummy_test.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def test_dummy(): pass\n")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch.object(runner, "PROJECT_ROOT", tmp_path):
                code = _run_pytest(["tests/dummy_test.py"])
        assert mock_run.called
        assert code == 0

    def test_forwards_nonzero_exit_code(self, tmp_path):
        test_file = tmp_path / "tests" / "failing_test.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def test_fail(): assert False\n")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            with patch.object(runner, "PROJECT_ROOT", tmp_path):
                code = _run_pytest(["tests/failing_test.py"])
        assert code == 1


# ---------------------------------------------------------------------------
# _write_ci_run_result
# ---------------------------------------------------------------------------


class TestWriteCiRunResult:
    def test_writes_all_fields(self):
        r = MagicMock()
        pipe = MagicMock()
        pipe.execute.return_value = []
        r.pipeline.return_value = pipe

        _write_ci_run_result(r, 3, 5, ["uncov.py"], 0)

        pipe.hmset.assert_called_once()
        key, mapping = pipe.hmset.call_args[0]
        assert key == "adg:drift:ci_run"
        assert mapping["changed_files"] == "3"
        assert mapping["test_files_run"] == "5"
        assert mapping["uncovered_changed"] == "1"
        assert mapping["exit_code"] == "0"

    def test_sets_ttl(self):
        r = MagicMock()
        pipe = MagicMock()
        pipe.execute.return_value = []
        r.pipeline.return_value = pipe
        _write_ci_run_result(r, 1, 2, [], 0)
        pipe.expire.assert_called_once_with("adg:drift:ci_run", 3600)


# ---------------------------------------------------------------------------
# run() — integration
# ---------------------------------------------------------------------------


class TestRun:
    def test_returns_zero_when_no_changed_files(self):
        r = _mock_redis()
        with patch.object(runner, "_connect", return_value=r), \
             patch.object(runner, "_changed_prod_files", return_value=[]):
            code = run()
        assert code == 0

    def test_fails_when_changed_module_has_no_covers(self):
        r = _mock_redis({})  # no covers for any module
        with patch.object(runner, "_connect", return_value=r), \
             patch.object(
                 runner,
                 "_changed_prod_files",
                 return_value=["apps_rg/reasoning/Foo.py"],
             ):
            code = run()
        assert code == 1

    def test_passes_and_runs_pytest_when_covered(self, tmp_path):
        test_path = "tests/unit/apps_rg/test_Foo_adg.py"
        abs_test = tmp_path / test_path
        abs_test.parent.mkdir(parents=True)
        abs_test.write_text("def test_dummy(): pass\n")

        r = _mock_redis(
            {"apps_rg/reasoning/Foo.py": [test_path]}
        )
        with patch.object(runner, "_connect", return_value=r), \
             patch.object(
                 runner,
                 "_changed_prod_files",
                 return_value=["apps_rg/reasoning/Foo.py"],
             ), \
             patch.object(runner, "PROJECT_ROOT", tmp_path), \
             patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            code = run()
        assert code == 0

    def test_dry_run_skips_pytest(self):
        test_path = "tests/unit/apps_rg/test_Foo_adg.py"
        r = _mock_redis({"apps_rg/reasoning/Foo.py": [test_path]})
        with patch.object(runner, "_connect", return_value=r), \
             patch.object(
                 runner,
                 "_changed_prod_files",
                 return_value=["apps_rg/reasoning/Foo.py"],
             ), \
             patch("subprocess.run") as mock_run:
            code = run(dry_run=True)
        # subprocess.run should NOT be called for pytest in dry-run
        pytest_calls = [
            c for c in mock_run.call_args_list
            if "pytest" in str(c)
        ]
        assert len(pytest_calls) == 0
        assert code == 0

    def test_forwards_pytest_exit_code_on_failure(self, tmp_path):
        test_path = "tests/unit/apps_rg/test_Foo_adg.py"
        abs_test = tmp_path / test_path
        abs_test.parent.mkdir(parents=True)
        abs_test.write_text("def test_fail(): assert False\n")

        r = _mock_redis({"apps_rg/reasoning/Foo.py": [test_path]})
        with patch.object(runner, "_connect", return_value=r), \
             patch.object(
                 runner,
                 "_changed_prod_files",
                 return_value=["apps_rg/reasoning/Foo.py"],
             ), \
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
        """B4: pytest timeout → _run_pytest returns 2 instead of hanging."""
        import subprocess

        test_file = tmp_path / "tests" / "slow_test.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def test_slow(): pass\n")

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("pytest", 300)):
            with patch.object(runner, "PROJECT_ROOT", tmp_path):
                code = _run_pytest(["tests/slow_test.py"])
        assert code == 2

    def test_redis_connection_error_returns_exit_2(self):
        """B5: Redis down → run() returns 2 instead of raising."""
        import redis as redis_lib

        with patch.object(runner, "_connect", side_effect=redis_lib.ConnectionError("down")):
            code = run()
        assert code == 2

    def test_redis_ping_failure_returns_exit_2(self):
        """B5: Redis connects but ping raises → run() returns 2."""
        import redis as redis_lib

        r = MagicMock()
        r.ping.side_effect = redis_lib.ConnectionError("ping failed")
        with patch.object(runner, "_connect", return_value=r):
            code = run()
        assert code == 2


class TestMultipleChangedFiles:
    def test_multiple_changed_files_aggregates_test_paths(self, tmp_path):
        covers = {
            "apps_rg/reasoning/Foo.py": ["tests/unit/test_Foo.py"],
            "apps_rg/reasoning/Bar.py": ["tests/unit/test_Bar.py"],
        }

        # Build a more precise mock that handles two files
        r = MagicMock()
        node_map = {
            "apps_rg/reasoning/Foo.py": ("10", "20", "tests/unit/test_Foo.py"),
            "apps_rg/reasoning/Bar.py": ("11", "21", "tests/unit/test_Bar.py"),
        }

        def smembers(key):
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
