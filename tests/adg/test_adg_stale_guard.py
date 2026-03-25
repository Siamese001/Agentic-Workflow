"""Tests for ADG staleness guard — Accelerator #2.

Coverage matrix per §1.1:
- Success: fresh ADG (commit before ingest), stale ADG (commit after ingest)
- Edge cases: no Python commits, missing ingested_at field, exact boundary (equal timestamps)
- Fail-closed: Redis unavailable raises RuntimeError; git failure raises RuntimeError
- State transitions: fresh→assert_fresh OK; stale→assert_fresh raises
- Determinism: StalenessResult.seconds_stale computed from fixed timestamps
- Subprocess timeout: git commands that time out raise RuntimeError
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_stale_guard")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_stale_guard", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_stale_guard", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_stale_guard", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_adg_stale_guard", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_stale_guard", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_stale_guard", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_stale_guard", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_stale_guard", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_stale_guard", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_stale_guard", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_stale_guard", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_stale_guard", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_stale_guard", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_stale_guard", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_stale_guard", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_stale_guard", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_stale_guard", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_stale_guard", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_stale_guard", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_stale_guard", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_stale_guard", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_stale_guard", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_stale_guard", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_stale_guard", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_stale_guard", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_stale_guard", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_stale_guard", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_stale_guard", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_stale_guard", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_stale_guard", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_stale_guard", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_stale_guard", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_stale_guard", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_stale_guard", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_stale_guard", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_stale_guard", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_stale_guard", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_stale_guard", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_stale_guard", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_stale_guard", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_stale_guard", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_stale_guard", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_stale_guard", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_stale_guard", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_stale_guard", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_stale_guard", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_stale_guard", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_stale_guard", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_stale_guard", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_stale_guard", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_stale_guard", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_stale_guard")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_stale_guard", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_stale_guard")
# REMOVED: emit_determinism_digest("p0", "test_adg_stale_guard")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_stale_guard", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_stale_guard", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_stale_guard", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_stale_guard", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_stale_guard", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_stale_guard", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_stale_guard", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_stale_guard", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_stale_guard", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_stale_guard", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_stale_guard", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_stale_guard", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_stale_guard", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_stale_guard", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_stale_guard", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_stale_guard", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_stale_guard", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_stale_guard", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_stale_guard", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_stale_guard", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_adg_client(ingested_at: str | None) -> object:
    """Build a minimal ADGRedisClient stub with fixed ingested_at."""
    from tools.adg.adg_redis_query import ADGRedisClient

    client = ADGRedisClient.__new__(ADGRedisClient)
    r = MagicMock()
    meta = {}
    if ingested_at is not None:
        meta["ingested_at"] = ingested_at
    r.hgetall.return_value = meta
    client._r = r
    return client


def _make_checker(ingested_at: str | None, repo_root: Path | None = None):
    from tools.adg.adg_stale_guard import ADGStalenessChecker

    client = _make_adg_client(ingested_at)
    return ADGStalenessChecker(client=client, repo_root=repo_root or ROOT)


# ===========================================================================
# StalenessResult dataclass
# ===========================================================================


class TestStalenessResult:
    def test_seconds_stale_positive_when_stale(self):
        from tools.adg.adg_stale_guard import StalenessResult

        r = StalenessResult(is_stale=True, ingest_time=1000.0, last_commit_time=1100.0)
        assert r.seconds_stale == 100.0

    def test_seconds_stale_zero_when_fresh(self):
        from tools.adg.adg_stale_guard import StalenessResult

        r = StalenessResult(is_stale=False, ingest_time=1100.0, last_commit_time=1000.0)
        assert r.seconds_stale == 0.0

    def test_seconds_stale_zero_at_exact_boundary(self):
        from tools.adg.adg_stale_guard import StalenessResult

        r = StalenessResult(is_stale=False, ingest_time=1000.0, last_commit_time=1000.0)
        assert r.seconds_stale == 0.0

    def test_changed_files_defaults_to_empty_list(self):
        from tools.adg.adg_stale_guard import StalenessResult

        r = StalenessResult(is_stale=False, ingest_time=0.0, last_commit_time=0.0)
        assert r.changed_files == []


# ===========================================================================
# _get_ingest_time
# ===========================================================================


class TestGetIngestTime:
    def test_returns_float_from_meta(self):
        checker = _make_checker(ingested_at="1741000000.5")
        result = checker._get_ingest_time()
        assert result == 1741000000.5

    def test_missing_ingested_at_raises_runtime_error(self):
        checker = _make_checker(ingested_at=None)
        with pytest.raises(RuntimeError, match="ingested_at"):
            checker._get_ingest_time()

    def test_invalid_float_raises_value_error(self):
        checker = _make_checker(ingested_at="not-a-float")
        with pytest.raises(ValueError):
            checker._get_ingest_time()


# ===========================================================================
# _get_last_python_commit_time
# ===========================================================================


class TestGetLastPythonCommitTime:
    def test_returns_float_timestamp(self):
        checker = _make_checker(ingested_at="0")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "1741050000\n"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result):
            t = checker._get_last_python_commit_time()
        assert t == 1741050000.0

    def test_no_python_commits_returns_zero(self):
        checker = _make_checker(ingested_at="0")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result):
            t = checker._get_last_python_commit_time()
        assert t == 0.0

    def test_git_failure_raises_runtime_error(self):
        checker = _make_checker(ingested_at="0")
        mock_result = MagicMock()
        mock_result.returncode = 128
        mock_result.stdout = ""
        mock_result.stderr = "not a git repo"
        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(RuntimeError, match="git log failed"):
                checker._get_last_python_commit_time()

    def test_timeout_raises_runtime_error(self):
        checker = _make_checker(ingested_at="0")
        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="git", timeout=30),
        ):
            with pytest.raises(RuntimeError, match="timed out"):
                checker._get_last_python_commit_time()

    def test_git_called_with_no_shell(self):
        checker = _make_checker(ingested_at="0")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "1741000000\n"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            checker._get_last_python_commit_time()
        args, kwargs = mock_run.call_args
        cmd = args[0]
        assert cmd[0] == "git"
        assert kwargs.get("shell", False) is False  # §3.2: no shell=True


# ===========================================================================
# check() — full staleness check
# ===========================================================================


class TestStalenessCheck:
    def test_fresh_when_last_commit_before_ingest(self):
        checker = _make_checker(ingested_at="1741100000")
        with patch.object(checker, "_get_last_python_commit_time", return_value=1741000000.0):
            result = checker.check()
        assert result.is_stale is False
        assert "fresh" in result.message.lower()

    def test_stale_when_last_commit_after_ingest(self):
        checker = _make_checker(ingested_at="1741000000")
        with (
            patch.object(checker, "_get_last_python_commit_time", return_value=1741100000.0),
            patch.object(checker, "_get_files_changed_since", return_value=["agentic_core/foo.py"]),
        ):
            result = checker.check()
        assert result.is_stale is True
        assert "STALE" in result.message
        assert "agentic_core/foo.py" in result.changed_files

    def test_fresh_at_exact_boundary_equal_timestamps(self):
        """Exactly equal timestamps → fresh (not stale)."""
        checker = _make_checker(ingested_at="1741000000")
        with patch.object(checker, "_get_last_python_commit_time", return_value=1741000000.0):
            result = checker.check()
        assert result.is_stale is False

    def test_stale_result_contains_ingest_and_commit_times(self):
        checker = _make_checker(ingested_at="1741000000")
        with (
            patch.object(checker, "_get_last_python_commit_time", return_value=1741100000.0),
            patch.object(checker, "_get_files_changed_since", return_value=[]),
        ):
            result = checker.check()
        assert result.ingest_time == 1741000000.0
        assert result.last_commit_time == 1741100000.0

    def test_no_python_commits_is_fresh(self):
        """If last_commit_time == 0.0 (no commits), ADG is fresh."""
        checker = _make_checker(ingested_at="1741000000")
        with patch.object(checker, "_get_last_python_commit_time", return_value=0.0):
            result = checker.check()
        assert result.is_stale is False

    def test_check_is_deterministic(self):
        """Same inputs must yield same result on repeated calls."""
        checker = _make_checker(ingested_at="1741000000")
        with (
            patch.object(checker, "_get_last_python_commit_time", return_value=1741050000.0),
            patch.object(checker, "_get_files_changed_since", return_value=["a.py"]),
        ):
            r1 = checker.check()
            r2 = checker.check()
        assert r1.is_stale == r2.is_stale
        assert r1.changed_files == r2.changed_files


# ===========================================================================
# assert_fresh
# ===========================================================================


class TestAssertFresh:
    def test_does_not_raise_when_fresh(self):
        checker = _make_checker(ingested_at="1741100000")
        with patch.object(checker, "_get_last_python_commit_time", return_value=1741000000.0):
            checker.assert_fresh()  # must not raise

    def test_raises_when_stale(self):
        checker = _make_checker(ingested_at="1741000000")
        with (
            patch.object(checker, "_get_last_python_commit_time", return_value=1741100000.0),
            patch.object(checker, "_get_files_changed_since", return_value=["foo.py"]),
        ):
            with pytest.raises(RuntimeError, match="STALE"):
                checker.assert_fresh()

    def test_error_message_contains_regen_instructions(self):
        checker = _make_checker(ingested_at="1741000000")
        with (
            patch.object(checker, "_get_last_python_commit_time", return_value=1741100000.0),
            patch.object(checker, "_get_files_changed_since", return_value=["foo.py"]),
        ):
            with pytest.raises(RuntimeError, match="adg_redis_ingest"):
                checker.assert_fresh()


# ===========================================================================
# CLI — Redis unavailability in --warn mode (regression gate for pre-commit)
# ===========================================================================


class TestCLIRedisUnavailable:
    """Gate: pre-commit T3g hook must exit 0 when Redis is down (warn mode).

    Tests run _cli() in-process with patched sys.argv to verify exact exit
    codes via SystemExit, so mocks apply correctly to the same process.
    """

    def _call_cli(self, args: list[str]) -> tuple[int, str]:
        """Invoke _cli() in-process with patched argv. Returns (exit_code, stderr)."""
        import io

        from tools.adg.adg_stale_guard import _cli

        captured_err = io.StringIO()
        with (
            patch("sys.argv", ["adg_stale_guard"] + args),
            patch("sys.stderr", captured_err),
        ):
            try:
                _cli()
                return 0, captured_err.getvalue()
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else int(exc.code or 0)
                return code, captured_err.getvalue()

    def test_warn_mode_exits_0_on_redis_connection_error(self):
        """--warn exits 0 even when redis raises ConnectionError."""
        import redis

        with patch("tools.adg.adg_stale_guard.ADGRedisClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.ping.side_effect = redis.ConnectionError("Connection refused")
            mock_cls.return_value = mock_instance
            code, _ = self._call_cli(["--warn"])
        assert code == 0, f"--warn must exit 0 when Redis is down; got {code}"

    def test_warn_mode_exits_0_on_runtime_error(self):
        """--warn exits 0 when ADG cache is not loaded (RuntimeError from ping)."""
        with patch("tools.adg.adg_stale_guard.ADGRedisClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.ping.side_effect = RuntimeError("ADG Redis cache is not loaded")
            mock_cls.return_value = mock_instance
            code, _ = self._call_cli(["--warn"])
        assert code == 0, f"--warn must exit 0 on RuntimeError; got {code}"

    def test_strict_mode_exits_1_on_redis_connection_error(self):
        """Without --warn, redis.ConnectionError must exit 1 (fail-closed)."""
        import redis

        with patch("tools.adg.adg_stale_guard.ADGRedisClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.ping.side_effect = redis.ConnectionError("Connection refused")
            mock_cls.return_value = mock_instance
            code, _ = self._call_cli([])
        assert code == 1, f"Strict mode must exit 1 when Redis is down; got {code}"

    def test_warn_mode_prints_warning_to_stderr(self):
        """--warn prints a human-readable WARNING message when Redis is unavailable."""
        import redis

        with patch("tools.adg.adg_stale_guard.ADGRedisClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.ping.side_effect = redis.ConnectionError("Connection refused")
            mock_cls.return_value = mock_instance
            _, stderr = self._call_cli(["--warn"])
        assert "WARNING" in stderr, f"--warn must emit a WARNING message to stderr; got {stderr!r}"

    def test_warn_mode_exits_0_when_stale(self):
        """--warn exits 0 even when ADG is genuinely stale (non-blocking)."""
        from tools.adg.adg_stale_guard import ADGStalenessChecker, StalenessResult

        stale_result = StalenessResult(
            is_stale=True,
            ingest_time=1000000000.0,
            last_commit_time=1000100000.0,
            changed_files=["foo.py"],
            message="ADG is STALE",
        )
        with (
            patch("tools.adg.adg_stale_guard.ADGRedisClient") as mock_cls,
            patch.object(ADGStalenessChecker, "check", return_value=stale_result),
        ):
            mock_instance = MagicMock()
            mock_instance.ping.return_value = True
            mock_cls.return_value = mock_instance
            code, _ = self._call_cli(["--warn"])
        assert code == 0, f"--warn must exit 0 even when stale; got {code}"
