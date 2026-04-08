"""
Tests for ops_scripts/hooks/windsurf/post_run_audit.py (Phase 1.6).

Covers:
  - Valid payload → log record written
  - Log record has required fields (timestamp, command, cwd, pid)
  - PID is None when psutil unavailable
  - Empty stdin → exit 0 (no log)
  - Malformed JSON → exit 0 (no log)
  - Missing command_line field → empty command logged
  - ALWAYS exits 0
  - Log file appended (not overwritten)
"""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from ops_scripts.hooks.windsurf.post_run_audit import main


class TestMain:
    def _run(self, payload: dict, log_path: Path) -> int:
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            with patch("ops_scripts.hooks.windsurf.post_run_audit.PROCESS_LOG", log_path):
                return main()

    def test_valid_payload_exits_0(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload = {"tool_info": {"command_line": "python run.py", "cwd": "/some/dir"}}
        assert self._run(payload, log) == 0

    def test_log_record_written(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload = {"tool_info": {"command_line": "pytest tests/", "cwd": "C:/repo"}}
        self._run(payload, log)
        assert log.exists()
        record = json.loads(log.read_text().strip())
        assert record["command"] == "pytest tests/"
        assert record["cwd"] == "C:/repo"
        assert "timestamp" in record
        assert "pid" in record

    def test_pid_is_none_when_psutil_unavailable(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload = {"tool_info": {"command_line": "python server.py", "cwd": "."}}
        with patch("sys.stdin", StringIO(json.dumps(payload))):
            with patch("ops_scripts.hooks.windsurf.post_run_audit.PROCESS_LOG", log):
                with patch.dict("sys.modules", {"psutil": None}):
                    main()
        record = json.loads(log.read_text().strip())
        assert record["pid"] is None

    def test_empty_stdin_exits_0_no_log(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        with patch("sys.stdin", StringIO("")):
            with patch("ops_scripts.hooks.windsurf.post_run_audit.PROCESS_LOG", log):
                result = main()
        assert result == 0
        assert not log.exists()

    def test_malformed_json_exits_0_no_log(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        with patch("sys.stdin", StringIO("{bad}")):
            with patch("ops_scripts.hooks.windsurf.post_run_audit.PROCESS_LOG", log):
                result = main()
        assert result == 0
        assert not log.exists()

    def test_missing_command_line_logs_empty_string(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload = {"tool_info": {"cwd": "/somewhere"}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["command"] == ""

    def test_log_appended_not_overwritten(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        payload1 = {"tool_info": {"command_line": "cmd1", "cwd": "."}}
        payload2 = {"tool_info": {"command_line": "cmd2", "cwd": "."}}
        self._run(payload1, log)
        self._run(payload2, log)
        lines = log.read_text().strip().splitlines()
        assert len(lines) == 2
        assert json.loads(lines[0])["command"] == "cmd1"
        assert json.loads(lines[1])["command"] == "cmd2"
