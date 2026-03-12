"""ADG-driven tests for L2_execution/types/mcp_security_types.py — fan_in=0."""
from __future__ import annotations

import pytest

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
