"""Test RoutingContractsTypes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRoutingContractsTypes:
    """Test RoutingContractsTypes functionality."""

    def test_routing_contracts_types_imports(self):
        """Test routing_contracts_types module imports."""
        from agentic_core import routing_contracts_types

        assert routing_contracts_types is not None

    def test_routing_contracts_types_class(self):
        """Test RoutingContractsTypes class exists."""
        from agentic_core import RoutingContractsTypes

        assert RoutingContractsTypes is not None

    def test_routing_contracts_types_callable(self):
        """Test routing_contracts_types functions are callable."""
        from agentic_core import validate_routing_contracts_types

        assert callable(validate_routing_contracts_types)
