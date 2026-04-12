"""Test CidRegistry functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCidRegistry:
    """Test CidRegistry functionality."""

    def test_cid_registry_imports(self):
        """Test CID registry module imports."""
        from agentic_core.L2_execution import cid_registry

        assert cid_registry is not None

    def test_cid_registry_class(self):
        """Test CID registry class exists."""
        from agentic_core.L2_execution.cid_registry import CIDRegistry

        assert CIDRegistry is not None

    def test_register_cid(self):
        """Test register CID function."""
        from agentic_core.L2_execution.cid_registry import register_cid

        assert callable(register_cid)
