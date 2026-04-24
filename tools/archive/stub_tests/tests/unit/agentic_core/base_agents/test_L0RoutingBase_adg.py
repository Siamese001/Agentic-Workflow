"""Test L0routingbaseAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestL0routingbaseAdg:
    """Test L0routingbaseAdg functionality."""

    def test_L0RoutingBase_adg_imports(self):
        """Test L0RoutingBase_adg module imports."""
        from agentic_core import L0RoutingBase_adg

        assert L0RoutingBase_adg is not None

    def test_L0RoutingBase_adg_class(self):
        """Test L0routingbaseAdg class exists."""
        from agentic_core import L0routingbaseAdg

        assert L0routingbaseAdg is not None

    def test_L0RoutingBase_adg_callable(self):
        """Test L0RoutingBase_adg functions are callable."""
        from agentic_core import validate_L0RoutingBase_adg

        assert callable(validate_L0RoutingBase_adg)
