"""Test L0routingbase functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestL0routingbase:
    """Test L0routingbase functionality."""

    def test_L0RoutingBase_imports(self):
        """Test L0RoutingBase module imports."""
        from agentic_core import L0RoutingBase

        assert L0RoutingBase is not None

    def test_L0RoutingBase_class(self):
        """Test L0routingbase class exists."""
        from agentic_core import L0routingbase

        assert L0routingbase is not None

    def test_L0RoutingBase_callable(self):
        """Test L0RoutingBase functions are callable."""
        from agentic_core import validate_L0RoutingBase

        assert callable(validate_L0RoutingBase)
