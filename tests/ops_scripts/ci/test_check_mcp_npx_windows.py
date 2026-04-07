"""
Tests for ops_scripts/ci/check_mcp_npx_windows.py

Edge cases covered:
- Bare 'npx' in double-quotes → violation
- Bare 'npx' unquoted → violation
- Bare 'npx' in single-quotes → violation
- 'npx.cmd' → no violation (correct form)
- 'npx' as part of package name in args → no violation (not a command line)
- Multiple violations reported with correct line numbers
- Missing yaml file → exits 0 (skip, not fail)
- Empty file → exits 0
- File with only comments → exits 0
- Mixed valid/invalid → reports only invalid
- check_npx_commands() return value: 0=pass, 1=fail
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from ops_scripts.ci.check_mcp_npx_windows import check_npx_commands

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_with_content(tmp_path, content: str) -> int:
    yaml_file = tmp_path / "mcp_servers.yaml"
    yaml_file.write_text(content, encoding="utf-8")
    with patch("ops_scripts.ci.check_mcp_npx_windows.YAML_PATH", yaml_file):
        return check_npx_commands()


# ===========================================================================
# Violation detection
# ===========================================================================

class TestNpxViolationDetection:
    def test_double_quoted_npx_is_violation(self, tmp_path):
        content = '    command: "npx"\n'
        assert _run_with_content(tmp_path, content) == 1

    def test_unquoted_npx_is_violation(self, tmp_path):
        content = "    command: npx\n"
        assert _run_with_content(tmp_path, content) == 1

    def test_single_quoted_npx_is_violation(self, tmp_path):
        content = "    command: 'npx'\n"
        assert _run_with_content(tmp_path, content) == 1

    def test_npx_cmd_is_not_violation(self, tmp_path):
        content = '    command: "npx.cmd"\n'
        assert _run_with_content(tmp_path, content) == 0

    def test_npx_in_package_name_arg_not_violation(self, tmp_path):
        """'npx' appearing in args (package names) must not trigger."""
        content = (
            '    command: "npx.cmd"\n'
            '    args:\n'
            '      - "-y"\n'
            '      - "@modelcontextprotocol/server-npx-example"\n'
        )
        assert _run_with_content(tmp_path, content) == 0

    def test_npx_in_comment_not_violation(self, tmp_path):
        content = "# command: npx  (old form, do not use)\n    command: \"npx.cmd\"\n"
        assert _run_with_content(tmp_path, content) == 0

    def test_multiple_violations_all_reported(self, tmp_path, capsys):
        content = (
            "  brave_search:\n"
            '    command: "npx"\n'
            "  deepwiki:\n"
            '    command: "npx"\n'
            "  filesystem:\n"
            '    command: "npx.cmd"\n'
        )
        result = _run_with_content(tmp_path, content)
        assert result == 1
        captured = capsys.readouterr()
        assert "Line 2" in captured.out
        assert "Line 4" in captured.out
        assert "Line 6" not in captured.out  # npx.cmd must not appear

    def test_violation_output_contains_fix_instruction(self, tmp_path, capsys):
        content = '    command: "npx"\n'
        _run_with_content(tmp_path, content)
        captured = capsys.readouterr()
        assert "npx.cmd" in captured.out
        assert "sync_yaml_to_global.py" in captured.out

    def test_partial_match_not_triggered(self, tmp_path):
        """'npx-extra' or 'npx2' must not match."""
        content = "    command: npx-extra\n    command: npx2\n"
        assert _run_with_content(tmp_path, content) == 0


# ===========================================================================
# File-level edge cases
# ===========================================================================

class TestFileEdgeCases:
    def test_missing_yaml_returns_0(self, tmp_path):
        missing = tmp_path / "no_such_file.yaml"
        with patch("ops_scripts.ci.check_mcp_npx_windows.YAML_PATH", missing):
            assert check_npx_commands() == 0

    def test_empty_file_returns_0(self, tmp_path):
        assert _run_with_content(tmp_path, "") == 0

    def test_only_comments_returns_0(self, tmp_path):
        content = "# This is a comment\n# command: npx  (historical note)\n"
        assert _run_with_content(tmp_path, content) == 0

    def test_valid_full_yaml_returns_0(self, tmp_path):
        content = """
