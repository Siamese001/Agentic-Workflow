# adg-grep-ban: skip-file
"""Tests for the ADG Grep-Ban Gate and enforcement hardenings.

Coverage:
  1. grep-ban gate core scanner — detects all forbidden patterns
  2. grep-ban gate exemptions — guardian: allow-grep passes through
  3. grep-ban gate negative — canonical ADG calls are NOT flagged
  4. redis.ConnectionError handling — all 3 accelerator CLIs exit 1 cleanly
  5. ADGQuerySession — stale guard asserted on enter; fail-closed; warn_only
  6. Pre-commit contract — T3h hook registered in .pre-commit-config.yaml
  7. CI workflow contract — adg-grep-ban-ci.yml exists and is valid
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import MagicMock, create_autospec, patch

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_grep_ban_gate")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_grep_ban_gate", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_grep_ban_gate", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_grep_ban_gate", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_adg_grep_ban_gate")
# REMOVED: emit_determinism_digest("p0", "test_adg_grep_ban_gate")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_grep_ban_gate", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_grep_ban_gate", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_grep_ban_gate", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_grep_ban_gate", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_grep_ban_gate", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_grep_ban_gate", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_grep_ban_gate", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_grep_ban_gate", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_grep_ban_gate", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_grep_ban_gate", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_grep_ban_gate", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_grep_ban_gate", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_grep_ban_gate", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_grep_ban_gate", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_grep_ban_gate", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_grep_ban_gate", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_grep_ban_gate", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_grep_ban_gate", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_grep_ban_gate", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_grep_ban_gate", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
from ops_scripts.ci.adg_grep_ban_gate import (
    _BANNED_PATTERNS,
    _EXEMPTION_RE,
    scan_file,
    scan_files,
)

# REMOVED: _emit_emits_metric_event("test_adg_grep_ban_gate", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_grep_ban_gate", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_grep_ban_gate", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_grep_ban_gate", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_grep_ban_gate", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_grep_ban_gate", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_grep_ban_gate", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_grep_ban_gate", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_grep_ban_gate", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_grep_ban_gate", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_grep_ban_gate", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_grep_ban_gate", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_grep_ban_gate", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_grep_ban_gate", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_grep_ban_gate", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_grep_ban_gate", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_grep_ban_gate", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_grep_ban_gate", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_grep_ban_gate", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_grep_ban_gate", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_grep_ban_gate", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_grep_ban_gate", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_grep_ban_gate", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_grep_ban_gate", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_grep_ban_gate", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_grep_ban_gate", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_grep_ban_gate", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_grep_ban_gate", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_grep_ban_gate", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_grep_ban_gate", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_grep_ban_gate", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_grep_ban_gate", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_grep_ban_gate", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_grep_ban_gate", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_grep_ban_gate", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_grep_ban_gate", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_grep_ban_gate", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_grep_ban_gate", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_grep_ban_gate", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_grep_ban_gate", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_grep_ban_gate", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_grep_ban_gate", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_grep_ban_gate", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_grep_ban_gate", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_grep_ban_gate", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_grep_ban_gate", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_grep_ban_gate", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_grep_ban_gate", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_grep_ban_gate")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_grep_ban_gate", "confidence_gate")

PRE_COMMIT_CFG = ROOT / ".pre-commit-config.yaml"
CI_WF = ROOT / ".github" / "workflows" / "adg-grep-ban-ci.yml"


# ===========================================================================
# 1. Core scanner — forbidden patterns ARE detected
# ===========================================================================


class TestGrepBanScanner:
    """Verify each forbidden grep/rg pattern is caught."""

    def _scan_line(self, line: str) -> bool:
        """Return True if the line triggers at least one banned pattern."""
        for pat in _BANNED_PATTERNS:
            if pat.search(line):
                return True
        return False

    def test_subprocess_run_grep_list_detected(self):
        line = '    result = subprocess.run(["grep", "-r", "MyClass", "."], capture_output=True)'
        assert self._scan_line(line), "subprocess.run(['grep',...]) must be banned"

    def test_subprocess_run_rg_list_detected(self):
        line = '    out = subprocess.run(["rg", "--json", "pattern"], capture_output=True)'
        assert self._scan_line(line), "subprocess.run(['rg',...]) must be banned"

    def test_subprocess_run_ripgrep_list_detected(self):
        line = '    p = subprocess.run(["ripgrep", "term", "src/"], capture_output=True)'
        assert self._scan_line(line), "subprocess.run(['ripgrep',...]) must be banned"

    def test_subprocess_call_grep_detected(self):
        line = "    subprocess.call(['grep', '-n', 'TODO', 'file.py'])"
        assert self._scan_line(line), "subprocess.call(['grep',...]) must be banned"

    def test_subprocess_check_output_rg_detected(self):
        line = "    out = subprocess.check_output(['rg', 'pattern', '--type', 'py'])"
        assert self._scan_line(line), "subprocess.check_output(['rg',...]) must be banned"

    def test_subprocess_popen_grep_detected(self):
        line = '    proc = subprocess.Popen(["grep", "-l", "import", "tools/"])'
        assert self._scan_line(line), "subprocess.Popen(['grep',...]) must be banned"

    def test_pure_comment_line_not_flagged_by_scan_file(self):
        """scan_file() must skip pure comment lines even if they contain banned patterns."""
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("# os.popen('grep -r ClassName .')  -- do not use this\n")
            tmp = Path(f.name)
        try:
            vs = scan_file(tmp)
            assert vs == [], f"Pure comment lines must be skipped; got: {vs}"
        finally:
            tmp.unlink()

    def test_os_popen_grep_in_code_detected(self):
        line = "    out = os.popen('grep -r ClassName .')"
        assert self._scan_line(line), "os.popen('grep ...') in code must be banned"

    def test_os_popen_rg_detected(self):
        line = '    lines = os.popen("rg --vimgrep pattern src/").readlines()'
        assert self._scan_line(line), "os.popen('rg ...') must be banned"

    def test_subprocess_run_ag_detected(self):
        line = '    subprocess.run(["ag", "SearchTerm", "--python"])'
        assert self._scan_line(line), "subprocess.run(['ag',...]) must be banned"

    def test_subprocess_run_findstr_detected(self):
        line = '    subprocess.run(["findstr", "/s", "pattern", "*.py"])'
        assert self._scan_line(line), "subprocess.run(['findstr',...]) must be banned"


# ===========================================================================
# 2. Exemption mechanism
# ===========================================================================


class TestGrepBanExemption:
    """Verify guardian: allow-grep exemption bypasses the gate."""

    def test_exemption_pattern_matches_canonical_form(self):
        line = '    subprocess.run(["grep", ...])  # guardian: allow-grep -- legacy script wrapper'
        assert _EXEMPTION_RE.search(line), "Canonical allow-grep exemption must match"

    def test_exemption_suppresses_scan_file_violation(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write(
                '    result = subprocess.run(["grep", "-r", "x"])  '
                "# guardian: allow-grep -- used in wrapper around legacy shell script\n"
            )
            tmp = Path(f.name)
        try:
            vs = scan_file(tmp)
            assert vs == [], f"Exempted line must produce zero violations; got: {vs!r}"
        finally:
            tmp.unlink()

    def test_non_canonical_exemption_does_not_suppress(self):
        """'# allow-grep' without 'guardian:' prefix is NOT a valid exemption."""
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write('    subprocess.run(["grep", "-r", "foo"])  # allow-grep -- test\n')
            tmp = Path(f.name)
        try:
            vs = scan_file(tmp)
            assert len(vs) == 1, "Non-canonical exemption must NOT suppress the violation"
        finally:
            tmp.unlink()

    def test_exemption_requires_nonempty_justification(self):
        """'guardian: allow-grep --' with nothing after is NOT a valid exemption."""
        line = '    subprocess.run(["grep", "x"])  # guardian: allow-grep --'
        assert not _EXEMPTION_RE.search(line), (
            "Empty justification after -- must NOT match the exemption regex"
        )


# ===========================================================================
# 3. Negative cases — canonical ADG calls are NOT flagged
# ===========================================================================


class TestGrepBanNegative:
    """Verify legitimate ADG-accelerator calls pass through without flags."""

    def _scan_line(self, line: str) -> bool:
        for pat in _BANNED_PATTERNS:
            if pat.search(line):
                return True
        return False

    def test_adg_search_nodes_not_flagged(self):
        line = "    nodes = adg.search_nodes('MyClass', layer='L3')"
        assert not self._scan_line(line), "adg.search_nodes() must NOT be flagged"

    def test_adg_search_files_not_flagged(self):
        line = "    files = adg.search_files('dashboard')"
        assert not self._scan_line(line), "adg.search_files() must NOT be flagged"

    def test_adg_test_selector_call_not_flagged(self):
        line = "    tests = selector.select_tests(changed_files)"
        assert not self._scan_line(line), "selector.select_tests() must NOT be flagged"

    def test_git_subprocess_not_flagged(self):
        line = '    subprocess.run(["git", "diff", "--name-only"], capture_output=True)'
        assert not self._scan_line(line), "git subprocess calls must NOT be flagged"

    def test_mypy_subprocess_not_flagged(self):
        line = '    subprocess.run([sys.executable, "-m", "mypy", *files])'
        assert not self._scan_line(line), "mypy subprocess calls must NOT be flagged"

    def test_python_subprocess_not_flagged(self):
        line = '    subprocess.run([sys.executable, "tools/adg/adg_stale_guard.py", "--warn"])'
        assert not self._scan_line(line), "Python subprocess calls must NOT be flagged"

    def test_string_containing_grep_word_in_comment_not_flagged(self):
        """A comment mentioning 'grep' must not trigger the gate."""
        line = "    # Do NOT use grep here — use adg.search_nodes() instead"
        assert not self._scan_line(line), "grep in comment must NOT be flagged"

    def test_scan_file_on_clean_file_returns_empty(self):
        """A file with only ADG calls must produce zero violations."""
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write(
                "from tools.adg.adg_redis_query import ADGRedisClient\n"
                "adg = ADGRedisClient()\n"
                "adg.ping()\n"
                "nodes = adg.search_nodes('MyClass')\n"
            )
            tmp = Path(f.name)
        try:
            assert scan_file(tmp) == []
        finally:
            tmp.unlink()


# ===========================================================================
# 4. Full file scan — multi-violation and mixed content
# ===========================================================================


class TestGrepBanScanFiles:
    """Full-file scanning: multiple violations, mixed exemptions."""

    def test_scan_detects_multiple_violations_in_one_file(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write(
                '    subprocess.run(["grep", "-r", "foo"])\n'
                '    subprocess.run(["rg", "bar"])\n'
                "    adg.search_nodes('baz')\n"
            )
            tmp = Path(f.name)
        try:
            vs = scan_file(tmp)
            assert len(vs) == 2, f"Expected 2 violations, got {len(vs)}"
        finally:
            tmp.unlink()

    def test_scan_files_aggregates_across_multiple_files(self):
        tmps = []
        for content in [
            '    subprocess.run(["grep", "x"])\n',
            "    adg.search_nodes('x')\n",
            '    subprocess.run(["rg", "y"])\n',
        ]:
            f = tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False)
            f.write(content)
            f.close()
            tmps.append(Path(f.name))
        try:
            result = scan_files(tmps)
            assert len(result) == 2, f"Expected violations in 2 files (not the clean one), got {len(result)}"
        finally:
            for p in tmps:
                p.unlink()

    def test_exit_code_1_on_violation(self):
        """Gate CLI exits 1 when violations are present."""
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write('    subprocess.run(["grep", "-r", "MyClass", "."])\n')
            tmp = Path(f.name)
        try:
            r = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "ops_scripts" / "ci" / "adg_grep_ban_gate.py"),
                    str(tmp),
                ],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
            )
            assert r.returncode == 1, f"Gate must exit 1 on violation; got {r.returncode}"
            assert "grep-ban violation" in r.stderr.lower(), "Stderr must mention 'grep-ban violation'"
        finally:
            tmp.unlink()

    def test_exit_code_0_on_clean_file(self):
        """Gate CLI exits 0 on a clean file."""
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("adg = ADGRedisClient()\nnodes = adg.search_nodes('X')\n")
            tmp = Path(f.name)
        try:
            r = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "ops_scripts" / "ci" / "adg_grep_ban_gate.py"),
                    str(tmp),
                ],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
            )
            assert r.returncode == 0, (
                f"Gate must exit 0 on clean file; got {r.returncode}. stderr={r.stderr!r}"
            )
        finally:
            tmp.unlink()

    def test_gate_self_scan_passes(self):
        """The gate script itself must have zero grep-ban violations."""
        gate_path = ROOT / "ops_scripts" / "ci" / "adg_grep_ban_gate.py"
        r = subprocess.run(
            [sys.executable, str(gate_path), str(gate_path)],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
        assert r.returncode == 0, f"adg_grep_ban_gate.py must pass its own check; stderr={r.stderr!r}"


# ===========================================================================
# 5. redis.ConnectionError handling in all 3 accelerator CLIs
# ===========================================================================


class TestConnectionErrorHandling:
    """All accelerator CLIs must exit 1 cleanly (no traceback) when Redis is down.

    Uses in-process _cli() calls with unittest.mock patches so the test is fast
    and deterministic regardless of whether a local Redis instance is running.
    """

    def _assert_cli_exits_1_on_connection_error(self, cli_fn, argv: list[str]) -> None:
        """Call cli_fn() with patched ping() -> ConnectionError, assert exit 1."""
        import io

        import redis as _redis

        err_buf = io.StringIO()
        with (
            patch(
                "tools.adg.adg_redis_query.ADGRedisClient.ping",
                side_effect=_redis.ConnectionError("Connection refused"),
            ),
            patch("sys.argv", argv),
            redirect_stderr(err_buf),
        ):
            with pytest.raises(SystemExit) as exc_info:
                cli_fn()
        assert exc_info.value.code == 1, (
            f"{argv[0]} must exit 1 on redis.ConnectionError; "
            f"got {exc_info.value.code!r}. stderr={err_buf.getvalue()!r}"
        )
        assert "Traceback" not in err_buf.getvalue(), (
            f"{argv[0]} must NOT print a raw traceback; stderr={err_buf.getvalue()!r}"
        )

    def test_adg_redis_query_exits_1_on_connection_error(self):
        from tools.adg.adg_redis_query import _cli

        self._assert_cli_exits_1_on_connection_error(_cli, ["adg_redis_query", "meta"])

    def test_adg_test_selector_exits_1_on_connection_error(self):
        from tools.adg.adg_test_selector import _cli

        self._assert_cli_exits_1_on_connection_error(_cli, ["adg_test_selector", "some_file.py"])

    def test_adg_type_check_exits_1_on_connection_error(self):
        from tools.adg.adg_type_check import _cli

        self._assert_cli_exits_1_on_connection_error(_cli, ["adg_type_check", "some_file.py"])

    def test_adg_test_selector_runtime_error_also_exits_1(self):
        """RuntimeError (cache not loaded) also exits 1 cleanly."""
        import io

        from tools.adg.adg_test_selector import _cli

        err_buf = io.StringIO()
        with (
            patch(
                "tools.adg.adg_redis_query.ADGRedisClient.ping",
                side_effect=RuntimeError("ADG Redis cache is not loaded"),
            ),
            patch("sys.argv", ["adg_test_selector", "some_file.py"]),
            redirect_stderr(err_buf),
        ):
            with pytest.raises(SystemExit) as exc_info:
                _cli()
        assert exc_info.value.code == 1
        assert "Traceback" not in err_buf.getvalue()

    def test_error_message_mentions_adg_redis(self):
        """The clean error message must identify the problem clearly."""
        import io

        import redis as _redis

        from tools.adg.adg_redis_query import _cli

        err_buf = io.StringIO()
        with (
            patch(
                "tools.adg.adg_redis_query.ADGRedisClient.ping",
                side_effect=_redis.ConnectionError("Connection refused"),
            ),
            patch("sys.argv", ["adg_redis_query", "meta"]),
            redirect_stderr(err_buf),
        ):
            with pytest.raises(SystemExit):
                _cli()
        assert "ERROR" in err_buf.getvalue(), "Error message must start with ERROR: ..."


# ===========================================================================
# 6. ADGQuerySession context manager
# ===========================================================================


class TestADGQuerySession:
    """ADGQuerySession must assert freshness on __enter__; fail-closed by default.

    Uses create_autospec(ADGStalenessChecker) so that assert_fresh / warn_if_stale
    are properly spec'd mock methods (avoiding MagicMock's assert_* AttributeError).
    """

    def _make_checker_mock(self):
        """Return an autospec'd ADGStalenessChecker instance mock."""
        from tools.adg.adg_stale_guard import ADGStalenessChecker

        return create_autospec(ADGStalenessChecker, instance=True)

    def test_query_session_calls_assert_fresh_on_enter(self):
        """__enter__ must invoke assert_fresh() when warn_only=False."""
        from tools.adg.adg_redis_query import ADGQuerySession

        mock_client = MagicMock()
        mock_checker = self._make_checker_mock()

        with patch(
            "tools.adg.adg_stale_guard.ADGStalenessChecker",
            return_value=mock_checker,
        ):
            session = ADGQuerySession(warn_only=False, client=mock_client)
            returned_client = session.__enter__()

        mock_checker.assert_fresh.assert_called_once()
        mock_checker.warn_if_stale.assert_not_called()
        assert returned_client is mock_client

    def test_query_session_calls_warn_if_stale_in_warn_mode(self):
        """__enter__ must invoke warn_if_stale() when warn_only=True."""
        from tools.adg.adg_redis_query import ADGQuerySession

        mock_client = MagicMock()
        mock_checker = self._make_checker_mock()

        with patch(
            "tools.adg.adg_stale_guard.ADGStalenessChecker",
            return_value=mock_checker,
        ):
            session = ADGQuerySession(warn_only=True, client=mock_client)
            session.__enter__()

        mock_checker.warn_if_stale.assert_called_once()
        mock_checker.assert_fresh.assert_not_called()

    def test_query_session_propagates_stale_error(self):
        """assert_fresh() raising RuntimeError must propagate out of __enter__."""
        from tools.adg.adg_redis_query import ADGQuerySession

        mock_client = MagicMock()
        mock_checker = self._make_checker_mock()
        mock_checker.assert_fresh.side_effect = RuntimeError("ADG is stale")

        with patch(
            "tools.adg.adg_stale_guard.ADGStalenessChecker",
            return_value=mock_checker,
        ):
            session = ADGQuerySession(warn_only=False, client=mock_client)
            with pytest.raises(RuntimeError, match="ADG is stale"):
                session.__enter__()

    def test_query_session_context_manager_returns_client(self):
        """The with-block variable must be the ADGRedisClient instance."""
        from tools.adg.adg_redis_query import ADGQuerySession

        mock_client = MagicMock()
        mock_checker = self._make_checker_mock()

        with patch(
            "tools.adg.adg_stale_guard.ADGStalenessChecker",
            return_value=mock_checker,
        ):
            session = ADGQuerySession(warn_only=True, client=mock_client)
            with session as adg:
                assert adg is mock_client


