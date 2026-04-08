"""
EXHAUSTIVE tests for post_cascade_cleanup.py (Phase 1.8).

Plan requirements verified:
  - _rotate_log: file > limit → truncated to LAST N lines (oldest dropped)
  - _rotate_log: file = limit → unchanged
  - _rotate_log: file < limit → unchanged
  - _rotate_log: file absent → returns 0, no crash
  - _rotate_log: empty file → returns 0
  - _rotate_log: trailing newline handled correctly
  - _count_lines: absent → 0
  - _count_lines: empty → 0
  - _count_lines: N lines → N
  - run_cleanup: returns dict with timestamp + audit_line_counts
  - run_cleanup: audit_line_counts has all three log keys
  - run_cleanup: rotation applied (spawned_processes: 500, mcp_tool: 500, mcp_lint: 200)
  - run_cleanup: absent logs count as 0
  - run_cleanup: creates windsurf_dir if missing
  - main: always exits 0
  - main: writes session_summary.json with correct structure
  - main: session_summary timestamp is ISO8601
  - main: audit_line_counts present in session_summary
  - main: graceful if WINDSURF_DIR cannot be created (OSError)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from ops_scripts.hooks.windsurf.post_cascade_cleanup import (
    _count_lines,
    _rotate_log,
    main,
    run_cleanup,
)


# ---------------------------------------------------------------------------
# _rotate_log
# ---------------------------------------------------------------------------

class TestRotateLog:
    def test_file_over_limit_truncated_to_last_n(self, tmp_path):
        log = tmp_path / "test.jsonl"
        lines = [f'{{"n": {i}}}' for i in range(600)]
        log.write_text("\n".join(lines) + "\n")
        kept = _rotate_log(log, 500)
        assert kept == 500
        result = log.read_text().strip().splitlines()
        assert len(result) == 500
        # Last 500: indices 100-599
        assert json.loads(result[0])["n"] == 100
        assert json.loads(result[-1])["n"] == 599

    def test_file_at_limit_unchanged(self, tmp_path):
        log = tmp_path / "test.jsonl"
        lines = [f'{{"n": {i}}}' for i in range(500)]
        log.write_text("\n".join(lines) + "\n")
        kept = _rotate_log(log, 500)
        assert kept == 500
        assert len(log.read_text().strip().splitlines()) == 500

    def test_file_under_limit_unchanged(self, tmp_path):
        log = tmp_path / "test.jsonl"
        lines = [f'{{"n": {i}}}' for i in range(50)]
        log.write_text("\n".join(lines) + "\n")
        kept = _rotate_log(log, 500)
        assert kept == 50
        assert len(log.read_text().strip().splitlines()) == 50

    def test_file_one_line_kept(self, tmp_path):
        log = tmp_path / "test.jsonl"
        log.write_text('{"a": 1}\n')
        kept = _rotate_log(log, 500)
        assert kept == 1

    def test_file_absent_returns_zero(self, tmp_path):
        assert _rotate_log(tmp_path / "missing.jsonl", 500) == 0

    def test_empty_file_returns_zero(self, tmp_path):
        log = tmp_path / "empty.jsonl"
        log.write_text("")
        kept = _rotate_log(log, 500)
        assert kept == 0

    def test_file_with_only_whitespace_returns_zero(self, tmp_path):
        log = tmp_path / "ws.jsonl"
        log.write_text("   \n   \n")
        kept = _rotate_log(log, 500)
        assert kept == 0

    def test_limit_of_200_applied_for_lint_log(self, tmp_path):
        log = tmp_path / "lint.jsonl"
        lines = [f'{{"n": {i}}}' for i in range(300)]
        log.write_text("\n".join(lines) + "\n")
        kept = _rotate_log(log, 200)
        assert kept == 200
        result = log.read_text().strip().splitlines()
        assert json.loads(result[0])["n"] == 100

    def test_preserves_content_order_after_rotation(self, tmp_path):
        log = tmp_path / "test.jsonl"
        lines = [f'{{"seq": {i}}}' for i in range(10)]
        log.write_text("\n".join(lines) + "\n")
        _rotate_log(log, 7)
        result = [json.loads(l)["seq"] for l in log.read_text().strip().splitlines()]
        assert result == [3, 4, 5, 6, 7, 8, 9]


# ---------------------------------------------------------------------------
# _count_lines
# ---------------------------------------------------------------------------

class TestCountLines:
    def test_absent_returns_0(self, tmp_path):
        assert _count_lines(tmp_path / "missing.jsonl") == 0

    def test_empty_returns_0(self, tmp_path):
        log = tmp_path / "empty.jsonl"
        log.write_text("")
        assert _count_lines(log) == 0

    def test_n_lines_returns_n(self, tmp_path):
        log = tmp_path / "test.jsonl"
        log.write_text('{"a": 1}\n{"b": 2}\n{"c": 3}\n')
        assert _count_lines(log) == 3

    def test_single_line_no_trailing_newline(self, tmp_path):
        log = tmp_path / "test.jsonl"
        log.write_text('{"a": 1}')
        assert _count_lines(log) == 1


# ---------------------------------------------------------------------------
# run_cleanup
# ---------------------------------------------------------------------------

class TestRunCleanup:
    def test_returns_summary_with_required_keys(self, tmp_path):
        summary = run_cleanup(tmp_path)
        assert "timestamp" in summary
        assert "audit_line_counts" in summary

    def test_timestamp_is_iso8601(self, tmp_path):
        summary = run_cleanup(tmp_path)
        datetime.fromisoformat(summary["timestamp"].replace("Z", "+00:00"))

    def test_audit_line_counts_has_all_three_logs(self, tmp_path):
        summary = run_cleanup(tmp_path)
        counts = summary["audit_line_counts"]
        assert "spawned_processes.jsonl" in counts
        assert "mcp_tool_audit.jsonl" in counts
        assert "mcp_lint_audit.jsonl" in counts

    def test_absent_logs_show_zero(self, tmp_path):
        summary = run_cleanup(tmp_path)
        assert all(v == 0 for v in summary["audit_line_counts"].values())

    def test_spawned_processes_rotated_to_500(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        log.write_text("\n".join(f'{{"n": {i}}}' for i in range(600)) + "\n")
        run_cleanup(tmp_path)
        assert len(log.read_text().strip().splitlines()) == 500

    def test_mcp_tool_rotated_to_500(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        log.write_text("\n".join(f'{{"n": {i}}}' for i in range(600)) + "\n")
        run_cleanup(tmp_path)
        assert len(log.read_text().strip().splitlines()) == 500

    def test_mcp_lint_rotated_to_200(self, tmp_path):
        log = tmp_path / "mcp_lint_audit.jsonl"
        log.write_text("\n".join(f'{{"n": {i}}}' for i in range(300)) + "\n")
        run_cleanup(tmp_path)
        assert len(log.read_text().strip().splitlines()) == 200

    def test_counts_match_kept_lines(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        log.write_text("\n".join(f'{{"n": {i}}}' for i in range(50)) + "\n")
        summary = run_cleanup(tmp_path)
        assert summary["audit_line_counts"]["spawned_processes.jsonl"] == 50

    def test_run_cleanup_no_crash_on_missing_dir(self, tmp_path):
        sub = tmp_path / "nonexistent_subdir"
        # Directory doesn't exist — run_cleanup should still return a dict
        summary = run_cleanup(sub)
        assert "timestamp" in summary


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

class TestMain:
    def test_always_exits_0_clean(self, tmp_path):
        summary_path = tmp_path / "session_summary.json"
        with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.WINDSURF_DIR", tmp_path):
            with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.SESSION_SUMMARY", summary_path):
                assert main() == 0

    def test_session_summary_written(self, tmp_path):
        summary_path = tmp_path / "session_summary.json"
        with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.WINDSURF_DIR", tmp_path):
            with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.SESSION_SUMMARY", summary_path):
                main()
        assert summary_path.exists()

    def test_session_summary_has_timestamp(self, tmp_path):
        summary_path = tmp_path / "session_summary.json"
        with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.WINDSURF_DIR", tmp_path):
            with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.SESSION_SUMMARY", summary_path):
                main()
        data = json.loads(summary_path.read_text())
        assert "timestamp" in data
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

    def test_session_summary_has_audit_line_counts(self, tmp_path):
        summary_path = tmp_path / "session_summary.json"
        with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.WINDSURF_DIR", tmp_path):
            with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.SESSION_SUMMARY", summary_path):
                main()
        data = json.loads(summary_path.read_text())
        assert "audit_line_counts" in data

    def test_main_exits_0_even_if_oserror(self, tmp_path):
        summary_path = tmp_path / "session_summary.json"
        with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.WINDSURF_DIR", tmp_path):
            with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.SESSION_SUMMARY", summary_path):
                with patch(
                    "ops_scripts.hooks.windsurf.post_cascade_cleanup.run_cleanup",
                    side_effect=OSError("disk full"),
                ):
                    assert main() == 0

    def test_main_creates_windsurf_dir_if_missing(self, tmp_path):
        new_dir = tmp_path / "new_artifacts" / "windsurf"
        summary_path = new_dir / "session_summary.json"
        with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.WINDSURF_DIR", new_dir):
            with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.SESSION_SUMMARY", summary_path):
                main()
        assert new_dir.exists()

    def test_rotation_applied_during_main(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        log.write_text("\n".join(f'{{"n": {i}}}' for i in range(600)) + "\n")
        summary_path = tmp_path / "session_summary.json"
        with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.WINDSURF_DIR", tmp_path):
            with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.SESSION_SUMMARY", summary_path):
                main()
        assert len(log.read_text().strip().splitlines()) == 500