schema_version: "1.0.0"
servers:
  sequential_thinking:
    name: "Sequential Thinking"
    command: "npx.cmd"
    args:
      - "-y"
      - "@modelcontextprotocol/server-sequential-thinking"
  filesystem:
    name: "Filesystem"
    command: "npx.cmd"
    args:
      - "-y"
      - "@modelcontextprotocol/server-filesystem"
  redis_mcp:
    name: "Redis MCP"
    command: "python"
    args:
      - "-c"
      - "import server; server.run()"
"""
        assert _run_with_content(tmp_path, content) == 0

    def test_mixed_valid_invalid_only_flags_invalid(self, tmp_path, capsys):
        content = (
            "  memory:\n"
            '    command: "npx.cmd"\n'   # valid
            "  sequential_thinking:\n"
            '    command: "npx"\n'       # invalid — line 4
            "  filesystem:\n"
            '    command: "npx.cmd"\n'   # valid
        )
        result = _run_with_content(tmp_path, content)
        assert result == 1
        captured = capsys.readouterr()
        assert "Line 4" in captured.out
        # Valid lines must not appear in output
        assert "Line 2" not in captured.out
        assert "Line 6" not in captured.out


# ===========================================================================
# Output format
# ===========================================================================

class TestOutputFormat:
    def test_ok_message_on_pass(self, tmp_path, capsys):
        content = '    command: "npx.cmd"\n'
        _run_with_content(tmp_path, content)
        captured = capsys.readouterr()
        assert "[OK]" in captured.out

    def test_fail_message_on_violation(self, tmp_path, capsys):
        content = '    command: "npx"\n'
        _run_with_content(tmp_path, content)
        captured = capsys.readouterr()
        assert "[FAIL]" in captured.out


class TestMcpSsotHardcodedPaths:
    """Verify config/mcp_servers.yaml uses ${REPO_ROOT} placeholders, not hardcoded absolute paths."""

    _SSOT_PATH = Path(__file__).resolve().parents[3] / "config" / "mcp_servers.yaml"

    def _server_fields(self):
        """Extract all string values from args/env/cwd fields across all servers."""
        import yaml  # type: ignore[import-untyped]

        if not self._SSOT_PATH.exists():
            return []
        with open(self._SSOT_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        servers = (data or {}).get("servers", {})
        values = []
        for _name, cfg in servers.items():
            for field in ("cwd", "args"):
                val = cfg.get(field)
                if isinstance(val, str):
                    values.append(val)
                elif isinstance(val, list):
                    values.extend(str(v) for v in val)
            env = cfg.get("env") or {}
            values.extend(str(v) for v in env.values())
        return values

    def test_no_hardcoded_windows_paths_in_server_fields(self):
        """No server arg/env/cwd should contain a raw Windows absolute path."""
        import re
        values = self._server_fields()
        hardcoded = [v for v in values if re.search(r"(?<![a-zA-Z])[A-Za-z]:[/\\\\]", v) and "${" not in v]
        assert not hardcoded, (
            f"Hardcoded absolute paths found in mcp_servers.yaml server fields "
            f"(use ${{REPO_ROOT}} instead): {hardcoded}"
        )

    def test_repo_root_placeholder_used_where_needed(self):
        """Every server field containing a file path uses the ${REPO_ROOT} placeholder."""
        import re
        values = self._server_fields()
        for v in values:
            if re.search(r"[/\\\\]", v) and not v.startswith("-") and len(v) > 5:
                assert "${REPO_ROOT}" in v or "${" in v or not re.match(r"[A-Za-z]:", v), (
                    f"Potential hardcoded path without placeholder: {v!r}"
                )

    def test_ssot_yaml_is_parseable(self):
        """config/mcp_servers.yaml must be valid YAML."""
        import yaml  # type: ignore[import-untyped]
        assert self._SSOT_PATH.exists(), "config/mcp_servers.yaml not found"
        with open(self._SSOT_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data is not None
        assert "servers" in data
