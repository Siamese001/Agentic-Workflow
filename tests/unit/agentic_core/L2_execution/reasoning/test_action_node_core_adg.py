"""Smoke tests for reasoning ActionNodeCore exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestActionNodeCoreAdg:
    """Smoke tests for reasoning ActionNodeCore exports."""

    def test_execute_plan(self) -> None:
        """Import execute_plan export."""
        func = import_attr_or_skip("agentic_core.L2_execution.reasoning", "execute_plan")
        assert callable(func)

    def test_ActionNodeCore_init(self) -> None:
        """Import ActionNodeCore class."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "ActionNodeCore")
        assert klass is not None

    def test_ActionNodeCore_execute_plan(self) -> None:
        """Validate ActionNodeCore.execute_plan method is present."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "ActionNodeCore")
        assert hasattr(klass, "execute_plan")
