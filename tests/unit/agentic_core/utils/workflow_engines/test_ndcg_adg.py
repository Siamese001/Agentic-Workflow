"""Test NdcgAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestNdcgAdg:
    """Test NdcgAdg functionality."""

    def test_ndcg_adg_imports(self):
        """Test ndcg_adg module imports."""
        from agentic_core import ndcg_adg

        assert ndcg_adg is not None

    def test_ndcg_adg_class(self):
        """Test NdcgAdg class exists."""
        from agentic_core import NdcgAdg

        assert NdcgAdg is not None

    def test_ndcg_adg_callable(self):
        """Test ndcg_adg functions are callable."""
        from agentic_core import validate_ndcg_adg

        assert callable(validate_ndcg_adg)
