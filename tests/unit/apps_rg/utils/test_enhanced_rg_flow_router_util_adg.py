"""Test EnhancedRgFlowRouterUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEnhancedRgFlowRouterUtilAdg:
    """Test EnhancedRgFlowRouterUtilAdg functionality."""

    def test_enhanced_rg_flow_router_util_adg_imports(self):
        """Test enhanced_rg_flow_router_util_adg module imports."""
        from agentic_core import enhanced_rg_flow_router_util_adg
        assert enhanced_rg_flow_router_util_adg is not None

    def test_enhanced_rg_flow_router_util_adg_class(self):
        """Test EnhancedRgFlowRouterUtilAdg class exists."""
        from agentic_core import EnhancedRgFlowRouterUtilAdg
        assert EnhancedRgFlowRouterUtilAdg is not None

    def test_enhanced_rg_flow_router_util_adg_callable(self):
        """Test enhanced_rg_flow_router_util_adg functions are callable."""
        from agentic_core import validate_enhanced_rg_flow_router_util_adg
        assert callable(validate_enhanced_rg_flow_router_util_adg)
