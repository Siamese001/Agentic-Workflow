"""
Tests for ops_scripts/hooks/windsurf/pre_run_gate.py (Phase 1.1).

Covers:
  - PowerShell block (powershell, pwsh, mixed-case)
  - Full-suite block when ADG_REPAIR_ACTIVE set
  - Full-suite allowed when ADG_REPAIR_ACTIVE not set
  - Safe commands allowed
  - Malformed JSON handling (fail-closed)
  - Empty stdin handling (fail-closed)
  - Missing command_line field (allow)
"""

import json
import sys
from io import StringIO
from unittest.mock import patch

import pytest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[5]))

from ops_scripts.hooks.windsurf.pre_run_gate import check_command, main


class TestCheckCommand:
    def test_blocks_powershell_lowercase(self):
        assert check_command("powershell -Command Get-Date") == 2

    def test_blocks_pwsh(self):
        assert check_command("pwsh -File script.ps1") == 2

    def test_blocks_powershell_mixed_case(self):
        assert check_command("PowerShell -NoProfile") == 2

    def test_allows_python(self):
        assert check_command("python ops_scripts/ci/run_contract_gates.py") == 0

    def test_allows_pytest_scoped(self):
        assert check_command("pytest tests/unit/agentic_core/test_foo.py -q") == 0

    def test_allows_git_command(self):
        assert check_command("git status") == 0

    def test_blocks_full_suite_when_repair_active(self, monkeypatch):
        monkeypatch.setenv("ADG_REPAIR_ACTIVE", "1")
        assert check_command("pytest tests/unit") == 2

    def test_allows_full_suite_when_repair_inactive(self, monkeypatch):
        monkeypatch.delenv("ADG_REPAIR_ACTIVE", raising=False)
        assert check_command("pytest tests/unit") == 0

    def test_blocks_full_suite_with_extra_args_when_repair_active(self, monkeypatch):
        monkeypatch.setenv("ADG_REPAIR_ACTIVE", "1")
        assert check_command("pytest tests/unit -v --tb=short") == 2

    def test_allows_empty_command(self):
        assert check_command("") == 0


class TestMain:
    def _run_main(self, stdin_data: str, env_overrides: dict = None):
        env_overrides = env_overrides or {}
        with patch("sys.stdin", StringIO(stdin_data)):
            with patch.dict("os.environ", env_overrides, clear=False):
                return main()

    def test_valid_powershell_payload_blocked(self):
        payload = json.dumps({"tool_info": {"command_line": "pwsh -File x.ps1"}})
        assert self._run_main(payload) == 2

    def test_valid_safe_payload_allowed(self):
        payload = json.dumps({"tool_info": {"command_line": "python run.py"}})
        assert self._run_main(payload) == 0

    def test_flat_payload_without_tool_info(self):
        payload = json.dumps({"command_line": "git commit -m msg"})
        assert self._run_main(payload) == 0

    def test_malformed_json_fail_closed(self):
        assert self._run_main("{not valid json}") == 2

    def test_empty_stdin_fail_closed(self):
        assert self._run_main("") == 2

    def test_missing_command_line_field_allowed(self):
        payload = json.dumps({"tool_info": {}})
        assert self._run_main(payload) == 0

    def test_repair_active_full_suite_blocked(self):
        payload = json.dumps({"tool_info": {"command_line": "pytest tests/unit"}})
        assert self._run_main(payload, {"ADG_REPAIR_ACTIVE": "1"}) == 2

    def test_repair_active_scoped_allowed(self):
        payload = json.dumps({"tool_info": {"command_line": "pytest tests/unit/foo/test_bar.py"}})
        assert self._run_main(payload, {"ADG_REPAIR_ACTIVE": "1"}) == 0
