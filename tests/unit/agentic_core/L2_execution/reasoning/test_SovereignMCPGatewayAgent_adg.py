"""Smoke tests for SovereignMCPGatewayAgent ADG exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestSovereignmcpgatewayagentAdg:
    """Smoke tests for SovereignMCPGatewayAgent ADG exports."""

    def test_SovereignMCPGatewayAgent_adg_imports(self) -> None:
        """Import module export."""
        symbol = import_attr_or_skip("agentic_core", "SovereignMCPGatewayAgent_adg")
        assert symbol is not None

    def test_SovereignMCPGatewayAgent_adg_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "SovereignmcpgatewayagentAdg")
        assert klass is not None

    def test_SovereignMCPGatewayAgent_adg_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_SovereignMCPGatewayAgent_adg")
        assert callable(validator)
