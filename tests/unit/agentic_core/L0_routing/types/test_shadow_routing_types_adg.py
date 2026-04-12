"""Test ShadowRoutingTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestShadowRoutingTypesAdg:
    """Test ShadowRoutingTypesAdg functionality."""

    def test_shadow_routing_types_adg_imports(self):
        """Test shadow_routing_types_adg module imports."""
        from agentic_core import shadow_routing_types_adg

        assert shadow_routing_types_adg is not None

    def test_shadow_routing_types_adg_class(self):
        """Test ShadowRoutingTypesAdg class exists."""
        from agentic_core import ShadowRoutingTypesAdg

        assert ShadowRoutingTypesAdg is not None

    def test_shadow_routing_types_adg_callable(self):
        """Test shadow_routing_types_adg functions are callable."""
        from agentic_core import validate_shadow_routing_types_adg

        assert callable(validate_shadow_routing_types_adg)
