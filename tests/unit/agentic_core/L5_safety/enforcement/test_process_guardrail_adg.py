"""ADG-driven tests for agentic_core/L5_safety/enforcement/process_guardrail.py — fan_in=2.

Contract tests: BLOCKED_COMMANDS, SecurityViolation, ProcessGuard singleton.
"""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_process_guardrail_adg")
_emit_applies_guardrail("p0", "test_process_guardrail_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_process_guardrail_adg", "policy_binding")
_emit_snapshots_state("p0", "test_process_guardrail_adg", "state_snapshot")
emit_replay_key("p0", "test_process_guardrail_adg")
emit_determinism_digest("p0", "test_process_guardrail_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.process_guardrail import (
    BLOCKED_COMMANDS,
    ProcessGuard,
    SecurityViolation,
)


class TestBlockedCommands:
    def test_is_frozenset(self):
        assert isinstance(BLOCKED_COMMANDS, frozenset)

    def test_pip_blocked(self):
        assert "pip" in BLOCKED_COMMANDS

    def test_rm_blocked(self):
        assert "rm" in BLOCKED_COMMANDS

    def test_sudo_blocked(self):
        assert "sudo" in BLOCKED_COMMANDS

    def test_powershell_blocked(self):
        assert "powershell" in BLOCKED_COMMANDS

    def test_npm_blocked(self):
        assert "npm" in BLOCKED_COMMANDS

    def test_python_not_blocked(self):
        assert "python" not in BLOCKED_COMMANDS

    def test_echo_not_blocked(self):
        assert "echo" not in BLOCKED_COMMANDS


class TestSecurityViolation:
    def test_is_exception(self):
        assert issubclass(SecurityViolation, Exception)

    def test_attributes_stored(self):
        err = SecurityViolation(command=["pip", "install"], reason="blocked package manager")
        assert err.command == ["pip", "install"]
        assert err.reason == "blocked package manager"

    def test_message_contains_reason(self):
        err = SecurityViolation(["rm", "-rf"], "destructive command")
        assert "destructive command" in str(err)

    def test_can_be_raised(self):
        with pytest.raises(SecurityViolation):
            raise SecurityViolation(["sudo"], "privilege escalation")


class TestProcessGuardSingleton:
    def test_singleton_same_instance(self):
        g1 = ProcessGuard.get_instance()
        g2 = ProcessGuard.get_instance()
        assert g1 is g2

    def test_new_returns_same_instance(self):
        g1 = ProcessGuard()
        g2 = ProcessGuard()
        assert g1 is g2


class TestProcessGuardValidate:
    def _fresh_guard(self) -> ProcessGuard:
        return ProcessGuard.get_instance()

    def test_safe_command_passes(self):
        guard = self._fresh_guard()
        guard.validate_command(["python", "script.py"])  # must not raise

    def test_blocked_command_raises(self):
        guard = self._fresh_guard()
        with pytest.raises(SecurityViolation):
            guard.validate_command(["pip", "install", "requests"])

    def test_rm_command_raises(self):
        guard = self._fresh_guard()
        with pytest.raises(SecurityViolation):
            guard.validate_command(["rm", "-rf", "/tmp/test"])

    def test_python_command_passes(self):
        guard = self._fresh_guard()
        guard.validate_command(["python", "-c", "print('hello')"])


class TestProcessGuardPidRegistry:
    def _guard(self) -> ProcessGuard:
        return ProcessGuard.get_instance()

    def test_register_and_get(self):
        guard = self._guard()
        guard.register_pid(99999)
        assert 99999 in guard.get_active_pids()
        guard.unregister_pid(99999)

    def test_unregister_removes_pid(self):
        guard = self._guard()
        guard.register_pid(88888)
        guard.unregister_pid(88888)
        assert 88888 not in guard.get_active_pids()

    def test_get_active_pids_returns_copy(self):
        guard = self._guard()
        pids = guard.get_active_pids()
        pids.add(-1)
        assert -1 not in guard.get_active_pids()
