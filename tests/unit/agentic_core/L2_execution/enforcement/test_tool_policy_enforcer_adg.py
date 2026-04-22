"""Smoke tests for enforcement tool policy enforcer exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip, import_module_or_skip


@pytest.mark.unit
class TestToolPolicyEnforcerAdg:
    """Validate expected public enforcement exports without invoking live behavior."""

    def test_get_tool_policy_enforcer(self) -> None:
        """Import the getter export."""
        getter = import_attr_or_skip("agentic_core.L2_execution.enforcement", "get_tool_policy_enforcer")
        assert callable(getter)

    def test_set_tool_policy_enforcer(self) -> None:
        """Import the setter export."""
        setter = import_attr_or_skip("agentic_core.L2_execution.enforcement", "set_tool_policy_enforcer")
        assert callable(setter)

    def test_tool_policy_enforcer_class(self) -> None:
        """Import the ToolPolicyEnforcer class export."""
        klass = import_attr_or_skip("agentic_core.L2_execution.enforcement", "ToolPolicyEnforcer")
        assert klass is not None

    def test_enforcement_module_importable(self) -> None:
        """Import the enforcement module itself."""
        module = import_module_or_skip("agentic_core.L2_execution.enforcement")
        assert module is not None
