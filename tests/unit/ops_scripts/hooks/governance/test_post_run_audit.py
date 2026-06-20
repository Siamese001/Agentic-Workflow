"""
EXHAUSTIVE tests for post_run_audit.py (Phase 1.6).

Plan requirements verified:
  - Valid payload → log record written with all required fields
  - Required fields: timestamp, command, cwd, pid
  - PID: None when psutil unavailable
  - PID: None when psutil import succeeds but no matching process found
  - PID: None when psutil raises AccessDenied on iteration
  - Empty stdin → exit 0, no log
  - Malformed JSON → exit 0, no log
  - Whitespace stdin → exit 0, no log
  - Missing command_line field → empty string logged
  - Missing cwd field → empty string logged
  - Log appended, not overwritten
  - ALWAYS exits 0
  - Flat payload (no tool_info wrapper) → works
  - Timestamp is ISO8601 format
  - Very long command → no crash
  - Unicode in command → no crash
  - Multiple sequential calls → all appended
"""

import json
import sys
from datetime import datetime
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / ".codex" / "governance/scripts"))

from post_run_audit import _get_pid_best_effort, main


# ---------------------------------------------------------------------------
# _get_pid_best_effort
# ---------------------------------------------------------------------------


class TestGetPidBestEffort:
    def test_returns_none_when_psutil_not_installed(self):
        with patch.dict("sys.modules", {"psutil": None}):
            result = _get_pid_best_effort("some_command", ".")
        assert result is None

    def test_returns_none_when_no_matching_process(self):
        # psutil available but returns empty iterator → no match → None
        try:
            import psutil as _psutil
        except ImportError:
            pytest.skip("psutil not installed")
        psutil_mock = MagicMock()
        psutil_mock.process_iter.return_value = []
        psutil_mock.NoSuchProcess = _psutil.NoSuchProcess
        psutil_mock.AccessDenied = _psutil.AccessDenied
        with patch.dict("sys.modules", {"psutil": psutil_mock}):
            result = _get_pid_best_effort("definitely_not_running_cmd", "/tmp")
        assert result is None

    def test_returns_none_when_psutil_raises_access_denied_on_iter(self):
        # psutil.process_iter itself raises AccessDenied → function catches ImportError only
        # so we simulate psutil unavailable via import error
        try:
            import psutil as _psutil
        except ImportError:
            pytest.skip("psutil not installed")
        psutil_mock = MagicMock()
        psutil_mock.process_iter.side_effect = _psutil.AccessDenied(0)
        psutil_mock.NoSuchProcess = _psutil.NoSuchProcess
        psutil_mock.AccessDenied = _psutil.AccessDenied
        with patch.dict("sys.modules", {"psutil": psutil_mock}):
            # The function catches NoSuchProcess/AccessDenied per-proc but not on iter itself
            # → should still return None without crashing
            result = _get_pid_best_effort("cmd", "/dir")
        assert result is None


# ---------------------------------------------------------------------------
# main() integration
# ---------------------------------------------------------------------------


class TestMain:
    def _run(self, payload: dict, log_path: Path) -> int:
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            with patch("post_run_audit.process_log", log_path):
                with patch(
                    "post_run_audit._get_pid_best_effort",
                    return_value=None,
                ):
                    return main()

    # Always exits 0
    def test_valid_payload_exits_0(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload = {"tool_info": {"command_line": "python run.py", "cwd": "/some/dir"}}
        assert self._run(payload, log) == 0

    def test_empty_stdin_exits_0_no_log(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        with patch("sys.stdin", StringIO("")):
            with patch("post_run_audit.process_log", log):
                result = main()
        assert result == 0
        assert not log.exists()

    def test_malformed_json_exits_0_no_log(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        with patch("sys.stdin", StringIO("{bad json")):
            with patch("post_run_audit.process_log", log):
                result = main()
        assert result == 0
        assert not log.exists()

    def test_whitespace_stdin_exits_0_no_log(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        with patch("sys.stdin", StringIO("   \n  ")):
            with patch("post_run_audit.process_log", log):
                result = main()
        assert result == 0
        assert not log.exists()

    # Log record content
    def test_log_record_has_all_required_fields(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload = {"tool_info": {"command_line": "pytest tests/", "cwd": "C:/repo"}}
        self._run(payload, log)
        assert log.exists()
        record = json.loads(log.read_text().strip())
        assert "timestamp" in record
        assert "command" in record
        assert "cwd" in record
        assert "pid" in record

    def test_command_captured_correctly(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload = {"tool_info": {"command_line": "pytest tests/unit/foo.py -q", "cwd": "."}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["command"] == "pytest tests/unit/foo.py -q"

    def test_cwd_captured_correctly(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload = {"tool_info": {"command_line": "git log", "cwd": "C:/Git/Agentic-Workflow"}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["cwd"] == "C:/Git/Agentic-Workflow"

    def test_pid_is_none_when_not_found(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload = {"tool_info": {"command_line": "python server.py", "cwd": "."}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["pid"] is None

    def test_timestamp_is_iso8601(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload = {"tool_info": {"command_line": "git status", "cwd": "."}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))

    # Missing field handling
    def test_missing_command_line_logs_empty_string(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload = {"tool_info": {"cwd": "/somewhere"}}
        self._run(payload, log)
        assert json.loads(log.read_text().strip())["command"] == ""

    def test_missing_cwd_logs_empty_string(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload = {"tool_info": {"command_line": "git status"}}
        self._run(payload, log)
        assert json.loads(log.read_text().strip())["cwd"] == ""

    def test_empty_tool_info_logs_empty_fields(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload = {"tool_info": {}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["command"] == ""
        assert record["cwd"] == ""

    # Append behavior
    def test_log_appended_not_overwritten(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        for cmd in ["cmd1", "cmd2", "cmd3"]:
            self._run({"tool_info": {"command_line": cmd, "cwd": "."}}, log)
        lines = log.read_text().strip().splitlines()
        assert len(lines) == 3
        assert json.loads(lines[0])["command"] == "cmd1"
        assert json.loads(lines[1])["command"] == "cmd2"
        assert json.loads(lines[2])["command"] == "cmd3"

    # Payload variants
    def test_flat_payload_no_tool_info(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload = {"command_line": "git push", "cwd": "."}
        self._run(payload, log)
        assert json.loads(log.read_text().strip())["command"] == "git push"

    # Edge cases
    def test_very_long_command_no_crash(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload = {"tool_info": {"command_line": "python " + "a" * 10000, "cwd": "."}}
        assert self._run(payload, log) == 0

    def test_unicode_in_command_no_crash(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload = {"tool_info": {"command_line": "python \u4e2d\u6587_script.py", "cwd": "."}}
        assert self._run(payload, log) == 0
        assert "\u4e2d\u6587" in json.loads(log.read_text().strip())["command"]
