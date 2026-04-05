"""Test NetworkOps functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestNetworkOps:
    """Test NetworkOps functionality."""

    def test_network_ops_imports(self):
        """Test network_ops module imports."""
        from agentic_core import network_ops
        assert network_ops is not None

    def test_network_ops_class(self):
        """Test NetworkOps class exists."""
        from agentic_core import NetworkOps
        assert NetworkOps is not None

    def test_network_ops_callable(self):
        """Test network_ops functions are callable."""
        from agentic_core import validate_network_ops
        assert callable(validate_network_ops)
