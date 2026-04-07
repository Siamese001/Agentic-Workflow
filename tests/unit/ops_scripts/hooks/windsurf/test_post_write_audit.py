"""
Tests for ops_scripts/hooks/windsurf/post_write_audit.py (Phase 1.5).

Covers:
  - Non-mcp_config file → exit 0, no audit
  - mcp_config.json with missing mcpServers → finding logged
  - mcp_config.json with shell-syntax env var → finding logged
  - mcp_config.json with server missing command/serverUrl → finding logged
  - Clean mcp_config.json → no findings
  - Server removal edit → risky finding logged
  - mcp_config.json not on disk → no findings (graceful)
  - ALWAYS exits 0 regardless of findings
  - Empty stdin → exit 0
  - Malformed JSON → exit 0
  - Audit log appended
"""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from ops_scripts.hooks.windsurf.post_write_audit import lint_mcp_config, main


class TestLintMcpConfig:
    def _write_config(self, tmp_path, config: dict) -> str:
        p = tmp_path / "mcp_config.json"
        p.write_text(json.dumps(config), encoding="utf-8")
        return str(p)

    def test_missing_mcp_servers_key(self, tmp_path):
        path = self._write_config(tmp_path, {"version": 1})
        findings = lint_mcp_config(path, [])
        assert any("mcpServers" in f for f in findings)

    def test_server_missing_command(self, tmp_path):
        config = {"mcpServers": {"myServer": {"env": {}}}}
        path = self._write_config(tmp_path, config)
        findings = lint_mcp_config(path, [])
        assert any("missing 'command'" in f for f in findings)

    def test_server_with_serverurl_ok(self, tmp_path):
        config = {"mcpServers": {"myServer": {"serverUrl": "http://localhost:3000"}}}
        path = self._write_config(tmp_path, config)
        findings = lint_mcp_config(path, [])
        assert not any("missing 'command'" in f for f in findings)

    def test_shell_env_var_syntax_flagged(self, tmp_path):
        config = {
            "mcpServers": {
                "redis": {
                    "command": "python",
                    "env": {"REDIS_URL": "${REDIS_URL:-redis://localhost:6379}"},
                }
            }
        }
        path = self._write_config(tmp_path, config)
        findings = lint_mcp_config(path, [])
        assert any("shell syntax" in f for f in findings)

    def test_windsurf_env_var_format_ok(self, tmp_path):
        config = {
            "mcpServers": {
                "brave": {
                    "command": "npx",
                    "env": {"BRAVE_API_KEY": "${env:BRAVE_API_KEY}"},
                }
            }
        }
        path = self._write_config(tmp_path, config)
        findings = lint_mcp_config(path, [])
        assert not any("shell syntax" in f for f in findings)

    def test_clean_config_no_findings(self, tmp_path):
        config = {
            "mcpServers": {
                "fs": {"command": "python", "args": ["server.py"]}
            }
        }
        path = self._write_config(tmp_path, config)
        assert lint_mcp_config(path, []) == []

    def test_server_removal_edit_flagged(self, tmp_path):
        config = {"mcpServers": {}}
        path = self._write_config(tmp_path, config)
        edits = [{"old_string": '"myServer": {"command": "python"}', "new_string": ""}]
        findings = lint_mcp_config(path, edits)
        assert any("removed" in f for f in findings)

    def test_file_not_on_disk_returns_empty(self, tmp_path):
        findings = lint_mcp_config(str(tmp_path / "nonexistent.json"), [])
        assert findings == []


class TestMain:
    def _run(self, payload: dict) -> int:
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            return main()

    def test_non_mcp_file_exits_0(self):
        payload = {"tool_info": {"file_path": "some_module.py", "edits": []}}
        assert self._run(payload) == 0

    def test_empty_stdin_exits_0(self):
        with patch("sys.stdin", StringIO("")):
            assert main() == 0

    def test_malformed_json_exits_0(self):
        with patch("sys.stdin", StringIO("{bad}")):
            assert main() == 0

    def test_mcp_config_with_findings_still_exits_0(self, tmp_path):
        config_path = tmp_path / "mcp_config.json"
        config_path.write_text(json.dumps({"version": 1}), encoding="utf-8")
        audit_log = tmp_path / "artifacts" / "windsurf" / "mcp_lint_audit.jsonl"
        payload = {"tool_info": {"file_path": str(config_path), "edits": []}}
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            with patch("ops_scripts.hooks.windsurf.post_write_audit.AUDIT_LOG", audit_log):
                result = main()
        assert result == 0

    def test_audit_log_written(self, tmp_path):
        config_path = tmp_path / "mcp_config.json"
        config_path.write_text(json.dumps({"mcpServers": {}}), encoding="utf-8")
        audit_log = tmp_path / "artifacts" / "windsurf" / "mcp_lint_audit.jsonl"
        payload = {"tool_info": {"file_path": str(config_path), "edits": []}}
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            with patch("ops_scripts.hooks.windsurf.post_write_audit.AUDIT_LOG", audit_log):
                main()
        assert audit_log.exists()
        lines = audit_log.read_text().strip().splitlines()
        assert len(lines) >= 1
        record = json.loads(lines[0])
        assert "timestamp" in record
        assert "findings" in record
