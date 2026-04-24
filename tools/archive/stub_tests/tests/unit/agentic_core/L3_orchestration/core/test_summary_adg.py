"""Test SummaryAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSummaryAdg:
    """Test SummaryAdg functionality."""

    def test_summary_adg_imports(self):
        """Test summary_adg module imports."""
        from agentic_core import summary_adg

        assert summary_adg is not None

    def test_summary_adg_class(self):
        """Test SummaryAdg class exists."""
        from agentic_core import SummaryAdg

        assert SummaryAdg is not None

    def test_summary_adg_callable(self):
        """Test summary_adg functions are callable."""
        from agentic_core import validate_summary_adg

        assert callable(validate_summary_adg)
