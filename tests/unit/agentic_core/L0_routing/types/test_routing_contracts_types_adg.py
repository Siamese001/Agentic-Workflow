"""Test RoutingContractsTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRoutingContractsTypesAdg:
    """Test RoutingContractsTypesAdg functionality."""

    def test_routing_contracts_types_adg_imports(self):
        """Test routing_contracts_types_adg module imports."""
        from agentic_core import routing_contracts_types_adg

        assert routing_contracts_types_adg is not None

    def test_routing_contracts_types_adg_class(self):
        """Test RoutingContractsTypesAdg class exists."""
        from agentic_core import RoutingContractsTypesAdg

        assert RoutingContractsTypesAdg is not None

    def test_routing_contracts_types_adg_callable(self):
        """Test routing_contracts_types_adg functions are callable."""
        from agentic_core import validate_routing_contracts_types_adg

        assert callable(validate_routing_contracts_types_adg)
