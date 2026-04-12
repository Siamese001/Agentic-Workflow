"""Test MrrAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMrrAdg:
    """Test MrrAdg functionality."""

    def test_mrr_adg_imports(self):
        """Test mrr_adg module imports."""
        from agentic_core import mrr_adg

        assert mrr_adg is not None

    def test_mrr_adg_class(self):
        """Test MrrAdg class exists."""
        from agentic_core import MrrAdg

        assert MrrAdg is not None

    def test_mrr_adg_callable(self):
        """Test mrr_adg functions are callable."""
        from agentic_core import validate_mrr_adg

        assert callable(validate_mrr_adg)
