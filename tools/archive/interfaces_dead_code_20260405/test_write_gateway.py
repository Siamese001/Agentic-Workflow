"""Test WriteGateway functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestWriteGateway:
    """Test WriteGateway functionality."""

    def test_write_gateway_imports(self):
        """Test write_gateway module imports."""
        from agentic_core import write_gateway
        assert write_gateway is not None

    def test_write_gateway_class(self):
        """Test WriteGateway class exists."""
        from agentic_core import WriteGateway
        assert WriteGateway is not None

    def test_write_gateway_callable(self):
        """Test write_gateway functions are callable."""
        from agentic_core import validate_write_gateway
        assert callable(validate_write_gateway)
