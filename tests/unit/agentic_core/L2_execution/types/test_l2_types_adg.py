"""Test L2TypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestL2TypesAdg:
    """Test L2TypesAdg functionality."""

    def test_l2_types_adg_imports(self):
        """Test l2_types_adg module imports."""
        from agentic_core import l2_types_adg

        assert l2_types_adg is not None

    def test_l2_types_adg_class(self):
        """Test L2TypesAdg class exists."""
        from agentic_core import L2TypesAdg

        assert L2TypesAdg is not None

    def test_l2_types_adg_callable(self):
        """Test l2_types_adg functions are callable."""
        from agentic_core import validate_l2_types_adg

        assert callable(validate_l2_types_adg)
