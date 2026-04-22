"""Smoke tests for StructuredEngineAgent ADG exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestStructuredengineagentAdg:
    """Smoke tests for StructuredEngineAgent ADG exports."""

    def test_StructuredEngineAgent_adg_imports(self) -> None:
        """Import module export."""
        symbol = import_attr_or_skip("agentic_core", "StructuredEngineAgent_adg")
        assert symbol is not None

    def test_StructuredEngineAgent_adg_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "StructuredengineagentAdg")
        assert klass is not None

    def test_StructuredEngineAgent_adg_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_StructuredEngineAgent_adg")
        assert callable(validator)
