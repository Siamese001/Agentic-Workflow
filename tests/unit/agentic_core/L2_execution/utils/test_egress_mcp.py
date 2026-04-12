"""Test EgressMcp functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEgressMcp:
    """Test EgressMcp functionality."""

    def test_egress_mcp_imports(self):
        """Test egress_mcp module imports."""
        from agentic_core import egress_mcp

        assert egress_mcp is not None

    def test_egress_mcp_class(self):
        """Test EgressMcp class exists."""
        from agentic_core import EgressMcp

        assert EgressMcp is not None

    def test_egress_mcp_callable(self):
        """Test egress_mcp functions are callable."""
        from agentic_core import validate_egress_mcp

        assert callable(validate_egress_mcp)