# ===========================================================================
# 7. Pre-commit T3h contract
# ===========================================================================


class TestPreCommitT3hContract:
    """Verify the T3h grep-ban hook is correctly registered."""

    def _cfg(self) -> str:
        return PRE_COMMIT_CFG.read_text(encoding="utf-8")

    def test_t3h_hook_exists(self):
        assert "adg-grep-ban-gate" in self._cfg(), (
            "T3h hook 'adg-grep-ban-gate' must be in .pre-commit-config.yaml"
        )

    def test_t3h_entry_uses_staged_flag(self):
        assert "adg_grep_ban_gate.py --staged" in self._cfg(), (
            "T3h hook entry must use --staged to scan only staged Python files"
        )

    def test_t3h_hook_is_hard_fail(self):
        """T3h must NOT have always_run: true — only runs when Python files change."""
        cfg = self._cfg()
        idx = cfg.find("adg-grep-ban-gate")
        block = cfg[idx : idx + 500]
        assert "always_run: true" not in block, (
            "T3h grep-ban gate must not be always_run — it only matters when .py files change"
        )

    def test_t3h_appears_after_t3g_stale_guard(self):
        """T3h must appear after T3g (stale guard runs first)."""
        cfg = self._cfg()
        t3g_pos = cfg.find("adg-stale-guard")
        t3h_pos = cfg.find("adg-grep-ban-gate")
        assert t3g_pos != -1 and t3h_pos != -1
        assert t3g_pos < t3h_pos, "T3h grep-ban must appear after T3g stale-guard in .pre-commit-config.yaml"


# ===========================================================================
# 8. CI workflow contract for grep-ban
# ===========================================================================


class TestGrepBanCIWorkflow:
    """adg-grep-ban-ci.yml must exist, be valid YAML, and scan all Python files."""

    def _load(self) -> str:
        assert CI_WF.exists(), f"CI workflow missing: {CI_WF}"
        return CI_WF.read_text(encoding="utf-8")

    def test_ci_workflow_exists(self):
        assert CI_WF.exists()

    def test_ci_workflow_is_valid_yaml(self):
        import importlib.util

        text = self._load()
        if importlib.util.find_spec("yaml"):
            import yaml

            data = yaml.safe_load(text)
            assert isinstance(data, dict)
        else:
            assert "name:" in text and "jobs:" in text

    def test_ci_workflow_uses_all_python_flag(self):
        assert "--all-python" in self._load(), (
            "CI workflow must use --all-python to scan the entire codebase, not just staged files"
        )

    def test_ci_workflow_calls_grep_ban_gate(self):
        assert "adg_grep_ban_gate.py" in self._load()

    def test_ci_workflow_triggers_on_python_files(self):
        text = self._load()
        assert "**.py" in text or "*.py" in text
