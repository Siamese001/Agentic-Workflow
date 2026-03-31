"""Test WriteGatewayAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestWriteGatewayAdg:
    """Test WriteGatewayAdg functionality."""

    def test_write_gateway_adg_imports(self):
        """Test write_gateway_adg module imports."""
        from agentic_core import write_gateway_adg
        assert write_gateway_adg is not None

    def test_write_gateway_adg_class(self):
        """Test WriteGatewayAdg class exists."""
        from agentic_core import WriteGatewayAdg
        assert WriteGatewayAdg is not None

    def test_write_gateway_adg_callable(self):
        """Test write_gateway_adg functions are callable."""
        from agentic_core import validate_write_gateway_adg
        assert callable(validate_write_gateway_adg)
