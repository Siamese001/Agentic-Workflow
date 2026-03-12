"""ADG-driven tests for agentic_core/L0_routing/utils/subprocess_runner_util.py — fan_in=10.

All functions wrap subprocess.run — tests mock it to verify:
  - correct command construction
  - JSON stdout parsing
  - timeout/error resilience
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.utils.subprocess_runner_util import (
    invoke_agent_roster_validation,
    invoke_arch_governor,
    invoke_code_validator,
    invoke_hierarchy_agent,
    invoke_orchestrator_mission,
)


def _mock_run(stdout: str = "", returncode: int = 0) -> MagicMock:
    m = MagicMock()
    m.stdout = stdout
    m.stderr = ""
    m.returncode = returncode
    return m


class TestAllExportsPresent:
    def test_all_exports_importable(self):
        import agentic_core.L0_routing.utils.subprocess_runner_util as m
        for name in m.__all__:
            assert hasattr(m, name), f"Missing __all__ member: {name}"


class TestInvokeArchGovernor:
    def test_returns_success_on_zero_returncode(self):
        with patch("subprocess.run", return_value=_mock_run(returncode=0)):
            result = invoke_arch_governor("verify")
        assert result["success"] is True

    def test_parses_json_stdout(self):
        payload = json.dumps({"success": True, "violations": 0})
        with patch("subprocess.run", return_value=_mock_run(stdout=payload)):
            result = invoke_arch_governor("verify")
        assert result["violations"] == 0

    def test_action_included_in_command(self):
        with patch("subprocess.run", return_value=_mock_run()) as mock_run:
            invoke_arch_governor("capture_baseline")
        cmd = mock_run.call_args[0][0]
        assert any("capture_baseline" in str(c) for c in cmd)

    def test_project_root_appended_when_provided(self):
        with patch("subprocess.run", return_value=_mock_run()) as mock_run:
            invoke_arch_governor("verify", project_root=Path("/repo"))
        cmd = mock_run.call_args[0][0]
        # project_root is passed as --project-root=/repo
        cmd_str = " ".join(str(c) for c in cmd)
        assert "project-root" in cmd_str or "repo" in cmd_str

    def test_timeout_returns_error_dict(self):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="x", timeout=300)):
            result = invoke_arch_governor("verify")
        assert result["success"] is False
        assert "timed out" in result["error"].lower()

    def test_json_decode_error_returns_error_dict(self):
        with patch("subprocess.run", return_value=_mock_run(stdout="NOT JSON")):
            result = invoke_arch_governor("verify")
        assert result["success"] is False
        assert "parse" in result["error"].lower()

    def test_generic_exception_returns_error_dict(self):
        with patch("subprocess.run", side_effect=OSError("no such file")):
            result = invoke_arch_governor("verify")
        assert result["success"] is False


class TestInvokeOrchestratorMission:
    def test_no_targets_returns_error(self):
        result = invoke_orchestrator_mission(targets=None)
        assert result["success"] is False
        assert "targets" in result["error"].lower()

    def test_targets_included_in_command(self):
        with patch("subprocess.run", return_value=_mock_run()) as mock_run:
            invoke_orchestrator_mission(targets=["agentic_core", "apps_lic"])
        cmd = mock_run.call_args[0][0]
        assert any("agentic_core" in str(c) for c in cmd)

    def test_execute_flag_appended(self):
        with patch("subprocess.run", return_value=_mock_run()) as mock_run:
            invoke_orchestrator_mission(targets=["x"], execute=True)
        cmd = mock_run.call_args[0][0]
        assert any("execute" in str(c) for c in cmd)

    def test_timeout_resilience(self):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="x", timeout=600)):
            result = invoke_orchestrator_mission(targets=["x"])
        assert result["success"] is False


class TestInvokeAgentRosterValidation:
    def test_returns_dict(self):
        with patch("subprocess.run", return_value=_mock_run(returncode=0)):
            result = invoke_agent_roster_validation()
        assert isinstance(result, dict)

    def test_parses_json_stdout(self):
        payload = json.dumps({"success": True, "agents_validated": 5})
        with patch("subprocess.run", return_value=_mock_run(stdout=payload)):
            result = invoke_agent_roster_validation()
        assert result["agents_validated"] == 5


class TestInvokeHierarchyAgent:
    def test_action_in_command(self):
        with patch("subprocess.run", return_value=_mock_run()) as mock_run:
            invoke_hierarchy_agent("dry_run")
        cmd = mock_run.call_args[0][0]
        assert any("dry_run" in str(c) for c in cmd)

    def test_timeout_resilience(self):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="x", timeout=300)):
            result = invoke_hierarchy_agent("verify_mro")
        assert result["success"] is False


class TestInvokeCodeValidator:
    def test_action_in_command(self):
        with patch("subprocess.run", return_value=_mock_run()) as mock_run:
            invoke_code_validator("validate")
        cmd = mock_run.call_args[0][0]
        assert any("validate" in str(c) for c in cmd)

    def test_directory_appended_when_provided(self):
        with patch("subprocess.run", return_value=_mock_run()) as mock_run:
            invoke_code_validator("validate_directory", directory="/some/dir")
        cmd = mock_run.call_args[0][0]
        assert any("/some/dir" in str(c) for c in cmd)

    def test_timeout_resilience(self):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="x", timeout=300)):
            result = invoke_code_validator("validate")
        assert result["success"] is False
