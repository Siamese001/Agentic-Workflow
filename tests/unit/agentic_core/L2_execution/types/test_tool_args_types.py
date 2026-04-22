"""Smoke tests for tool_args_types exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestToolArgsTypes:
    """Validate the tool_args_types module surfaces cleanly."""

    def test_tool_args_types_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "tool_args_types")
        assert module is not None

    def test_tool_args_types_docstring_present(self) -> None:
        """Ensure the module docstring is present."""
        module = import_attr_or_skip("agentic_core", "tool_args_types")
        assert module.__doc__ is not None

    def test_tool_args_types_public_attributes_accessible(self) -> None:
        """Ensure public attributes can be enumerated."""
        module = import_attr_or_skip("agentic_core", "tool_args_types")
        attrs = [name for name in dir(module) if not name.startswith("_")]
        assert isinstance(attrs, list)
