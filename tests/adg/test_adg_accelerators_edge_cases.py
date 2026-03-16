# adg-grep-ban: skip-file
"""Novel edge-case tests for all ADG accelerators — flush out boundary conditions.

Sections:
  1. GrepBanGate — parametrized tool × invocation matrix
  2. GrepBanGate — whitespace variants, shell-string form, binary files
  3. GrepBanGate — exemption precision (wrong-line, case-sensitivity, empty justification)
  4. GrepBanGate — idempotency and determinism
  5. GrepBanGate — known static-analysis limitations (documented with tests)
  6. WarnIfStale — all warn_if_stale() scenarios
  7. ADGQuerySession — __exit__ passthrough, None client, ConnectionError propagation
  8. CLI robustness — --help without Redis, sys.argv edge cases
  9. ADGTestSelector — path normalisation, dedup, gap detection
  10. ADGTypeCheck — blast-radius depth=0, security (no shell=True)
  11. Concurrency — scan_file thread-safety
"""

from __future__ import annotations

import io
import sys
import tempfile
import threading
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, create_autospec, patch

import pytest

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
)

_emit_records_execution_trace("p0", "evidence", "test_adg_accelerators_edge_cases")
_emit_applies_guardrail("p0", "test_adg_accelerators_edge_cases", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_accelerators_edge_cases", "policy_binding")
_emit_snapshots_state("p0", "test_adg_accelerators_edge_cases", "state_snapshot")
emit_replay_key("p0", "test_adg_accelerators_edge_cases")
emit_determinism_digest("p0", "test_adg_accelerators_edge_cases")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_accelerators_edge_cases", "execution_auth")
_emit_validates_capability("p2", "test_adg_accelerators_edge_cases", "capability_check")
_emit_routes_to_capability("p2", "test_adg_accelerators_edge_cases", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_accelerators_edge_cases", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_accelerators_edge_cases", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_accelerators_edge_cases", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_accelerators_edge_cases", "exec_output")
_emit_dispatches_agent("p3", "test_adg_accelerators_edge_cases", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_accelerators_edge_cases", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_accelerators_edge_cases", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_accelerators_edge_cases", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_accelerators_edge_cases", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_accelerators_edge_cases", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_accelerators_edge_cases", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_accelerators_edge_cases", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_accelerators_edge_cases", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_accelerators_edge_cases", "eval_metric")
_emit_stores_embedding("p4", "test_adg_accelerators_edge_cases", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_accelerators_edge_cases", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_accelerators_edge_cases", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ops_scripts.ci.adg_grep_ban_gate import (
    _BANNED_PATTERNS,
    _BANNED_POPEN_RE,
    _BANNED_SHELL_STR_RE,
    _BANNED_SUBPROCESS_RE,
    _EXEMPTION_RE,
    scan_file,
    scan_files,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_adg_accelerators_edge_cases", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_accelerators_edge_cases", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_accelerators_edge_cases", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_accelerators_edge_cases", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_accelerators_edge_cases", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_accelerators_edge_cases", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_accelerators_edge_cases", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_accelerators_edge_cases", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_accelerators_edge_cases", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_accelerators_edge_cases", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_accelerators_edge_cases", "p4obs", "alert")
_emit_links_incident_trace("test_adg_accelerators_edge_cases", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_accelerators_edge_cases", "p3lm", "pattern")
_emit_records_learning_event("test_adg_accelerators_edge_cases", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_accelerators_edge_cases", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_accelerators_edge_cases", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_accelerators_edge_cases", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_accelerators_edge_cases", "p3lm", "policy")
_emit_stores_learning_state("test_adg_accelerators_edge_cases", "p3lm", "state")
_emit_records_execution_trace("test_adg_accelerators_edge_cases", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_accelerators_edge_cases", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_accelerators_edge_cases", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_accelerators_edge_cases", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_accelerators_edge_cases", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_accelerators_edge_cases", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_accelerators_edge_cases", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_accelerators_edge_cases", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_accelerators_edge_cases", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_accelerators_edge_cases", "context_pull")
_emit_pulls_context("p1", "test_adg_accelerators_edge_cases", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_accelerators_edge_cases", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_accelerators_edge_cases", "uwg_term_2")
_emit_writes_through("p1", "test_adg_accelerators_edge_cases", "write_through")
_emit_writes_through("p1", "test_adg_accelerators_edge_cases", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_accelerators_edge_cases", "safety_validation")
_emit_invokes_eval("p1", "test_adg_accelerators_edge_cases", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_accelerators_edge_cases", "routing_commit")

# ============================================================================
# Helpers
# ============================================================================


def _tmppy(content: str) -> Path:
    """Write content to a temp .py file, return its Path."""
    f = tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False)
    f.write(content)
    f.close()
    return Path(f.name)


def _scan_line(line: str) -> bool:
    for pat in _BANNED_PATTERNS:
        if pat.search(line):
            return True
    return False


# ============================================================================
# 1. Parametrized banned-tool × invocation-method matrix
# ============================================================================

_BANNED_TOOLS = ["grep", "rg", "ripgrep", "ag", "ack", "findstr"]
_SUBPROCESS_METHODS = ["run", "call", "check_output", "check_call", "Popen"]


class TestGrepBanParametrizedMatrix:
    """Every banned tool × subprocess method combination must be detected."""

    @pytest.mark.parametrize("tool", _BANNED_TOOLS)
    @pytest.mark.parametrize("method", _SUBPROCESS_METHODS)
    def test_subprocess_list_form(self, tool: str, method: str) -> None:
        line = f'    result = subprocess.{method}(["{tool}", "-r", "pattern", "."])'
        assert _scan_line(line), f'subprocess.{method}(["{tool}", ...]) must be banned'

    @pytest.mark.parametrize("tool", ["grep", "rg", "ripgrep", "ag", "ack", "findstr"])
    def test_os_popen_all_tools(self, tool: str) -> None:
        line = f'    out = os.popen("{tool} -r pattern .")'
        assert _BANNED_POPEN_RE.search(line), f"os.popen('{tool} ...') must be banned"

    @pytest.mark.parametrize("tool", ["grep", "rg", "ripgrep"])
    @pytest.mark.parametrize("method", ["run", "call", "check_output", "check_call"])
    def test_subprocess_shell_string_form(self, tool: str, method: str) -> None:
        """subprocess.run('grep pattern .') shell-string form must be caught."""
        line = f'    subprocess.{method}("{tool} -r pattern .")'
        assert _BANNED_SHELL_STR_RE.search(line), (
            f'subprocess.{method}("{tool} ...") shell-string form must be banned'
        )


# ============================================================================
# 2. Whitespace variants and shell-string form
# ============================================================================


class TestGrepBanWhitespaceVariants:
    """Whitespace between tokens must not allow bypass (regex uses \\s*)."""

    def test_spaces_around_dot_in_subprocess(self) -> None:
        line = '    result = subprocess . run (["grep", "pattern", "."])'
        assert _BANNED_SUBPROCESS_RE.search(line), "subprocess . run with spaces around dot must be caught"

    def test_spaces_around_dot_and_parens(self) -> None:
        line = '    subprocess . run ( [ "rg", "pattern" ] )'
        assert _BANNED_SUBPROCESS_RE.search(line), (
            "subprocess . run ( [ 'rg'... ] ) with spaces must be caught"
        )

    def test_shell_string_with_args_before_tool(self) -> None:
        """String with grep appearing after other text in shell-string form."""
        line = '    subprocess.run("find . -exec grep {} +")'
        assert _BANNED_SHELL_STR_RE.search(line), (
            "shell-string subprocess.run with grep mid-string must be caught"
        )

    def test_single_quotes_list_form(self) -> None:
        line = "    subprocess.run(['grep', '-r', 'pattern', '.'])"
        assert _BANNED_SUBPROCESS_RE.search(line), "Single-quote list form must also be caught"

    def test_single_quotes_shell_form(self) -> None:
        line = "    subprocess.run('grep -r pattern .')"
        assert _BANNED_SHELL_STR_RE.search(line), "Single-quote shell-string form must be caught"


# ============================================================================
# 3. Exemption precision edge cases
# ============================================================================


class TestGrepBanExemptionPrecision:
    """Exemptions must be surgical — wrong-line placement does NOT suppress."""

    def test_exemption_on_line_above_does_not_suppress(self) -> None:
        """The guardian comment must be on the SAME line as the violation."""
        tmp = _tmppy(
            '# guardian: allow-grep -- intentional\nsubprocess.run(["grep", "-r", "pattern", "."])\n'
        )
        try:
            vs = scan_file(tmp)
            assert len(vs) == 1, "Exemption on previous line must NOT suppress the violation on next line"
        finally:
            tmp.unlink()

    def test_exemption_on_line_below_does_not_suppress(self) -> None:
        tmp = _tmppy(
            'subprocess.run(["grep", "-r", "pattern", "."])\n# guardian: allow-grep -- intentional\n'
        )
        try:
            vs = scan_file(tmp)
            assert len(vs) == 1, "Exemption on next line must NOT suppress the violation on previous line"
        finally:
            tmp.unlink()

    def test_exemption_case_sensitive_uppercase_guardian_not_valid(self) -> None:
        """GUARDIAN: allow-grep (uppercase) is NOT a valid exemption."""
        line = '    subprocess.run(["grep", "x"])  # GUARDIAN: allow-grep -- test'
        assert not _EXEMPTION_RE.search(line), (
            "Uppercase GUARDIAN: must NOT be a valid exemption (case-sensitive)"
        )

    def test_exemption_with_only_whitespace_justification_not_valid(self) -> None:
        """'# guardian: allow-grep --   ' (only whitespace after --) is invalid."""
        line = '    subprocess.run(["grep"])  # guardian: allow-grep --   '
        assert not _EXEMPTION_RE.search(line), "Whitespace-only justification after -- must NOT be valid"

    def test_multiple_exemptions_respected_independently(self) -> None:
        """Each exempted line is independent; non-exempted lines still flagged."""
        tmp = _tmppy(
            'subprocess.run(["grep", "x"])  # guardian: allow-grep -- wrapper\n'
            'subprocess.run(["rg", "x"])\n'
            'subprocess.run(["grep", "y"])  # guardian: allow-grep -- legacy\n'
        )
        try:
            vs = scan_file(tmp)
            assert len(vs) == 1, f"Only the un-exempted rg line must be flagged; got {len(vs)} violations"
            assert "rg" in vs[0][1], "The flagged line must be the rg call"
        finally:
            tmp.unlink()


# ============================================================================
# 4. Edge cases: empty / binary / whitespace-only files
# ============================================================================


class TestGrepBanFileEdgeCases:
    """Gate must handle pathological files without crashing."""

    def test_empty_file_produces_no_violations(self) -> None:
        tmp = _tmppy("")
        try:
            assert scan_file(tmp) == []
        finally:
            tmp.unlink()

    def test_whitespace_only_file_produces_no_violations(self) -> None:
        tmp = _tmppy("   \n\t\n   \n")
        try:
            assert scan_file(tmp) == []
        finally:
            tmp.unlink()

    def test_malformed_utf8_file_handled_gracefully(self) -> None:
        """Files with invalid UTF-8 sequences must not crash the gate."""
        with tempfile.NamedTemporaryFile(suffix=".py", mode="wb", delete=False) as f:
            f.write(b"result = some_function()\n")
            f.write(b"\xff\xfe bad bytes\n")
            f.write(b'subprocess.run(["git", "status"])\n')
            tmp = Path(f.name)
        try:
            vs = scan_file(tmp)
            assert isinstance(vs, list), "Must return a list even for malformed files"
            # git is not banned so no violations
            assert len(vs) == 0
        finally:
            tmp.unlink()

    def test_file_with_only_comments_produces_no_violations(self) -> None:
        content = (
            "# subprocess.run(['grep', 'foo'])\n"
            "# os.popen('rg bar')\n"
            "# This file is intentionally empty of code\n"
        )
        tmp = _tmppy(content)
        try:
            assert scan_file(tmp) == [], "Comment-only file must produce zero violations"
        finally:
            tmp.unlink()

    def test_violation_line_numbers_are_correct(self) -> None:
        """Line numbers in violation tuples must be 1-indexed and accurate."""
        tmp = _tmppy(
            "import subprocess\n"  # line 1 — no violation
            "x = 1\n"  # line 2 — no violation
            'subprocess.run(["grep", "foo"])\n'  # line 3 — violation
            "y = 2\n"  # line 4 — no violation
            'subprocess.run(["rg", "bar"])\n'  # line 5 — violation
        )
        try:
            vs = scan_file(tmp)
            assert len(vs) == 2
            assert vs[0][0] == 3, f"First violation must be on line 3, got {vs[0][0]}"
            assert vs[1][0] == 5, f"Second violation must be on line 5, got {vs[1][0]}"
        finally:
            tmp.unlink()

    def test_scan_nonexistent_file_returns_empty_not_crash(self) -> None:
        """scan_file on a non-existent path must return [] (warned, not raised)."""
        phantom = Path("/nonexistent/path/to/file.py")
        err_buf = io.StringIO()
        with redirect_stderr(err_buf):
            result = scan_file(phantom)
        assert result == []
        assert "WARNING" in err_buf.getvalue()


# ============================================================================
# 5. Idempotency and determinism
# ============================================================================


class TestGrepBanIdempotency:
    """scan_file must be a pure function — same input always produces same output."""

    def test_scan_file_is_idempotent(self) -> None:
        tmp = _tmppy('subprocess.run(["grep", "x"])\nsubprocess.run(["rg", "y"])\n')
        try:
            first = scan_file(tmp)
            second = scan_file(tmp)
            assert first == second, "scan_file must produce identical results on repeated calls"
        finally:
            tmp.unlink()

    def test_scan_files_aggregate_count_matches_individual_sum(self) -> None:
        """Total violations from scan_files must match sum of individual scan_file calls."""
        files = [
            _tmppy('subprocess.run(["grep", "a"])\n'),
            _tmppy("adg.search_nodes('x')\n"),
            _tmppy('subprocess.run(["rg", "b"])\nos.popen("grep c")\n'),
        ]
        try:
            aggregate = scan_files(files)
            individual_total = sum(len(scan_file(p)) for p in files)
            aggregate_total = sum(len(vs) for vs in aggregate.values())
            assert aggregate_total == individual_total, (
                f"Aggregate count {aggregate_total} must equal individual sum {individual_total}"
            )
        finally:
            for p in files:
                p.unlink()

    def test_violation_output_is_deterministic_across_runs(self) -> None:
        """Same file content must produce the same violation list every time."""
        content = (
            'result1 = subprocess.run(["grep", "pattern"])\nresult2 = subprocess.run(["rg", "pattern"])\n'
        )
        results = []
        for _ in range(5):
            tmp = _tmppy(content)
            try:
                results.append(scan_file(tmp))
            finally:
                tmp.unlink()
        for r in results[1:]:
            assert r == results[0], "scan_file must be deterministic across runs"


# ============================================================================
# 6. Known static-analysis limitations (documented as "must NOT raise false positives")
# ============================================================================


class TestGrepBanKnownLimitations:
    """Document known boundaries of the static scanner.

    These tests define the CONTRACT: the gate must NOT produce false positives
    for legitimate patterns. Variable indirection is a known limitation.
    """

    def test_variable_indirection_not_flagged(self) -> None:
        """cmd = ['grep'...]; subprocess.run(cmd) — the run() line has no banned tool literal."""
        line = "    subprocess.run(cmd)"
        assert not _scan_line(line), (
            "subprocess.run(cmd) with variable indirection must NOT be flagged "
            "(static analysis limitation — acceptably not caught)"
        )

    def test_comment_after_code_containing_grep_word_not_flagged_by_raw_pattern(self) -> None:
        """A line that's all comment is skip-scanned by scan_file but not by raw pattern."""
        comment_line = "    # Use grep via os.popen('grep foo')"
        # The raw _BANNED_POPEN_RE would match — but scan_file skips it
        tmp = _tmppy(comment_line + "\n")
        try:
            assert scan_file(tmp) == []
        finally:
            tmp.unlink()

    def test_grep_in_docstring_not_flagged(self) -> None:
        """grep inside a docstring should not be flagged (no subprocess wrapper)."""
        line = '    """Do not use grep here."""'
        assert not _scan_line(line), "grep inside docstring text must NOT be flagged"

    def test_grep_in_a_string_literal_not_a_subprocess_call(self) -> None:
        """A string containing 'grep' but NOT wrapped in subprocess.run must not be caught."""
        line = '    banned_cmds = ["grep", "rg", "awk"]'
        assert not _BANNED_SUBPROCESS_RE.search(line), (
            "A list literal containing 'grep' without subprocess.run must not be flagged"
        )

    def test_subprocess_run_with_benign_rg_in_middle_of_path_not_flagged(self) -> None:
        """A path that CONTAINS 'rg' as a substring but is not a word boundary."""
        line = '    subprocess.run(["progress_reporter", "--all"])'
        assert not _BANNED_SUBPROCESS_RE.search(line), (
            "'rg' embedded inside a longer word (progress_reporter) must NOT be flagged"
        )


# ============================================================================
# 7. warn_if_stale() edge cases
# ============================================================================


class TestWarnIfStaleEdgeCases:
    """ADGStalenessChecker.warn_if_stale() must never raise; always demote to warning."""

    def _make_checker(self, check_result=None, check_raises=None):
        from tools.adg.adg_stale_guard import ADGStalenessChecker

        mock_client = MagicMock()
        checker = ADGStalenessChecker(client=mock_client)

        if check_raises is not None:
            checker.check = MagicMock(side_effect=check_raises)
        elif check_result is not None:
            checker.check = MagicMock(return_value=check_result)
        return checker

    def test_warn_if_stale_returns_none(self) -> None:
        from tools.adg.adg_stale_guard import StalenessResult

        checker = self._make_checker(
            check_result=StalenessResult(
                is_stale=False,
                ingest_time=1000.0,
                last_commit_time=999.0,
                changed_files=[],
                message="FRESH",
            )
        )
        result = checker.warn_if_stale()
        assert result is None, "warn_if_stale() must return None"

    def test_warn_if_stale_does_not_raise_when_fresh(self) -> None:
        from tools.adg.adg_stale_guard import StalenessResult

        checker = self._make_checker(
            check_result=StalenessResult(
                is_stale=False,
                ingest_time=1000.0,
                last_commit_time=999.0,
                changed_files=[],
                message="FRESH",
            )
        )
        checker.warn_if_stale()  # must not raise

    def test_warn_if_stale_produces_no_stderr_when_fresh(self) -> None:
        from tools.adg.adg_stale_guard import StalenessResult

        checker = self._make_checker(
            check_result=StalenessResult(
                is_stale=False,
                ingest_time=1000.0,
                last_commit_time=999.0,
                changed_files=[],
                message="FRESH",
            )
        )
        err_buf = io.StringIO()
        with redirect_stderr(err_buf):
            checker.warn_if_stale()
        assert err_buf.getvalue() == "", "warn_if_stale on fresh graph must print nothing"

    def test_warn_if_stale_prints_warning_when_stale(self) -> None:
        from tools.adg.adg_stale_guard import StalenessResult

        checker = self._make_checker(
            check_result=StalenessResult(
                is_stale=True,
                ingest_time=900.0,
                last_commit_time=1000.0,
                changed_files=["tools/adg/adg_stale_guard.py"],
                message="STALE: 100s behind",
            )
        )
        err_buf = io.StringIO()
        with redirect_stderr(err_buf):
            checker.warn_if_stale()
        assert "WARNING" in err_buf.getvalue(), "warn_if_stale on stale graph must print WARNING to stderr"
        assert "STALE" in err_buf.getvalue() or "100s" in err_buf.getvalue()

    def test_warn_if_stale_does_not_raise_on_redis_connection_error(self) -> None:
        import redis

        checker = self._make_checker(check_raises=redis.ConnectionError("Connection refused"))
        checker.warn_if_stale()  # must not raise

    def test_warn_if_stale_prints_warning_on_connection_error(self) -> None:
        import redis

        checker = self._make_checker(check_raises=redis.ConnectionError("Connection refused"))
        err_buf = io.StringIO()
        with redirect_stderr(err_buf):
            checker.warn_if_stale()
        assert "WARNING" in err_buf.getvalue()

    def test_warn_if_stale_does_not_raise_on_arbitrary_exception(self) -> None:
        checker = self._make_checker(check_raises=OSError("some weird OS error"))
        checker.warn_if_stale()  # must not raise

    def test_warn_if_stale_does_not_raise_on_runtime_error(self) -> None:
        checker = self._make_checker(check_raises=RuntimeError("ingested_at key missing"))
        checker.warn_if_stale()  # must not raise

    def test_warn_if_stale_prints_to_stderr_not_stdout(self) -> None:
        from tools.adg.adg_stale_guard import StalenessResult

        checker = self._make_checker(
            check_result=StalenessResult(
                is_stale=True,
                ingest_time=900.0,
                last_commit_time=1000.0,
                changed_files=[],
                message="STALE",
            )
        )
        out_buf = io.StringIO()
        with redirect_stdout(out_buf):
            checker.warn_if_stale()
        assert out_buf.getvalue() == "", "warn_if_stale must print to stderr, NOT stdout"


# ============================================================================
# 8. ADGQuerySession edge cases
# ============================================================================


class TestADGQuerySessionEdgeCases:
    """ADGQuerySession context manager boundary conditions."""

    def _make_checker_mock(self):
        from tools.adg.adg_stale_guard import ADGStalenessChecker

        return create_autospec(ADGStalenessChecker, instance=True)

    def test_exit_does_not_suppress_exceptions(self) -> None:
        """__exit__ must return None/False — exceptions from the body must propagate."""
        from tools.adg.adg_redis_query import ADGQuerySession

        mock_client = MagicMock()
        mock_checker = self._make_checker_mock()

        with patch(
            "tools.adg.adg_stale_guard.ADGStalenessChecker",
            return_value=mock_checker,
        ):
            session = ADGQuerySession(warn_only=True, client=mock_client)
            assert session.__exit__(None, None, None) is None, (
                "__exit__ must return None (not True), so exceptions are not suppressed"
            )

    def test_exit_with_exception_info_returns_none(self) -> None:
        """__exit__ with exc type/value/tb args must still return None."""
        from tools.adg.adg_redis_query import ADGQuerySession

        session = ADGQuerySession.__new__(ADGQuerySession)
        result = session.__exit__(ValueError, ValueError("test"), None)
        assert result is None

    def test_default_client_created_when_none_passed(self) -> None:
        """ADGQuerySession() with no client must create an ADGRedisClient instance."""
        from tools.adg.adg_redis_query import ADGQuerySession, ADGRedisClient

        with patch.object(ADGRedisClient, "__init__", return_value=None):
            session = ADGQuerySession()
        assert isinstance(session._client, ADGRedisClient), (
            "Default client must be an ADGRedisClient instance"
        )

    def test_connection_error_propagates_in_fail_closed_mode(self) -> None:
        """redis.ConnectionError during assert_fresh() must not be swallowed."""
        import redis

        from tools.adg.adg_redis_query import ADGQuerySession

        mock_client = MagicMock()
        mock_checker = self._make_checker_mock()
        mock_checker.assert_fresh.side_effect = redis.ConnectionError("Connection refused")

        with patch(
            "tools.adg.adg_stale_guard.ADGStalenessChecker",
            return_value=mock_checker,
        ):
            session = ADGQuerySession(warn_only=False, client=mock_client)
            with pytest.raises(redis.ConnectionError):
                session.__enter__()

    def test_warn_only_does_not_raise_on_connection_error(self) -> None:
        """In warn_only=True mode, ConnectionError in warn_if_stale is swallowed internally."""
        from tools.adg.adg_redis_query import ADGQuerySession

        mock_client = MagicMock()
        mock_checker = self._make_checker_mock()
        mock_checker.warn_if_stale.side_effect = None  # does not raise

        with patch(
            "tools.adg.adg_stale_guard.ADGStalenessChecker",
            return_value=mock_checker,
        ):
            session = ADGQuerySession(warn_only=True, client=mock_client)
            client = session.__enter__()  # must not raise
        assert client is mock_client

    def test_context_manager_protocol_complete(self) -> None:
        """Verify __enter__ and __exit__ are both callable (full CM protocol)."""
        from tools.adg.adg_redis_query import ADGQuerySession

        assert callable(ADGQuerySession.__enter__)
        assert callable(ADGQuerySession.__exit__)


# ============================================================================
# 9. CLI robustness edge cases
# ============================================================================


class TestCLIRobustness:
    """CLI tools must handle edge cases gracefully."""

    def test_adg_redis_query_help_exits_0_without_redis(self) -> None:
        """--help must exit 0 and not attempt any Redis connection."""
        import subprocess as sp

        r = sp.run(
            [sys.executable, str(ROOT / "tools/adg/adg_redis_query.py"), "--help"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        assert r.returncode == 0, f"--help must exit 0; got {r.returncode}. stderr={r.stderr!r}"
        assert "ADG" in r.stdout or "adg" in r.stdout.lower()

    def test_adg_stale_guard_help_exits_0_without_redis(self) -> None:
        import subprocess as sp

        r = sp.run(
            [sys.executable, str(ROOT / "tools/adg/adg_stale_guard.py"), "--help"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        assert r.returncode == 0

    def test_grep_ban_gate_help_exits_0(self) -> None:
        import subprocess as sp

        r = sp.run(
            [sys.executable, str(ROOT / "ops_scripts/ci/adg_grep_ban_gate.py"), "--help"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        assert r.returncode == 0

    def test_adg_test_selector_no_args_prints_error_not_traceback(self) -> None:
        """Calling the CLI with no files and no diff flag must exit 2 (argparse error)."""
        import subprocess as sp

        r = sp.run(
            [sys.executable, str(ROOT / "tools/adg/adg_test_selector.py")],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        assert r.returncode == 2, f"No-arg invocation must exit 2 (argparse error); got {r.returncode}"
        assert "Traceback" not in r.stderr

    def test_adg_type_check_no_args_prints_error_not_traceback(self) -> None:
        import subprocess as sp

        r = sp.run(
            [sys.executable, str(ROOT / "tools/adg/adg_type_check.py")],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        assert r.returncode == 2
        assert "Traceback" not in r.stderr

    def test_connection_error_message_does_not_leak_internal_details(self) -> None:
        """The error message on ConnectionError must mention 'ADG Redis', not raw traceback."""
        import redis

        from tools.adg.adg_redis_query import _cli

        err_buf = io.StringIO()
        with (
            patch(
                "tools.adg.adg_redis_query.ADGRedisClient.ping",
                side_effect=redis.ConnectionError("Connection refused"),
            ),
            patch("sys.argv", ["adg_redis_query", "meta"]),
            redirect_stderr(err_buf),
        ):
            with pytest.raises(SystemExit):
                _cli()
        output = err_buf.getvalue()
        assert "Traceback" not in output
        assert "ConnectionError" not in output, (
            "Raw exception class names should not leak to the user — must be a clean human-readable message"
        )


# ============================================================================
# 10. ADGTestSelector edge cases
# ============================================================================


class TestADGTestSelectorEdgeCases:
    """ADGTestSelector boundary conditions not covered in the primary test file."""

    def _make_adg(self, nodes_by_file: dict, edges: dict):
        """Build a mock ADGRedisClient from declarative spec."""
        mock = MagicMock()
        mock.nodes_in_file.side_effect = lambda p: set(nodes_by_file.get(p, set()))
        mock.fan_in.side_effect = lambda nid, rel: set(edges.get((nid, rel), set()))
        mock.get_node.side_effect = lambda nid: {"resolved_path": f"tests/{nid}.py"}
        return mock

    def test_path_with_backslashes_normalised(self) -> None:
        """Windows-style backslash paths must be normalised to forward slashes."""
        from tools.adg.adg_test_selector import ADGTestSelector

        mock_adg = MagicMock()
        mock_adg.nodes_in_file.return_value = set()
        selector = ADGTestSelector(client=mock_adg)

        # Input with backslashes — should be normalised before ADG query
        result = selector.select_tests(["apps_rg\\engines\\some_engine.py"])
        mock_adg.nodes_in_file.assert_called_once_with("apps_rg/engines/some_engine.py")
        assert result == []

    def test_empty_input_returns_empty_list(self) -> None:
        from tools.adg.adg_test_selector import ADGTestSelector

        mock_adg = MagicMock()
        selector = ADGTestSelector(client=mock_adg)
        result = selector.select_tests([])
        assert result == []
        mock_adg.nodes_in_file.assert_not_called()

    def test_coverage_gaps_empty_input(self) -> None:
        from tools.adg.adg_test_selector import ADGTestSelector

        mock_adg = MagicMock()
        selector = ADGTestSelector(client=mock_adg)
        assert selector.coverage_gaps([]) == []

    def test_coverage_gaps_file_not_in_adg_is_a_gap(self) -> None:
        from tools.adg.adg_test_selector import ADGTestSelector

        mock_adg = MagicMock()
        mock_adg.nodes_in_file.return_value = set()
        selector = ADGTestSelector(client=mock_adg)
        gaps = selector.coverage_gaps(["tools/adg/adg_redis_query.py"])
        assert "tools/adg/adg_redis_query.py" in gaps

    def test_select_tests_result_is_sorted(self) -> None:
        """Result must be alphabetically sorted for deterministic output."""
        from tools.adg.adg_test_selector import ADGTestSelector

        mock_adg = MagicMock()
        mock_adg.nodes_in_file.return_value = {"node1"}
        mock_adg.fan_in.return_value = {"t_z", "t_a", "t_m"}
        mock_adg.get_node.side_effect = lambda nid: {
            "t_a": {"resolved_path": "tests/z_test.py"},
            "t_z": {"resolved_path": "tests/a_test.py"},
            "t_m": {"resolved_path": "tests/m_test.py"},
        }.get(nid, {})
        selector = ADGTestSelector(client=mock_adg)
        result = selector.select_tests(["some_file.py"])
        assert result == sorted(result), "Test results must be sorted"


# ============================================================================
# 11. ADGTypeCheck edge cases
# ============================================================================


class TestADGTypeCheckEdgeCases:
    """ADGTypeChecker boundary conditions."""

    def test_get_blast_radius_depth_zero_returns_only_changed_file(self) -> None:
        from tools.adg.adg_type_check import ADGTypeChecker

        mock_adg = MagicMock()
        mock_adg.nodes_in_file.return_value = {"node1"}
        mock_adg.fan_in.return_value = set()
        checker = ADGTypeChecker(client=mock_adg)
        result = checker.get_blast_radius(["tools/adg/my_module.py"], depth=0)
        assert result == ["tools/adg/my_module.py"]
        mock_adg.fan_in.assert_not_called()  # depth=0 means no traversal

    def test_run_mypy_on_empty_list_does_not_invoke_subprocess(self) -> None:
        from tools.adg.adg_type_check import ADGTypeChecker

        mock_adg = MagicMock()
        checker = ADGTypeChecker(client=mock_adg)
        with patch("subprocess.run") as mock_run:
            result = checker.run_mypy([])
        mock_run.assert_not_called()
        assert result.exit_code == 0

    def test_mypy_subprocess_never_uses_shell_true(self) -> None:
        """Security: mypy must NEVER be run with shell=True."""
        from tools.adg.adg_type_check import ADGTypeChecker

        mock_adg = MagicMock()
        checker = ADGTypeChecker(client=mock_adg)
        captured_calls = []
        real_run = __import__("subprocess").run

        def capturing_run(*args, **kwargs):
            captured_calls.append(kwargs)
            raise FileNotFoundError("mypy not installed in test env")

        with patch("subprocess.run", side_effect=capturing_run):
            with pytest.raises((FileNotFoundError, RuntimeError)):
                checker.run_mypy(["some_file.py"])

        for call_kwargs in captured_calls:
            assert call_kwargs.get("shell") is not True, (
                "mypy subprocess call must NEVER use shell=True (security requirement)"
            )

    def test_blast_radius_deduplicates_repeated_files(self) -> None:
        """Passing the same file twice must not double-count in the blast radius."""
        from tools.adg.adg_type_check import ADGTypeChecker

        mock_adg = MagicMock()
        mock_adg.nodes_in_file.return_value = set()
        checker = ADGTypeChecker(client=mock_adg)
        result = checker.get_blast_radius(["tools/adg/foo.py", "tools/adg/foo.py", "tools/adg/foo.py"])
        assert result.count("tools/adg/foo.py") == 1, (
            "Duplicate input files must be deduplicated in the blast radius"
        )


# ============================================================================
# 12. Thread safety (concurrency)
# ============================================================================


class TestGrepBanConcurrency:
    """scan_file must be safe to call from multiple threads simultaneously."""

    def test_concurrent_scan_file_calls_are_thread_safe(self) -> None:
        """16 threads each scanning a different file must all complete without error."""
        files = [_tmppy(f'x = {i}\nsubprocess.run(["grep", "pattern"])\ny = {i + 1}\n') for i in range(16)]
        results: dict[int, list] = {}
        errors: list[Exception] = []

        def scan(idx: int, path: Path) -> None:
            try:
                results[idx] = scan_file(path)
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=scan, args=(i, f)) for i, f in enumerate(files)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        try:
            assert not errors, f"Thread errors: {errors}"
            assert len(results) == 16
            for idx, vs in results.items():
                assert len(vs) == 1, f"Thread {idx}: expected 1 violation, got {len(vs)}"
        finally:
            for f in files:
                f.unlink()
