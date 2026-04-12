"""Test RecallAtKAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRecallAtKAdg:
    """Test RecallAtKAdg functionality."""

    def test_recall_at_k_adg_imports(self):
        """Test recall_at_k_adg module imports."""
        from agentic_core import recall_at_k_adg

        assert recall_at_k_adg is not None

    def test_recall_at_k_adg_class(self):
        """Test RecallAtKAdg class exists."""
        from agentic_core import RecallAtKAdg

        assert RecallAtKAdg is not None

    def test_recall_at_k_adg_callable(self):
        """Test recall_at_k_adg functions are callable."""
        from agentic_core import validate_recall_at_k_adg

        assert callable(validate_recall_at_k_adg)
