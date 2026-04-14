"""Smoke tests for reasoning ActionNode exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestActionNodeAdg:
    """Smoke tests for reasoning ActionNode exports."""

    def test_act(self) -> None:
        """Import act export."""
        func = import_attr_or_skip("agentic_core.L2_execution.reasoning", "act")
        assert callable(func)

    def test_act_simple(self) -> None:
        """Import act_simple export."""
        func = import_attr_or_skip("agentic_core.L2_execution.reasoning", "act_simple")
        assert callable(func)

    def test_ActionNode_init(self) -> None:
        """Import ActionNode class."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "ActionNode")
        assert klass is not None

    def test_ActionNode_act(self) -> None:
        """Validate ActionNode.act method is present."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "ActionNode")
        assert hasattr(klass, "act")
