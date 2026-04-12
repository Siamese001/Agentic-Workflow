"""Test SovereignmcpgatewayagentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSovereignmcpgatewayagentAdg:
    """Test SovereignmcpgatewayagentAdg functionality."""

    def test_SovereignMCPGatewayAgent_adg_imports(self):
        """Test SovereignMCPGatewayAgent_adg module imports."""
        from agentic_core import SovereignMCPGatewayAgent_adg

        assert SovereignMCPGatewayAgent_adg is not None

    def test_SovereignMCPGatewayAgent_adg_class(self):
        """Test SovereignmcpgatewayagentAdg class exists."""
        from agentic_core import SovereignmcpgatewayagentAdg

        assert SovereignmcpgatewayagentAdg is not None

    def test_SovereignMCPGatewayAgent_adg_callable(self):
        """Test SovereignMCPGatewayAgent_adg functions are callable."""
        from agentic_core import validate_SovereignMCPGatewayAgent_adg

        assert callable(validate_SovereignMCPGatewayAgent_adg)
