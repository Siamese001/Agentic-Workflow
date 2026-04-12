"""Test FixAllTunnelsUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFixAllTunnelsUtilAdg:
    """Test FixAllTunnelsUtilAdg functionality."""

    def test_fix_all_tunnels_util_adg_imports(self):
        """Test fix_all_tunnels_util_adg module imports."""
        from agentic_core import fix_all_tunnels_util_adg

        assert fix_all_tunnels_util_adg is not None

    def test_fix_all_tunnels_util_adg_class(self):
        """Test FixAllTunnelsUtilAdg class exists."""
        from agentic_core import FixAllTunnelsUtilAdg

        assert FixAllTunnelsUtilAdg is not None

    def test_fix_all_tunnels_util_adg_callable(self):
        """Test fix_all_tunnels_util_adg functions are callable."""
        from agentic_core import validate_fix_all_tunnels_util_adg

        assert callable(validate_fix_all_tunnels_util_adg)
