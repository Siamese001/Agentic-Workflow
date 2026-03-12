"""ADG-driven tests for agentic_core/L2_execution/tools/safe_subprocess.py — fan_in=3.

Contract tests: safe_subprocess_run, safe_subprocess_call, safe_subprocess_check_output.
subprocess.run is mocked to avoid actual process execution.
"""
from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.tools.safe_subprocess import (
    safe_subprocess_call,
    safe_subprocess_check_output,
    safe_subprocess_run,
)


def _make_completed(returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


class TestSafeSubprocessRun:
    def test_non_dangerous_command_passes(self):
        with patch("subprocess.run", return_value=_make_completed()) as mock_run:
            result = safe_subprocess_run(["echo", "hello"])
            mock_run.assert_called_once()
            assert result.returncode == 0

    def test_non_list_argv_raises_type_error(self):
        with pytest.raises(TypeError, match="argv must be a list"):
            safe_subprocess_run("not a list")  # type: ignore[arg-type]

    def test_capture_output_forwarded(self):
        with patch("subprocess.run", return_value=_make_completed(stdout="output")) as mock_run:
            safe_subprocess_run(["echo", "hi"], capture_output=True, text=True)
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs.get("capture_output") is True
            assert call_kwargs.get("text") is True

    def test_dangerous_command_without_protected_root_passes(self):
        """Without a cwd, dangerous commands should pass through."""
        with patch("subprocess.run", return_value=_make_completed()) as mock_run:
            result = safe_subprocess_run(["git", "status"])
            mock_run.assert_called_once()
            assert result.returncode == 0

    def test_allow_protected_root_mutation_bypasses_check(self):
        with patch("subprocess.run", return_value=_make_completed()) as mock_run:
            result = safe_subprocess_run(["git", "commit"], allow_protected_root_mutation=True)
            mock_run.assert_called_once()
            assert result.returncode == 0

    def test_returns_completed_process(self):
        with patch("subprocess.run", return_value=_make_completed()):
            result = safe_subprocess_run(["echo"])
            assert isinstance(result, subprocess.CompletedProcess)


class TestSafeSubprocessCall:
    def test_returns_returncode(self):
        with patch("subprocess.run", return_value=_make_completed(returncode=0)):
            code = safe_subprocess_call(["echo", "hi"])
            assert code == 0

    def test_non_zero_returncode(self):
        with patch("subprocess.run", return_value=_make_completed(returncode=1)):
            code = safe_subprocess_call(["false"])
            assert code == 1

    def test_non_list_raises(self):
        with pytest.raises(TypeError):
            safe_subprocess_call("not a list")  # type: ignore[arg-type]


class TestSafeSubprocessCheckOutput:
    def test_returns_stdout(self):
        with patch("subprocess.run", return_value=_make_completed(stdout="hello\n")):
            output = safe_subprocess_check_output(["echo", "hello"], text=True)
            assert output == "hello\n"

    def test_empty_stdout_returns_empty(self):
        with patch("subprocess.run", return_value=_make_completed(stdout="")):
            output = safe_subprocess_check_output(["true"])
            assert output == ""

    def test_non_list_raises(self):
        with pytest.raises(TypeError):
            safe_subprocess_check_output("not a list")  # type: ignore[arg-type]
