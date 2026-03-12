"""ADG-driven tests for agentic_core/L5_safety/enforcement/mcp_sovereign_authority_enforcer.py — fan_in=2.

Contract tests: MCPSovereignAuthority — breach recording, authorization, tool auditing.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.mcp_sovereign_authority_enforcer import (
    MCPSovereignAuthority,
    mcp_authority,
)


class TestMCPSovereignAuthorityImport:
    def test_class_importable(self):
        assert callable(MCPSovereignAuthority)

    def test_module_level_instance_exists(self):
        assert isinstance(mcp_authority, MCPSovereignAuthority)


class TestMCPSovereignAuthorityInitialState:
    def test_fresh_instance_authorized(self):
        a = MCPSovereignAuthority()
        assert a.is_authorized() is True

    def test_fresh_violation_count_zero(self):
        a = MCPSovereignAuthority()
        assert a.violation_count == 0

    def test_fresh_breach_log_empty(self):
        a = MCPSovereignAuthority()
        assert a.breach_log == []

    def test_fresh_not_locked(self):
        a = MCPSovereignAuthority()
        assert a.is_locked is False


class TestMCPSovereignAuthorityBreachRecording:
    def test_record_breach_increments_count(self):
        a = MCPSovereignAuthority()
        a.record_breach("test violation")
        assert a.violation_count == 1

    def test_record_breach_adds_to_log(self):
        a = MCPSovereignAuthority()
        a.record_breach("violation A")
        assert len(a.breach_log) == 1
        assert a.breach_log[0]["error"] == "violation A"

    def test_breach_log_entry_has_timestamp(self):
        a = MCPSovereignAuthority()
        a.record_breach("test")
        assert "timestamp" in a.breach_log[0]

    def test_six_breaches_locks_authority(self):
        a = MCPSovereignAuthority()
        for i in range(6):
            a.record_breach(f"breach {i}")
        assert a.is_authorized() is False


class TestMCPSovereignAuthorityAuthorizeToolCall:
    def test_safe_tool_passes(self):
        a = MCPSovereignAuthority()
        a.authorize_tool_call("read_file", {"path": "docs/readme.md"})  # should not raise

    def test_forbidden_sdk_raises_permission_error(self):
        a = MCPSovereignAuthority()
        with pytest.raises(PermissionError, match="Sovereignty Shield"):
            a.authorize_tool_call("openai", {})

    def test_anthropic_sdk_blocked(self):
        a = MCPSovereignAuthority()
        with pytest.raises(PermissionError):
            a.authorize_tool_call("anthropic", {})

    def test_sequential_thinking_within_limit_passes(self):
        a = MCPSovereignAuthority()
        a.authorize_tool_call("sequential_thinking", {"max_steps": 5, "Task": "analyze code"})

    def test_sequential_thinking_over_limit_raises(self):
        a = MCPSovereignAuthority()
        with pytest.raises(ValueError, match="15 steps"):
            a.authorize_tool_call("sequential_thinking", {"max_steps": 20, "Task": "analyze"})
