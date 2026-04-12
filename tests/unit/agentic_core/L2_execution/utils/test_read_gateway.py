"""Test ReadGateway functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReadGateway:
    """Test ReadGateway functionality."""

    def test_read_gateway_imports(self):
        """Test read_gateway module imports."""
        from agentic_core import read_gateway

        assert read_gateway is not None

    def test_read_gateway_class(self):
        """Test ReadGateway class exists."""
        from agentic_core import ReadGateway

        assert ReadGateway is not None

    def test_read_gateway_callable(self):
        """Test read_gateway functions are callable."""
        from agentic_core import validate_read_gateway

        assert callable(validate_read_gateway)
