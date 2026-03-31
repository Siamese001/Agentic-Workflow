"""Test ManagerRouting functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestManagerRouting:
    """Test ManagerRouting functionality."""

    def test_manager_routing_imports(self):
        """Test manager_routing module imports."""
        from agentic_core import manager_routing
        assert manager_routing is not None

    def test_manager_routing_class(self):
        """Test ManagerRouting class exists."""
        from agentic_core import ManagerRouting
        assert ManagerRouting is not None

    def test_manager_routing_callable(self):
        """Test manager_routing functions are callable."""
        from agentic_core import validate_manager_routing
        assert callable(validate_manager_routing)
