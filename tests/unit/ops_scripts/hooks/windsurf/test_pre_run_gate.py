"""
EXHAUSTIVE tests for pre_run_gate.py (Phase 1.1) — PP-4, PP-9.

Plan requirements verified:
  - PowerShell ban (pwsh, powershell, mixed case, .exe suffix, with args, with path)
  - powershell-as-executor with allowed script path still BLOCKED (allowlist bypass fix)
  - python invoking allowed checker script still ALLOWED
  - Full-suite block when ADG_REPAIR_ACTIVE set
  - Full-suite allowed when ADG_REPAIR_ACTIVE not set
  - Scoped pytest allowed even when ADG_REPAIR_ACTIVE set
  - Safe commands (python, git, ruff, pip, etc.) allowed
  - Whitelist: checker scripts referencing 'powershell' in path allowed
  - Fail policy CLOSED: empty stdin → exit 2, malformed JSON → exit 2
  - Missing command_line field → exit 0 (allow)
  - Flat payload (no tool_info wrapper) → works
  - Unicode in command line → no crash
  - Very long command line → no crash
  - Newlines/whitespace in payload → handled
  - All POWERSHELL_PATTERNS case-insensitive
"""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / ".claude" / "governance/scripts"))

from pre_run_gate import check_command, main


# ---------------------------------------------------------------------------
# check_command unit tests
# ---------------------------------------------------------------------------


class TestCheckCommandPowerShellBlock:
    def test_blocks_powershell_lowercase(self):
        assert check_command("powershell -Command Get-Date") == 2

    def test_blocks_pwsh_lowercase(self):
        assert check_command("pwsh -File script.ps1") == 2

    def test_blocks_PowerShell_mixed_case(self):
        assert check_command("PowerShell -NoProfile -Command whoami") == 2

    def test_blocks_PWSH_uppercase(self):
        assert check_command("PWSH -NonInteractive") == 2

    def test_blocks_powershell_exe(self):
        assert check_command("powershell.exe -Command ls") == 2

    def test_blocks_pwsh_exe(self):
        assert check_command("pwsh.exe -File run.ps1") == 2

    def test_blocks_powershell_no_args(self):
        assert check_command("powershell") == 2

    def test_blocks_pwsh_no_args(self):
        assert check_command("pwsh") == 2

    def test_blocks_full_path_powershell(self):
        assert check_command("C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command x") == 2

    def test_blocks_full_path_pwsh(self):
        assert check_command("C:/Program Files/PowerShell/7/pwsh.exe -Command x") == 2


class TestCheckCommandAllowed:
    def test_allows_python(self):
        assert check_command("python ops_scripts/ci/run_contract_gates.py") == 0

    def test_allows_python3(self):
        assert check_command("python3 -m pytest tests/unit/foo.py") == 0

    def test_allows_scoped_pytest(self):
        assert check_command("pytest tests/unit/agentic_core/test_foo.py -q") == 0

    def test_allows_git_status(self):
        assert check_command("git status") == 0

    def test_allows_git_commit(self):
        assert check_command("git commit --no-verify -m 'msg'") == 0

    def test_allows_pip_install(self):
        assert check_command("pip install -r requirements.txt") == 0

    def test_allows_ruff(self):
        assert check_command("ruff check agentic_core/") == 0

    def test_allows_empty_string(self):
        assert check_command("") == 0

    def test_allows_node(self):
        assert check_command("node server.js") == 0

    def test_allows_cmd_with_powershell_in_argument_value(self):
        # powershell appears as string value in arg, not as executable
        assert check_command("python check_powershell_ban.py --report") == 0

    def test_allows_checker_script_path_containing_powershell(self):
        # Script path contains 'powershell' — must not be blocked
        assert check_command("python ops_scripts/ci/check_powershell_ban.py") == 0

    def test_powershell_as_executor_with_allowed_script_still_blocked(self):
        # The allowlist must NOT exempt powershell itself as executor.
        # Before the fix, "powershell check_powershell_ban.py" bypassed the gate.
        assert check_command("powershell check_powershell_ban.py") == 2

    def test_pwsh_as_executor_with_allowed_script_still_blocked(self):
        assert check_command("pwsh check_powershell_ban.py") == 2

    def test_powershell_executor_with_pre_run_gate_still_blocked(self):
        assert check_command("powershell pre_run_gate.py") == 2


