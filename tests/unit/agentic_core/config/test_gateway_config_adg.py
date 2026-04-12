"""Test GatewayConfigAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGatewayConfigAdg:
    """Test GatewayConfigAdg functionality."""

    def test_gateway_config_adg_imports(self):
        """Test gateway_config_adg module imports."""
        from agentic_core import gateway_config_adg

        assert gateway_config_adg is not None

    def test_gateway_config_adg_class(self):
        """Test GatewayConfigAdg class exists."""
        from agentic_core import GatewayConfigAdg

        assert GatewayConfigAdg is not None

    def test_gateway_config_adg_callable(self):
        """Test gateway_config_adg functions are callable."""
        from agentic_core import validate_gateway_config_adg

        assert callable(validate_gateway_config_adg)
