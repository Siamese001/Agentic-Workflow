"""ADG-driven tests for agentic_core/L5_safety/enforcement/safe_subprocess_handler_enforcer.py — fan_in=2.

Contract tests: safe_run, safe_popen, safe_communicate — subprocess.run mocked.
"""
from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_safe_subprocess_handler_enforcer_adg")
_emit_applies_guardrail("p0", "test_safe_subprocess_handler_enforcer_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_safe_subprocess_handler_enforcer_adg", "policy_binding")
_emit_snapshots_state("p0", "test_safe_subprocess_handler_enforcer_adg", "state_snapshot")
emit_replay_key("p0", "test_safe_subprocess_handler_enforcer_adg")
emit_determinism_digest("p0", "test_safe_subprocess_handler_enforcer_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.process_guardrail import SecurityViolation
from agentic_core.L5_safety.enforcement.safe_subprocess_handler_enforcer import (
    safe_communicate,
    safe_popen,
    safe_run,
)


def _make_completed(returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


class TestSafeRunImport:
    def test_callable(self):
        assert callable(safe_run)

    def test_safe_popen_callable(self):
        assert callable(safe_popen)

    def test_safe_communicate_callable(self):
        assert callable(safe_communicate)


class TestSafeRun:
    def test_safe_command_passes(self):
        with patch("subprocess.run", return_value=_make_completed()) as mock_run:
            result = safe_run(["python", "--version"], capture_output=True, text=True)
            mock_run.assert_called_once()
            assert result.returncode == 0

    def test_blocked_command_raises(self):
        with pytest.raises(SecurityViolation):
            safe_run(["pip", "install", "requests"])

    def test_returns_completed_process(self):
        with patch("subprocess.run", return_value=_make_completed(stdout="hello")):
            result = safe_run(["echo", "hello"], capture_output=True, text=True, sanitize_output=False)
            assert isinstance(result, subprocess.CompletedProcess)

    def test_sanitize_output_truncates_long_stdout(self):
        long_output = "x" * 5000
        with patch("subprocess.run", return_value=_make_completed(stdout=long_output)):
            result = safe_run(["echo"], capture_output=True, text=True, sanitize_output=True, max_output_chars=100)
            assert len(result.stdout) <= 200  # sanitized


class TestSafePopen:
    def test_blocked_command_raises(self):
        with pytest.raises(SecurityViolation):
            safe_popen(["rm", "-rf", "/"])

    def test_safe_command_registers_pid(self):
        mock_process = MagicMock()
        mock_process.pid = 12345
        with patch("subprocess.Popen", return_value=mock_process):
            proc = safe_popen(["python", "-c", "pass"])
            assert proc is mock_process