class TestCheckCommandFullSuiteBlock:
    def test_blocks_full_suite_when_repair_active(self, monkeypatch):
        monkeypatch.setenv("ADG_REPAIR_ACTIVE", "1")
        assert check_command("pytest tests/unit") == 2

    def test_blocks_full_suite_with_flags_when_repair_active(self, monkeypatch):
        monkeypatch.setenv("ADG_REPAIR_ACTIVE", "1")
        assert check_command("pytest tests/unit -v --tb=short") == 2

    def test_blocks_full_suite_with_trailing_space(self, monkeypatch):
        monkeypatch.setenv("ADG_REPAIR_ACTIVE", "1")
        assert check_command("pytest tests/unit ") == 2

    def test_allows_full_suite_when_repair_not_set(self, monkeypatch):
        monkeypatch.delenv("ADG_REPAIR_ACTIVE", raising=False)
        assert check_command("pytest tests/unit") == 0

    def test_allows_full_suite_when_repair_empty_string(self, monkeypatch):
        monkeypatch.setenv("ADG_REPAIR_ACTIVE", "")
        assert check_command("pytest tests/unit") == 0

    def test_allows_scoped_test_when_repair_active(self, monkeypatch):
        monkeypatch.setenv("ADG_REPAIR_ACTIVE", "1")
        assert check_command("pytest tests/unit/agentic_core/L0/test_routing.py -q") == 0

    def test_allows_scoped_with_class_when_repair_active(self, monkeypatch):
        monkeypatch.setenv("ADG_REPAIR_ACTIVE", "1")
        assert check_command("pytest tests/unit/foo/test_bar.py::TestClass::test_method -xvs") == 0


class TestCheckCommandEdgeCases:
    def test_unicode_command_no_crash(self):
        result = check_command("python script_\u4e2d\u6587.py")
        assert result in (0, 2)

    def test_very_long_command_no_crash(self):
        long_cmd = "python " + "a" * 10000
        assert check_command(long_cmd) == 0

    def test_newline_in_command(self):
        result = check_command("python\nscript.py")
        assert result in (0, 2)


# ---------------------------------------------------------------------------
# main() integration tests
# ---------------------------------------------------------------------------


class TestMain:
    def _run(self, stdin_data: str, env: dict = None) -> int:
        with patch("sys.stdin", StringIO(stdin_data)):
            with patch("sys.argv", ["pre_run_gate.py"]):
                if env is not None:
                    with patch.dict("os.environ", env, clear=False):
                        return main()
                return main()

    # Blocking cases
    def test_powershell_payload_blocked(self):
        payload = json.dumps({"tool_info": {"command_line": "pwsh -File x.ps1"}})
        assert self._run(payload) == 2

    def test_powershell_exe_payload_blocked(self):
        payload = json.dumps({"tool_info": {"command_line": "powershell.exe -Command whoami"}})
        assert self._run(payload) == 2

    def test_full_suite_repair_active_blocked(self):
        payload = json.dumps({"tool_info": {"command_line": "pytest tests/unit"}})
        assert self._run(payload, {"ADG_REPAIR_ACTIVE": "1"}) == 2

    # Allow cases
    def test_safe_python_command_allowed(self):
        payload = json.dumps({"tool_info": {"command_line": "python run.py"}})
        assert self._run(payload) == 0

    def test_scoped_pytest_repair_active_allowed(self):
        payload = json.dumps({"tool_info": {"command_line": "pytest tests/unit/foo/test_bar.py -q"}})
        assert self._run(payload, {"ADG_REPAIR_ACTIVE": "1"}) == 0

    def test_full_suite_no_repair_allowed(self):
        payload = json.dumps({"tool_info": {"command_line": "pytest tests/unit"}})
        assert self._run(payload, {"ADG_REPAIR_ACTIVE": ""}) == 0

    # Payload structure variants
    def test_flat_payload_without_tool_info(self):
        payload = json.dumps({"command_line": "git push origin main"})
        assert self._run(payload) == 0

    def test_flat_payload_powershell_blocked(self):
        payload = json.dumps({"command_line": "powershell Get-Date"})
        assert self._run(payload) == 2

    def test_missing_command_line_allowed(self):
        payload = json.dumps({"tool_info": {}})
        assert self._run(payload) == 0

    def test_null_command_line_allowed(self):
        payload = json.dumps({"tool_info": {"command_line": None}})
        assert self._run(payload) == 0

    def test_empty_command_line_allowed(self):
        payload = json.dumps({"tool_info": {"command_line": ""}})
        assert self._run(payload) == 0

    # Fail-closed cases
    def test_empty_stdin_fail_closed(self):
        assert self._run("") == 2

    def test_whitespace_only_stdin_fail_closed(self):
        assert self._run("   \n  ") == 2

    def test_malformed_json_fail_closed(self):
        assert self._run("{not valid json}") == 2

    def test_truncated_json_fail_closed(self):
        assert self._run('{"tool_info": {"command_line":') == 2

    def test_array_payload_allowed(self):
        # Non-dict root — hook guards isinstance(payload, dict) and returns 0
        payload = json.dumps([{"command_line": "git status"}])
        result = self._run(payload)
        assert result == 0  # non-dict payload → allow (no crash)

    def test_non_utf8_graceful(self):
        # Simulate stdin delivering non-JSON bytes as string
        result = self._run("\xff\xfe not utf8 text")
        assert result in (0, 2)
