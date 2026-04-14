"""Smoke tests for tool_executor exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestToolExecutor:
    """Smoke tests for tool_executor exports."""

    def test_tool_executor_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "tool_executor")
        assert module is not None

    def test_tool_executor_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "ToolExecutor")
        assert klass is not None

    def test_tool_executor_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_tool_executor")
        assert callable(validator)
