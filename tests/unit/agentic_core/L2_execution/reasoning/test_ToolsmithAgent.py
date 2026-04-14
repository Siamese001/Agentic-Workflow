"""Smoke tests for ToolsmithAgent-related exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestToolsmithAgent:
    """Smoke tests for ToolsmithAgent-related exports."""

    def test_get_ToolsmithAgent(self) -> None:
        """Import getter export."""
        func = import_attr_or_skip("agentic_core.L2_execution.reasoning", "get_ToolsmithAgent")
        assert callable(func)

    def test_initialize_ToolsmithAgent(self) -> None:
        """Import initializer export."""
        func = import_attr_or_skip("agentic_core.L2_execution.reasoning", "initialize_ToolsmithAgent")
        assert callable(func)

    def test_ToolSpec_init(self) -> None:
        """Import ToolSpec class."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "ToolSpec")
        assert klass is not None

    def test_ToolSpec_to_dict(self) -> None:
        """Validate ToolSpec.to_dict method is present."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "ToolSpec")
        assert hasattr(klass, "to_dict")

    def test_GeneratedTool_init(self) -> None:
        """Import GeneratedTool class."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "GeneratedTool")
        assert klass is not None

    def test_GeneratedTool_to_dict(self) -> None:
        """Validate GeneratedTool.to_dict method is present."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "GeneratedTool")
        assert hasattr(klass, "to_dict")
