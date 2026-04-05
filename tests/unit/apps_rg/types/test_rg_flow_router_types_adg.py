"""Test RgFlowRouterTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRgFlowRouterTypesAdg:
    """Test RgFlowRouterTypesAdg functionality."""

    def test_rg_flow_router_types_adg_imports(self):
        """Test rg_flow_router_types_adg module imports."""
        from agentic_core import rg_flow_router_types_adg
        assert rg_flow_router_types_adg is not None

    def test_rg_flow_router_types_adg_class(self):
        """Test RgFlowRouterTypesAdg class exists."""
        from agentic_core import RgFlowRouterTypesAdg
        assert RgFlowRouterTypesAdg is not None

    def test_rg_flow_router_types_adg_callable(self):
        """Test rg_flow_router_types_adg functions are callable."""
        from agentic_core import validate_rg_flow_router_types_adg
        assert callable(validate_rg_flow_router_types_adg)
