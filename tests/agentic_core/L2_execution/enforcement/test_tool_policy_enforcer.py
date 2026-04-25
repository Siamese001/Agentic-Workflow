"""Tests for ToolPolicyEnforcer - tool invocation policy enforcement."""
import pytest
from unittest.mock import Mock
from agentic_core.L2_execution.enforcement.tool_policy_enforcer import ToolPolicyEnforcer


class TestToolPolicyEnforcer:
    def test_init_with_policies(self):
        e = ToolPolicyEnforcer(policies={"allowed_tools": ["read"]})
        assert e.policies is not None

    def test_validate_allowed_tool(self):
        e = ToolPolicyEnforcer(policies={"allowed_tools": ["read"]})
        result = e.validate({"tool": "read"})
        assert result.valid is True

    def test_validate_disallowed_tool(self):
        e = ToolPolicyEnforcer(policies={"allowed_tools": ["read"]})
        result = e.validate({"tool": "delete"})
        assert result.valid is False

    def test_enforce_allowed(self):
        e = ToolPolicyEnforcer(policies={"allowed_tools": ["read"]})
        e.enforce({"tool": "read"})

    def test_enforce_blocked(self):
        e = ToolPolicyEnforcer(policies={"allowed_tools": ["read"]})
        with pytest.raises(PermissionError):
            e.enforce({"tool": "delete"})

    def test_per_tool_args_validation(self):
        e = ToolPolicyEnforcer(policies={
            "allowed_tools": ["read"],
            "tool_args": {"read": {"max_size": 1024}}
        })
        result = e.validate({"tool": "read", "args": {"size": 2048}})
        assert result.valid is False

    def test_update_policies(self):
        e = ToolPolicyEnforcer(policies={"allowed_tools": []})
        e.update_policies({"allowed_tools": ["x"]})
        assert "x" in e.policies["allowed_tools"]

    def test_get_violations(self):
        e = ToolPolicyEnforcer(policies={"allowed_tools": ["read"]})
        try:
            e.enforce({"tool": "delete"})
        except PermissionError:
            pass
        assert len(e.get_violations()) >= 1
