"""
Tests for ops_scripts/hooks/windsurf/post_cascade_cleanup.py (Phase 1.8).

Covers:
  - Log rotation: file over limit → truncated to last N lines
  - Log rotation: file under limit → unchanged
  - Log rotation: file absent → graceful (0 lines kept)
  - session_summary.json written with correct structure
  - session_summary.json has timestamp and audit_line_counts
  - ALWAYS exits 0
  - run_cleanup returns summary dict with expected keys
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from ops_scripts.hooks.windsurf.post_cascade_cleanup import (
    _count_lines,
    _rotate_log,
    main,
    run_cleanup,
)


class TestRotateLog:
    def test_file_over_limit_truncated(self, tmp_path):
        log = tmp_path / "test.jsonl"
        lines = [f'{{"n": {i}}}' for i in range(600)]
        log.write_text("\n".join(lines) + "\n")
        kept = _rotate_log(log, 500)
        assert kept == 500
        result_lines = log.read_text().strip().splitlines()
        assert len(result_lines) == 500
        assert json.loads(result_lines[0])["n"] == 100

    def test_file_under_limit_unchanged(self, tmp_path):
        log = tmp_path / "test.jsonl"
        lines = [f'{{"n": {i}}}' for i in range(50)]
        log.write_text("\n".join(lines) + "\n")
        kept = _rotate_log(log, 500)
        assert kept == 50
        assert len(log.read_text().strip().splitlines()) == 50

    def test_file_at_limit_unchanged(self, tmp_path):
        log = tmp_path / "test.jsonl"
        lines = [f'{{"n": {i}}}' for i in range(500)]
        log.write_text("\n".join(lines) + "\n")
        kept = _rotate_log(log, 500)
        assert kept == 500

    def test_absent_file_returns_0(self, tmp_path):
        assert _rotate_log(tmp_path / "missing.jsonl", 500) == 0


class TestCountLines:
    def test_counts_correctly(self, tmp_path):
        log = tmp_path / "test.jsonl"
        log.write_text('{"a": 1}\n{"b": 2}\n')
        assert _count_lines(log) == 2

    def test_absent_returns_0(self, tmp_path):
        assert _count_lines(tmp_path / "missing.jsonl") == 0


class TestRunCleanup:
    def test_returns_summary_dict_with_required_keys(self, tmp_path):
        summary = run_cleanup(tmp_path)
        assert "timestamp" in summary
        assert "audit_line_counts" in summary

    def test_audit_line_counts_contains_log_names(self, tmp_path):
        (tmp_path / "spawned_processes.jsonl").write_text('{"x": 1}\n')
        (tmp_path / "mcp_tool_audit.jsonl").write_text('{"x": 1}\n')
        (tmp_path / "mcp_lint_audit.jsonl").write_text('{"x": 1}\n')
        summary = run_cleanup(tmp_path)
        counts = summary["audit_line_counts"]
        assert "spawned_processes.jsonl" in counts
        assert "mcp_tool_audit.jsonl" in counts
        assert "mcp_lint_audit.jsonl" in counts

    def test_absent_logs_show_0(self, tmp_path):
        summary = run_cleanup(tmp_path)
        counts = summary["audit_line_counts"]
        assert all(v == 0 for v in counts.values())

    def test_rotation_applied(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        lines = [f'{{"n": {i}}}' for i in range(600)]
        log.write_text("\n".join(lines) + "\n")
        run_cleanup(tmp_path)
        assert len(log.read_text().strip().splitlines()) == 500


class TestMain:
    def test_always_exits_0(self, tmp_path):
        with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.WINDSURF_DIR", tmp_path):
            with patch(
                "ops_scripts.hooks.windsurf.post_cascade_cleanup.SESSION_SUMMARY",
                tmp_path / "session_summary.json",
            ):
                result = main()
        assert result == 0

    def test_session_summary_written(self, tmp_path):
        summary_path = tmp_path / "session_summary.json"
        with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.WINDSURF_DIR", tmp_path):
            with patch("ops_scripts.hooks.windsurf.post_cascade_cleanup.SESSION_SUMMARY", summary_path):
                main()
        assert summary_path.exists()
        data = json.loads(summary_path.read_text())
        assert "timestamp" in data
        assert "audit_line_counts" in data
