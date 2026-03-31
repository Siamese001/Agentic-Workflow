"""Test HardenedRoutingSsot functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHardenedRoutingSsot:
    """Test HardenedRoutingSsot functionality."""

    def test_hardened_routing_imports(self):
        """Test hardened routing module imports."""
        from agentic_core.L0_routing.scripts import hardened_routing_ssot
        assert hardened_routing_ssot is not None

    def test_hardened_routing_manager(self):
        """Test hardened routing manager exists."""
        from agentic_core.L0_routing.scripts.hardened_routing_ssot import HardenedRoutingManager
        assert HardenedRoutingManager is not None

    def test_validate_routing(self):
        """Test validate routing function."""
        from agentic_core.L0_routing.scripts.hardened_routing_ssot import validate_routing
        assert callable(validate_routing)
