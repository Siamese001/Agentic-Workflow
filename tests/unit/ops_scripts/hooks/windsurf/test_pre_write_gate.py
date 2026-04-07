"""
Tests for ops_scripts/hooks/windsurf/pre_write_gate.py (Phase 1.2).

Covers:
  - Anti-pattern: bare except → block
  - Anti-pattern: except Exception without guardian → block
  - Anti-pattern: except Exception WITH guardian → allow
  - Anti-pattern: shell=True in subprocess → block
  - Python syntax error → block
  - Valid Python syntax → allow
  - mcp_config.json deletion (no edits) → block
  - mcp_config.json risky edit → warn, allow
  - Non-.py file with syntax-like content → allow (no ast parse)
  - Malformed JSON → fail-closed (block)
  - Empty stdin → fail-closed (block)
  - Missing edits field → allow
"""

import json
import sys
from io import StringIO
from unittest.mock import patch

import pytest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[5]))

from ops_scripts.hooks.windsurf.pre_write_gate import (
    check_mcp_config,
    check_python_syntax,
    main,
    scan_antipatterns,
)


class TestScanAntipatterns:
    def test_bare_except_blocked(self):
        code = "try:\n    pass\nexcept:\n    pass\n"
        violations = scan_antipatterns(code)
        assert any("Bare 'except:'" in v for v in violations)

    def test_except_exception_no_guardian_blocked(self):
        code = "try:\n    pass\nexcept Exception as e:\n    pass\n"
        violations = scan_antipatterns(code)
        assert any("except Exception" in v for v in violations)

    def test_except_exception_with_guardian_allowed(self):
        code = "except Exception as e:  # guardian: allow-broad-exception -- legacy API contract\n"
        violations = scan_antipatterns(code)
        assert not any("except Exception" in v for v in violations)

    def test_shell_true_blocked(self):
        code = "import subprocess\nsubprocess.run('ls', shell=True)\n"
        violations = scan_antipatterns(code)
        assert any("shell=True" in v for v in violations)

    def test_clean_code_no_violations(self):
        code = "def foo():\n    return 42\n"
        assert scan_antipatterns(code) == []

    def test_specific_exception_allowed(self):
        code = "try:\n    pass\nexcept ValueError as e:\n    pass\n"
        assert scan_antipatterns(code) == []


class TestCheckPythonSyntax:
    def test_valid_syntax_no_errors(self, tmp_path):
        f = tmp_path / "mod.py"
        f.write_text("x = 1\n", encoding="utf-8")
        edits = [{"old_string": "x = 1", "new_string": "x = 2"}]
        assert check_python_syntax(str(f), edits) == []

    def test_invalid_syntax_detected(self, tmp_path):
        f = tmp_path / "mod.py"
        f.write_text("def foo():\n    pass\n", encoding="utf-8")
        edits = [{"old_string": "pass", "new_string": "except:\n    pass"}]
        errors = check_python_syntax(str(f), edits)
        assert len(errors) > 0
        assert "syntax error" in errors[0].lower()

    def test_non_python_file_skipped(self, tmp_path):
        f = tmp_path / "config.json"
        f.write_text("{}", encoding="utf-8")
        assert check_python_syntax(str(f), []) == []

    def test_new_file_creation(self, tmp_path):
        f = tmp_path / "new_mod.py"
        edits = [{"old_string": "", "new_string": "def bar():\n    return 1\n"}]
        assert check_python_syntax(str(f), edits) == []


class TestCheckMcpConfig:
    def test_mcp_deletion_blocked(self):
        block, msgs = check_mcp_config("~/.codeium/windsurf/mcp_config.json", [])
        assert block is True
        assert any("deletion" in m for m in msgs)

    def test_mcp_risky_edit_warns_no_block(self):
        edits = [{"old_string": "", "new_string": '"mcpServers": {"newServer": {}}'}]
        block, msgs = check_mcp_config("mcp_config.json", edits)
        assert block is False
        assert len(msgs) > 0

    def test_non_mcp_file_ignored(self):
        block, msgs = check_mcp_config("some_file.py", [{"old_string": "x", "new_string": "y"}])
        assert block is False
        assert msgs == []

    def test_server_removal_warns(self):
        edits = [{"old_string": '"myServer": {"command": "python"}', "new_string": ""}]
        block, msgs = check_mcp_config("mcp_config.json", edits)
        assert block is False
        assert any("removed" in m for m in msgs)


class TestMain:
    def _run(self, payload: dict) -> int:
        raw = json.dumps(payload)
        with patch("sys.stdin", StringIO(raw)):
            return main()

    def test_clean_edit_allowed(self):
        payload = {
            "tool_info": {
                "file_path": "some/module.py",
                "edits": [{"old_string": "x = 1", "new_string": "x = 2"}],
            }
        }
        assert self._run(payload) == 0

    def test_bare_except_edit_blocked(self):
        payload = {
            "tool_info": {
                "file_path": "some/module.py",
                "edits": [{"old_string": "", "new_string": "except:\n    pass\n"}],
            }
        }
        assert self._run(payload) == 2

    def test_shell_true_edit_blocked(self):
        payload = {
            "tool_info": {
                "file_path": "runner.py",
                "edits": [{"old_string": "", "new_string": "import subprocess\nsubprocess.run('ls', shell=True)\n"}],
            }
        }
        assert self._run(payload) == 2

    def test_mcp_deletion_blocked(self):
        payload = {"tool_info": {"file_path": "mcp_config.json", "edits": []}}
        assert self._run(payload) == 2

    def test_empty_stdin_fail_closed(self):
        with patch("sys.stdin", StringIO("")):
            assert main() == 2

    def test_malformed_json_fail_closed(self):
        with patch("sys.stdin", StringIO("{bad json}")):
            assert main() == 2

    def test_no_edits_field_allowed(self):
        payload = {"tool_info": {"file_path": "anything.txt"}}
        assert self._run(payload) == 0

    def test_markdown_file_always_allowed(self):
        payload = {
            "tool_info": {
                "file_path": ".windsurf/rules/constitutional.md",
                "edits": [{"old_string": "x", "new_string": "except:\n    pass\n"}],
            }
        }
        assert self._run(payload) == 0

    def test_non_py_json_doc_always_allowed(self):
        payload = {
            "tool_info": {
                "file_path": "docs/reference/some_doc.json",
                "edits": [{"old_string": "", "new_string": "shell=True"}],
            }
        }
        assert self._run(payload) == 0
