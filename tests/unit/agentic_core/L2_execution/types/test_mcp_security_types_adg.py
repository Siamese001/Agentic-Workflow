"""ADG-driven tests for L2_execution/types/mcp_security_types.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_mcp_security_types_adg")
_emit_applies_guardrail("p0", "test_mcp_security_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_mcp_security_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_mcp_security_types_adg", "state_snapshot")
emit_replay_key("p0", "test_mcp_security_types_adg")
emit_determinism_digest("p0", "test_mcp_security_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.mcp_security_types import MCPSecurityViolation


class TestMCPSecurityViolation:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(MCPSecurityViolation)

    def test_creates(self):
        v = MCPSecurityViolation(
            rule="no_shell_exec",
            severity="error",
            tool_name="shell",
            description="shell execution blocked",
        )
        assert v.rule == "no_shell_exec"
        assert v.severity == "error"
        assert v.blocked is False

    def test_blocked_flag(self):
        v = MCPSecurityViolation(
            rule="no_shell_exec",
            severity="critical",
            tool_name="bash",
            description="blocked",
            blocked=True,
        )
        assert v.blocked is True
