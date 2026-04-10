"""
EXHAUSTIVE tests for post_mcp_audit.py (Phase 1.7).

Plan requirements verified:
  - Valid payload → log record written with all required fields
  - Required fields: timestamp, mcp_server_name, mcp_tool_name, duration_ms
  - duration_ms present → recorded exactly
  - duration_ms absent → None recorded
  - duration_ms = 0 → recorded as 0 (not None)
  - Empty stdin → exit 0, no log
  - Malformed JSON → exit 0, no log
  - Whitespace stdin → exit 0, no log
  - Log appended across multiple calls
  - ALWAYS exits 0 regardless of input
  - Missing server name → empty string logged
  - Missing tool name → empty string logged
  - Flat payload (no tool_info wrapper)
  - Timestamp is ISO8601
  - All MCP server names accepted (no filtering)
  - Unicode in server/tool names → no crash
  - Very large duration_ms → no crash
"""

import json
import sys
from datetime import datetime
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / ".windsurf" / "scripts"))

from post_mcp_audit import main


# ---------------------------------------------------------------------------
# main() integration tests
# ---------------------------------------------------------------------------


class TestMain:
    def _run(self, payload: dict, log_path: Path) -> int:
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            with patch("post_mcp_audit.AUDIT_LOG", log_path):
                return main()

    # Always exits 0
    def test_valid_payload_exits_0(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {
            "tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_health", "duration_ms": 42}
        }
        assert self._run(payload, log) == 0

    def test_empty_stdin_exits_0_no_log(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        with patch("sys.stdin", StringIO("")):
            with patch("post_mcp_audit.AUDIT_LOG", log):
                result = main()
        assert result == 0
        assert not log.exists()

    def test_malformed_json_exits_0_no_log(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        with patch("sys.stdin", StringIO("{bad json")):
            with patch("post_mcp_audit.AUDIT_LOG", log):
                result = main()
        assert result == 0
        assert not log.exists()

    def test_whitespace_stdin_exits_0_no_log(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        with patch("sys.stdin", StringIO("   \n  ")):
            with patch("post_mcp_audit.AUDIT_LOG", log):
                result = main()
        assert result == 0
        assert not log.exists()

    # Record content
    def test_log_record_has_all_required_fields(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {
            "tool_info": {"mcp_server_name": "filesystem", "mcp_tool_name": "read_file", "duration_ms": 123}
        }
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert "timestamp" in record
        assert "mcp_server_name" in record
        assert "mcp_tool_name" in record
        assert "duration_ms" in record

    def test_server_name_captured(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {"tool_info": {"mcp_server_name": "memory", "mcp_tool_name": "search_nodes"}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["mcp_server_name"] == "memory"

    def test_tool_name_captured(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_edge_fanout"}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["mcp_tool_name"] == "adg_edge_fanout"

    def test_duration_ms_captured_exactly(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {"tool_info": {"mcp_server_name": "s", "mcp_tool_name": "t", "duration_ms": 999}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["duration_ms"] == 999

    def test_duration_ms_absent_recorded_as_none(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {"tool_info": {"mcp_server_name": "brave-search", "mcp_tool_name": "web_search"}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["duration_ms"] is None

    def test_duration_ms_zero_recorded_as_zero(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {"tool_info": {"mcp_server_name": "s", "mcp_tool_name": "t", "duration_ms": 0}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["duration_ms"] == 0

    def test_timestamp_is_iso8601(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {"tool_info": {"mcp_server_name": "s", "mcp_tool_name": "t"}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        ts = record["timestamp"]
        datetime.fromisoformat(ts.replace("Z", "+00:00"))

    # Missing fields
    def test_missing_server_name_logs_empty_string(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {"tool_info": {"mcp_tool_name": "some_tool"}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["mcp_server_name"] == ""

    def test_missing_tool_name_logs_empty_string(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {"tool_info": {"mcp_server_name": "some_server"}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["mcp_tool_name"] == ""

    def test_missing_all_fields_logs_empty_strings(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {"tool_info": {}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["mcp_server_name"] == ""
        assert record["mcp_tool_name"] == ""
        assert record["duration_ms"] is None

    # Append behavior
    def test_log_appended_not_overwritten(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        servers = ["s1", "s2", "s3", "s4", "s5"]
        for s in servers:
            self._run({"tool_info": {"mcp_server_name": s, "mcp_tool_name": "t"}}, log)
        lines = log.read_text().strip().splitlines()
        assert len(lines) == 5
        for i, s in enumerate(servers):
            assert json.loads(lines[i])["mcp_server_name"] == s

    # Payload variants
    def test_flat_payload_no_tool_info(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {"mcp_server_name": "gitkraken", "mcp_tool_name": "git_status"}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["mcp_server_name"] == "gitkraken"

    # All known MCP server names accepted
    @pytest.mark.parametrize(
        "server",
        [
            "adg_sqlite",
            "memory",
            "filesystem",
            "gitkraken",
            "deepwiki",
            "enhanced_http",
            "redis",
            "task_manager",
            "pytest_mcp",
        ],
    )
    def test_all_known_mcp_servers_accepted(self, tmp_path, server):
        log = tmp_path / f"audit_{server}.jsonl"
        payload = {"tool_info": {"mcp_server_name": server, "mcp_tool_name": "some_tool"}}
        result = self._run(payload, log)
        assert result == 0
        assert log.exists()

    # Edge cases
    def test_unicode_server_name_no_crash(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {"tool_info": {"mcp_server_name": "\u4e2d\u6587_server", "mcp_tool_name": "tool"}}
        result = self._run(payload, log)
        assert result == 0

    def test_very_large_duration_ms_no_crash(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        payload = {"tool_info": {"mcp_server_name": "s", "mcp_tool_name": "t", "duration_ms": 10**15}}
        result = self._run(payload, log)
        assert result == 0
        record = json.loads(log.read_text().strip())
        assert record["duration_ms"] == 10**15
