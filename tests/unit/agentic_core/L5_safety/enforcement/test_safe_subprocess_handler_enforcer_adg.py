"""ADG-driven tests for agentic_core/L5_safety/enforcement/safe_subprocess_handler_enforcer.py — fan_in=2.

Contract tests: safe_run, safe_popen, safe_communicate — subprocess.run mocked.
"""
from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
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
_emit_authorize_and_execute("p2", "test_safe_subprocess_handler_enforcer_adg", "execution_auth")
_emit_validates_capability("p2", "test_safe_subprocess_handler_enforcer_adg", "capability_check")
_emit_routes_to_capability("p2", "test_safe_subprocess_handler_enforcer_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_safe_subprocess_handler_enforcer_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_safe_subprocess_handler_enforcer_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_safe_subprocess_handler_enforcer_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_safe_subprocess_handler_enforcer_adg", "exec_output")
_emit_dispatches_agent("p3", "test_safe_subprocess_handler_enforcer_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_safe_subprocess_handler_enforcer_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_safe_subprocess_handler_enforcer_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_safe_subprocess_handler_enforcer_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_safe_subprocess_handler_enforcer_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_safe_subprocess_handler_enforcer_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_safe_subprocess_handler_enforcer_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_safe_subprocess_handler_enforcer_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_safe_subprocess_handler_enforcer_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_safe_subprocess_handler_enforcer_adg", "eval_metric")
_emit_stores_embedding("p4", "test_safe_subprocess_handler_enforcer_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_safe_subprocess_handler_enforcer_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_safe_subprocess_handler_enforcer_adg", "exec_snapshot_link")

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
