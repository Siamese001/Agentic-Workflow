"""Smoke tests for ToolsmithAgent ADG exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestToolsmithagentAdg:
    """Smoke tests for ToolsmithAgent ADG exports."""

    def test_ToolsmithAgent_adg_imports(self) -> None:
        """Import module export."""
        symbol = import_attr_or_skip("agentic_core", "ToolsmithAgent_adg")
        assert symbol is not None

    def test_ToolsmithAgent_adg_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "ToolsmithagentAdg")
        assert klass is not None

    def test_ToolsmithAgent_adg_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_ToolsmithAgent_adg")
        assert callable(validator)
