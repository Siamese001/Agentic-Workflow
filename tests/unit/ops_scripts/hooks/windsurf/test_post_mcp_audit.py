"""
Tests for ops_scripts/hooks/windsurf/post_mcp_audit.py (Phase 1.7).

Covers:
  - Valid payload → log record written with all fields
  - duration_ms present → recorded
  - duration_ms absent → None recorded
  - Empty stdin → exit 0, no log
  - Malformed JSON → exit 0, no log
  - ALWAYS exits 0
  - Log appended (not overwritten)
  - Log has required fields: timestamp, mcp_server_name, mcp_tool_name, duration_ms
"""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from ops_scripts.hooks.windsurf.post_mcp_audit import main


class TestMain:
    def _run(self, payload: dict, log_path: Path) -> int:
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            with patch("ops_scripts.hooks.windsurf.post_mcp_audit.AUDIT_LOG", log_path):
                return main()

    def test_valid_payload_exits_0(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {
            "tool_info": {
                "mcp_server_name": "adg_sqlite",
                "mcp_tool_name": "adg_health",
                "duration_ms": 42,
            },
        }
        assert self._run(payload, log) == 0

    def test_log_record_has_required_fields(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {
            "tool_info": {
                "mcp_server_name": "filesystem",
                "mcp_tool_name": "read_file",
                "duration_ms": 123,
            },
        }
        self._run(payload, log)
        assert log.exists()
        record = json.loads(log.read_text().strip())
        assert record["mcp_server_name"] == "filesystem"
        assert record["mcp_tool_name"] == "read_file"
        assert record["duration_ms"] == 123
        assert "timestamp" in record

    def test_duration_ms_absent_recorded_as_none(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {"tool_info": {"mcp_server_name": "brave-search", "mcp_tool_name": "web_search"}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["duration_ms"] is None

    def test_empty_stdin_exits_0_no_log(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        with patch("sys.stdin", StringIO("")):
            with patch("ops_scripts.hooks.windsurf.post_mcp_audit.AUDIT_LOG", log):
                result = main()
        assert result == 0
        assert not log.exists()

    def test_malformed_json_exits_0_no_log(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        with patch("sys.stdin", StringIO("{bad json")):
            with patch("ops_scripts.hooks.windsurf.post_mcp_audit.AUDIT_LOG", log):
                result = main()
        assert result == 0
        assert not log.exists()

    def test_log_appended_multiple_calls(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        p1 = {"tool_info": {"mcp_server_name": "s1", "mcp_tool_name": "t1"}}
        p2 = {"tool_info": {"mcp_server_name": "s2", "mcp_tool_name": "t2"}}
        self._run(p1, log)
        self._run(p2, log)
        lines = log.read_text().strip().splitlines()
        assert len(lines) == 2
        assert json.loads(lines[0])["mcp_server_name"] == "s1"
        assert json.loads(lines[1])["mcp_server_name"] == "s2"

    def test_missing_server_name_logs_empty_string(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {"tool_info": {"mcp_tool_name": "some_tool"}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["mcp_server_name"] == ""
