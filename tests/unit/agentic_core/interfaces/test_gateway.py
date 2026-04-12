"""Test Gateway functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGateway:
    """Test Gateway functionality."""

    def test_gateway_imports(self):
        """Test gateway module imports."""
        from agentic_core import gateway

        assert gateway is not None

    def test_gateway_class(self):
        """Test Gateway class exists."""
        from agentic_core import Gateway

        assert Gateway is not None

    def test_gateway_callable(self):
        """Test gateway functions are callable."""
        from agentic_core import validate_gateway

        assert callable(validate_gateway)
