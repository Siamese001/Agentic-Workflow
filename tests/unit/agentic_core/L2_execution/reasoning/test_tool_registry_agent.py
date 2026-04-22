"""Smoke tests for tool_registry_agent exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestToolRegistryAgent:
    """Smoke tests for tool_registry_agent exports."""

    def test_tool_registry_agent_imports(self) -> None:
        """Import module export."""
        module = import_attr_or_skip("agentic_core", "tool_registry_agent")
        assert module is not None

    def test_tool_registry_agent_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "ToolRegistryAgent")
        assert klass is not None

    def test_tool_registry_agent_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_tool_registry_agent")
        assert callable(validator)
