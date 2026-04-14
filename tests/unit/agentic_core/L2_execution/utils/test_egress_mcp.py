"""Smoke tests for egress_mcp exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestEgressMcp:
    """Smoke tests for egress_mcp exports."""

    def test_egress_mcp_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "egress_mcp")
        assert module is not None

    def test_egress_mcp_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "EgressMcp")
        assert klass is not None

    def test_egress_mcp_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_egress_mcp")
        assert callable(validator)
