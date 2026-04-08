"""
EXHAUSTIVE tests for post_write_audit.py (Phase 1.5).

Plan requirements verified:
  - Non-mcp_config file → exit 0, no audit written
  - mcp_config.json with missing mcpServers → finding logged
  - mcp_config.json with shell-syntax env var ${VAR:-default} → finding logged
  - mcp_config.json with Windsurf env var ${env:VAR} → allowed
  - mcp_config.json with server missing command AND serverUrl → finding logged
  - mcp_config.json with server using serverUrl only → allowed
  - mcp_config.json with server using url only → allowed
  - Clean mcp_config.json → no findings
  - Server removal edit (old→empty) → risky finding logged
  - New server addition edit (empty→mcpServers) → risky finding logged
  - mcp_config.json not on disk → no findings (graceful)
  - ALWAYS exits 0 regardless of findings
  - Empty stdin → exit 0
  - Malformed JSON → exit 0
  - Audit log appended (not overwritten) across multiple calls
  - Audit record has required fields: timestamp, file_path, findings, finding_count
  - Multiple findings in one config → all reported
  - Invalid JSON in config file → finding logged, no crash
"""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from ops_scripts.hooks.windsurf.post_write_audit import lint_mcp_config, main


# ---------------------------------------------------------------------------
# lint_mcp_config unit tests
# ---------------------------------------------------------------------------

class TestLintMcpConfig:
    def _write(self, tmp_path, config: dict) -> str:
        p = tmp_path / "mcp_config.json"
        p.write_text(json.dumps(config), encoding="utf-8")
        return str(p)

    def test_missing_mcp_servers_key_flagged(self, tmp_path):
        path = self._write(tmp_path, {"version": 1})
        findings = lint_mcp_config(path, [])
        assert any("mcpServers" in f for f in findings)

    def test_empty_mcp_servers_no_server_findings(self, tmp_path):
        path = self._write(tmp_path, {"mcpServers": {}})
        findings = lint_mcp_config(path, [])
        assert not any("missing 'command'" in f for f in findings)

    def test_server_missing_command_and_url_flagged(self, tmp_path):
        config = {"mcpServers": {"myServer": {"env": {}}}}
        path = self._write(tmp_path, config)
        findings = lint_mcp_config(path, [])
        assert any("missing 'command'" in f or "missing" in f.lower() for f in findings)

    def test_server_with_command_ok(self, tmp_path):
        config = {"mcpServers": {"myServer": {"command": "python", "args": ["srv.py"]}}}
        path = self._write(tmp_path, config)
        assert lint_mcp_config(path, []) == []

    def test_server_with_serverurl_ok(self, tmp_path):
        config = {"mcpServers": {"myServer": {"serverUrl": "http://localhost:3000"}}}
        path = self._write(tmp_path, config)
        findings = lint_mcp_config(path, [])
        assert not any("missing" in f.lower() for f in findings)

    def test_server_with_url_ok(self, tmp_path):
        config = {"mcpServers": {"myServer": {"url": "ws://localhost:8080"}}}
        path = self._write(tmp_path, config)
        findings = lint_mcp_config(path, [])
        assert not any("missing" in f.lower() for f in findings)

    def test_shell_env_var_syntax_flagged(self, tmp_path):
        config = {
            "mcpServers": {
                "redis": {
                    "command": "python",
                    "env": {"REDIS_URL": "${REDIS_URL:-redis://localhost:6379}"},
                },
            },
        }
        path = self._write(tmp_path, config)
        findings = lint_mcp_config(path, [])
        assert any("shell syntax" in f for f in findings)

    def test_windsurf_env_var_format_allowed(self, tmp_path):
        config = {
            "mcpServers": {
                "brave": {
                    "command": "npx",
                    "env": {"BRAVE_API_KEY": "${env:BRAVE_API_KEY}"},
                },
            },
        }
        path = self._write(tmp_path, config)
        findings = lint_mcp_config(path, [])
        assert not any("shell syntax" in f for f in findings)

    def test_multiple_servers_multiple_findings(self, tmp_path):
        config = {
            "mcpServers": {
                "s1": {"env": {}},  # missing command
                "s2": {"command": "python", "env": {"VAR": "${VAR:-default}"}},  # shell var
            },
        }
        path = self._write(tmp_path, config)
        findings = lint_mcp_config(path, [])
        assert len(findings) >= 2

    def test_clean_config_no_findings(self, tmp_path):
        config = {"mcpServers": {"fs": {"command": "python", "args": ["srv.py"]}}}
        path = self._write(tmp_path, config)
        assert lint_mcp_config(path, []) == []

    def test_server_removal_edit_flagged(self, tmp_path):
        config = {"mcpServers": {}}
        path = self._write(tmp_path, config)
        edits = [{"old_string": '"myServer": {"command": "python"}', "new_string": ""}]
        findings = lint_mcp_config(path, edits)
        assert any("removed" in f.lower() for f in findings)

    def test_new_server_edit_flagged(self, tmp_path):
        config = {"mcpServers": {}}
        path = self._write(tmp_path, config)
        edits = [{"old_string": "", "new_string": '"mcpServers": {"newServer": {}}'}]
        findings = lint_mcp_config(path, edits)
        assert any("added" in f.lower() or "risky" in f.lower() for f in findings)

    def test_file_not_on_disk_returns_empty(self, tmp_path):
        findings = lint_mcp_config(str(tmp_path / "nonexistent.json"), [])
        assert findings == []

    def test_invalid_json_in_file_reports_finding(self, tmp_path):
        p = tmp_path / "mcp_config.json"
        p.write_text("{invalid json!}", encoding="utf-8")
        findings = lint_mcp_config(str(p), [])
        assert len(findings) > 0
        assert any("parsed" in f.lower() or "json" in f.lower() for f in findings)

    def test_multiple_shell_env_vars_all_flagged(self, tmp_path):
        config = {
            "mcpServers": {
                "svc": {
                    "command": "python",
                    "env": {
                        "A": "${A:-default}",
                        "B": "${B:-fallback}",
                    },
                },
            },
        }
        path = self._write(tmp_path, config)
        findings = lint_mcp_config(path, [])
        assert sum(1 for f in findings if "shell syntax" in f) == 2


