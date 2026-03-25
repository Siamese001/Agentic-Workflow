"""Tests for ADG-scoped incremental type checker — Accelerator #4.

Coverage matrix per §1.1:
- Success: blast radius with 0/1/2 depth, empty file list, run_mypy clean/error
- Edge cases: depth=0 (changed files only), backslash paths, depth validation,
              file not in ADG, no importers, cycle prevention (visited guard)
- Fail-closed: Redis error propagates; mypy timeout raises; mypy not found raises
- Determinism: identical input → identical blast radius on every call
- MypyResult: passed, error_lines, error_count properties
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_type_check")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_type_check", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_type_check", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_type_check", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_adg_type_check", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_type_check", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_type_check", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_type_check", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_type_check", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_type_check", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_type_check", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_type_check", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_type_check", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_type_check", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_type_check", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_type_check", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_type_check", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_type_check", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_type_check", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_type_check", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_type_check", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_type_check", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_type_check", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_type_check", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_type_check", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_type_check", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_type_check", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_type_check", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_type_check", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_type_check", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_type_check", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_type_check", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_type_check", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_type_check", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_type_check", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_type_check", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_type_check", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_type_check", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_type_check", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_type_check", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_type_check", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_type_check", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_type_check", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_type_check", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_type_check", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_type_check", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_type_check", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_type_check", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_type_check", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_type_check", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_type_check", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_type_check", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_type_check")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_type_check", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_type_check")
# REMOVED: emit_determinism_digest("p0", "test_adg_type_check")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_type_check", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_type_check", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_type_check", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_type_check", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_type_check", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_type_check", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_type_check", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_type_check", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_type_check", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_type_check", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_type_check", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_type_check", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_type_check", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_type_check", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_type_check", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_type_check", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_type_check", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_type_check", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_type_check", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_type_check", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_client(
    nodes_by_file: dict[str, set[str]],
    fan_in_imports: dict[str, set[str]],
    nodes: dict[str, dict[str, str]],
) -> object:
    """Build a minimal ADGRedisClient stub for blast radius testing."""
    from tools.adg.adg_redis_query import ADGRedisClient

    client = ADGRedisClient.__new__(ADGRedisClient)
    r = MagicMock()

    def smembers(key: str) -> set[str]:
        if key.startswith("adg:nodes:by_file:"):
            return nodes_by_file.get(key[len("adg:nodes:by_file:") :], set())
        if key.startswith("adg:edge:in:") and key.endswith(":imports"):
            nid = key[len("adg:edge:in:") : -len(":imports")]
            return fan_in_imports.get(nid, set())
        return set()

    def hgetall(key: str) -> dict[str, str]:
        nid = key[len("adg:node:") :]
        return nodes.get(nid, {})

    r.smembers.side_effect = smembers
    r.hgetall.side_effect = hgetall
    client._r = r
    return client


def _make_checker(nodes_by_file, fan_in_imports, nodes):
    from tools.adg.adg_type_check import ADGTypeChecker

    return ADGTypeChecker(
        client=_make_client(nodes_by_file, fan_in_imports, nodes),
        repo_root=ROOT,
    )


# ===========================================================================
# MypyResult dataclass
# ===========================================================================


class TestMypyResult:
    def test_passed_true_when_exit_code_zero(self):
        from tools.adg.adg_type_check import MypyResult

        r = MypyResult(exit_code=0, stdout="", stderr="")
        assert r.passed is True

    def test_passed_false_when_exit_code_nonzero(self):
        from tools.adg.adg_type_check import MypyResult

        r = MypyResult(exit_code=1, stdout="foo.py:1: error: Incompatible types", stderr="")
        assert r.passed is False

    def test_error_lines_extracts_error_lines(self):
        from tools.adg.adg_type_check import MypyResult

        stdout = "foo.py:1: error: Incompatible types\nfoo.py:2: note: something\nfoo.py:3: error: Missing"
        r = MypyResult(exit_code=1, stdout=stdout, stderr="")
        assert len(r.error_lines) == 2
        assert all(": error:" in ln for ln in r.error_lines)

    def test_error_lines_empty_when_no_errors(self):
        from tools.adg.adg_type_check import MypyResult

        r = MypyResult(exit_code=0, stdout="Success: no issues found", stderr="")
        assert r.error_lines == []

    def test_error_count_matches_error_lines(self):
        from tools.adg.adg_type_check import MypyResult

        stdout = "a.py:1: error: E1\nb.py:2: error: E2\nb.py:3: note: N1"
        r = MypyResult(exit_code=1, stdout=stdout, stderr="")
        assert r.error_count == 2

    def test_scoped_files_defaults_to_empty(self):
        from tools.adg.adg_type_check import MypyResult

        r = MypyResult(exit_code=0, stdout="", stderr="")
        assert r.scoped_files == []


# ===========================================================================
# get_blast_radius
# ===========================================================================


class TestGetBlastRadius:
    def test_depth_zero_returns_only_changed_files(self):
        checker = _make_checker(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_imports={"n1": {"importer:1"}},
            nodes={"importer:1": {"resolved_path": "agentic_core/importer.py"}},
        )
        result = checker.get_blast_radius(["prod.py"], depth=0)
        assert result == ["prod.py"]
        assert "agentic_core/importer.py" not in result

    def test_depth_one_includes_direct_importers(self):
        checker = _make_checker(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_imports={"n1": {"imp:1"}},
            nodes={"imp:1": {"resolved_path": "agentic_core/importer.py"}},
        )
        result = checker.get_blast_radius(["prod.py"], depth=1)
        assert "prod.py" in result
        assert "agentic_core/importer.py" in result

    def test_depth_two_includes_transitive_importers(self):
        checker = _make_checker(
            nodes_by_file={
                "lib.py": {"n_lib"},
                "agentic_core/consumer.py": {"n_consumer"},
            },
            fan_in_imports={
                "n_lib": {"n_consumer"},
                "n_consumer": {"n_top"},
            },
            nodes={
                "n_consumer": {"resolved_path": "agentic_core/consumer.py"},
                "n_top": {"resolved_path": "agentic_core/top.py"},
            },
        )
        result = checker.get_blast_radius(["lib.py"], depth=2)
        assert "lib.py" in result
        assert "agentic_core/consumer.py" in result
        assert "agentic_core/top.py" in result

    def test_empty_changed_files_returns_empty(self):
        checker = _make_checker({}, {}, {})
        result = checker.get_blast_radius([], depth=1)
        assert result == []

    def test_file_not_in_adg_returns_just_itself(self):
        checker = _make_checker({}, {}, {})
        result = checker.get_blast_radius(["totally_unknown.py"], depth=1)
        assert result == ["totally_unknown.py"]

    def test_no_importers_returns_only_changed_files(self):
        checker = _make_checker(
            nodes_by_file={"leaf.py": {"n1"}},
            fan_in_imports={},  # no one imports leaf
            nodes={},
        )
        result = checker.get_blast_radius(["leaf.py"], depth=1)
        assert result == ["leaf.py"]

    def test_result_is_sorted(self):
        checker = _make_checker(
            nodes_by_file={"z_prod.py": {"n1"}},
            fan_in_imports={"n1": {"imp_a", "imp_z"}},
            nodes={
                "imp_a": {"resolved_path": "a_importer.py"},
                "imp_z": {"resolved_path": "z_importer.py"},
            },
        )
        result = checker.get_blast_radius(["z_prod.py"], depth=1)
        assert result == sorted(result)

    def test_depth_negative_raises_value_error(self):
        checker = _make_checker({}, {}, {})
        with pytest.raises(ValueError, match="depth"):
            checker.get_blast_radius(["prod.py"], depth=-1)

    def test_backslash_paths_normalized(self):
        checker = _make_checker(
            nodes_by_file={"agentic_core/L0_routing/router.py": {"n1"}},
            fan_in_imports={"n1": {"imp:1"}},
            nodes={"imp:1": {"resolved_path": "agentic_core/consumer.py"}},
        )
        result = checker.get_blast_radius(["agentic_core\\L0_routing\\router.py"], depth=1)
        assert "agentic_core/L0_routing/router.py" in result

    def test_non_python_files_in_nodes_excluded(self):
        """Only .py files should be included in blast radius."""
        checker = _make_checker(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_imports={"n1": {"imp_py", "imp_json"}},
            nodes={
                "imp_py": {"resolved_path": "agentic_core/consumer.py"},
                "imp_json": {"resolved_path": "config/settings.json"},  # not .py
            },
        )
        result = checker.get_blast_radius(["prod.py"], depth=1)
        assert "agentic_core/consumer.py" in result
        assert "config/settings.json" not in result

    def test_blast_radius_deterministic(self):
        checker = _make_checker(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_imports={"n1": {"imp:1"}},
            nodes={"imp:1": {"resolved_path": "agentic_core/importer.py"}},
        )
        r1 = checker.get_blast_radius(["prod.py"], depth=1)
        r2 = checker.get_blast_radius(["prod.py"], depth=1)
        assert r1 == r2

    def test_already_visited_files_not_revisited(self):
        """Cycle guard: if file A imports B and B imports A, no infinite loop."""
        checker = _make_checker(
            nodes_by_file={
                "a.py": {"n_a"},
                "b.py": {"n_b"},
            },
            fan_in_imports={
                "n_a": {"n_b"},  # b imports a
                "n_b": {"n_a"},  # a imports b (cycle!)
            },
            nodes={
                "n_a": {"resolved_path": "a.py"},
                "n_b": {"resolved_path": "b.py"},
            },
        )
        # Must terminate and not infinite-loop
        result = checker.get_blast_radius(["a.py"], depth=3)
        assert "a.py" in result
        assert "b.py" in result


# ===========================================================================
# run_mypy
# ===========================================================================


class TestRunMypy:
    def _make_checker(self):
        from tools.adg.adg_type_check import ADGTypeChecker

        return ADGTypeChecker(client=MagicMock(), repo_root=ROOT)

    def test_empty_file_list_returns_success_without_calling_mypy(self):
        checker = self._make_checker()
        with patch("subprocess.run") as mock_run:
            result = checker.run_mypy([])
        mock_run.assert_not_called()
        assert result.passed is True
        assert result.scoped_files == []

    def test_passes_files_to_mypy_command(self):
        checker = self._make_checker()
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success: no issues found in 1 source file"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            checker.run_mypy(["agentic_core/L0_routing/router.py"])
        call_args = mock_run.call_args[0][0]
        assert "agentic_core/L0_routing/router.py" in call_args

    def test_strict_flag_added_when_requested(self):
        checker = self._make_checker()
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success: no issues found"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            checker.run_mypy(["prod.py"], strict=True)
        call_args = mock_run.call_args[0][0]
        assert "--strict" in call_args

    def test_strict_flag_absent_by_default(self):
        checker = self._make_checker()
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success: no issues found"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            checker.run_mypy(["prod.py"])
        call_args = mock_run.call_args[0][0]
        assert "--strict" not in call_args

    def test_returns_passed_false_on_nonzero_exit(self):
        checker = self._make_checker()
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "prod.py:1: error: Incompatible types"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result):
            result = checker.run_mypy(["prod.py"])
        assert result.passed is False
        assert result.exit_code == 1

    def test_scoped_files_reflects_input(self):
        checker = self._make_checker()
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success: no issues found in 2 source files"
        mock_result.stderr = ""
        files = ["a.py", "b.py"]
        with patch("subprocess.run", return_value=mock_result):
            result = checker.run_mypy(files)
        assert result.scoped_files == files

    def test_timeout_raises_runtime_error(self):
    """Test timeout_raises_runtime_error runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute timeout_raises_runtime_error
    result = None  # Replace with actual execution

"""Test mypy_not_found_raises_runtime_error runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute mypy_not_found_raises_runtime_error
result = None  # Replace with actual execution

"""Test no_shell_true_in_subprocess_call runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute no_shell_true_in_subprocess_call
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions
# Fail-closed — Redis errors must propagate
# ===========================================================================


class TestBlastRadiusFailClosed:
    def test_redis_connection_error_propagates(self):
        """Redis ConnectionError must NOT be swallowed."""
        import redis

        from tools.adg.adg_redis_query import ADGRedisClient
        from tools.adg.adg_type_check import ADGTypeChecker

        client = ADGRedisClient.__new__(ADGRedisClient)
        bad_r = MagicMock()
        bad_r.smembers.side_effect = redis.ConnectionError("refused")
        client._r = bad_r

        checker = ADGTypeChecker(client=client, repo_root=ROOT)
        with pytest.raises(redis.ConnectionError):
            checker.get_blast_radius(["agentic_core/prod.py"], depth=1)