# ---------------------------------------------------------------------------
# main() integration
# ---------------------------------------------------------------------------

class TestMain:
    def _run(self, payload: dict, log_path: Path = None) -> int:
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            if log_path is not None:
                with patch("ops_scripts.hooks.windsurf.post_write_audit.AUDIT_LOG", log_path):
                    return main()
            return main()

    # Always exits 0
    def test_non_mcp_file_exits_0(self):
        payload = {"tool_info": {"file_path": "some_module.py", "edits": []}}
        assert self._run(payload) == 0

    def test_markdown_file_exits_0(self):
        payload = {"tool_info": {"file_path": "docs/README.md", "edits": []}}
        assert self._run(payload) == 0

    def test_empty_stdin_exits_0(self):
        with patch("sys.stdin", StringIO("")):
            assert main() == 0

    def test_malformed_json_exits_0(self):
        with patch("sys.stdin", StringIO("{bad}")):
            assert main() == 0

    def test_whitespace_stdin_exits_0(self):
        with patch("sys.stdin", StringIO("   \n")):
            assert main() == 0

    def test_mcp_config_with_findings_still_exits_0(self, tmp_path):
        config_path = tmp_path / "mcp_config.json"
        config_path.write_text(json.dumps({"version": 1}), encoding="utf-8")
        log = tmp_path / "mcp_lint_audit.jsonl"
        payload = {"tool_info": {"file_path": str(config_path), "edits": []}}
        assert self._run(payload, log) == 0

    def test_mcp_config_clean_exits_0(self, tmp_path):
        config_path = tmp_path / "mcp_config.json"
        config_path.write_text(
            json.dumps({"mcpServers": {"svc": {"command": "python"}}}), encoding="utf-8"
        )
        log = tmp_path / "mcp_lint_audit.jsonl"
        payload = {"tool_info": {"file_path": str(config_path), "edits": []}}
        assert self._run(payload, log) == 0

    # Audit log content
    def test_audit_log_written_on_mcp_config(self, tmp_path):
        config_path = tmp_path / "mcp_config.json"
        config_path.write_text(json.dumps({"mcpServers": {}}), encoding="utf-8")
        log = tmp_path / "mcp_lint_audit.jsonl"
        payload = {"tool_info": {"file_path": str(config_path), "edits": []}}
        self._run(payload, log)
        assert log.exists()
        record = json.loads(log.read_text().strip())
        assert "timestamp" in record
        assert "file_path" in record
        assert "findings" in record
        assert "finding_count" in record

    def test_audit_log_not_written_for_non_mcp_file(self, tmp_path):
        log = tmp_path / "mcp_lint_audit.jsonl"
        payload = {"tool_info": {"file_path": "module.py", "edits": []}}
        self._run(payload, log)
        assert not log.exists()

    def test_audit_log_appended_across_calls(self, tmp_path):
        config_path = tmp_path / "mcp_config.json"
        config_path.write_text(json.dumps({"mcpServers": {}}), encoding="utf-8")
        log = tmp_path / "mcp_lint_audit.jsonl"
        payload = {"tool_info": {"file_path": str(config_path), "edits": []}}
        self._run(payload, log)
        self._run(payload, log)
        lines = log.read_text().strip().splitlines()
        assert len(lines) == 2

    def test_finding_count_matches_findings_list(self, tmp_path):
        config_path = tmp_path / "mcp_config.json"
        config_path.write_text(json.dumps({"version": 1}), encoding="utf-8")
        log = tmp_path / "mcp_lint_audit.jsonl"
        payload = {"tool_info": {"file_path": str(config_path), "edits": []}}
        self._run(payload, log)
        record = json.loads(log.read_text().strip())
        assert record["finding_count"] == len(record["findings"])

    def test_missing_file_path_exits_0(self):
        payload = {"tool_info": {"edits": []}}
        assert self._run(payload) == 0

    def test_flat_payload_no_tool_info(self):
        payload = {"file_path": "some.py", "edits": []}
        assert self._run(payload) == 0
