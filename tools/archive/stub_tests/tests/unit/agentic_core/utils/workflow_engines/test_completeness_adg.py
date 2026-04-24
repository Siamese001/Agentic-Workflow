"""Test CompletenessAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCompletenessAdg:
    """Test CompletenessAdg functionality."""

    def test_completeness_adg_imports(self):
        """Test completeness_adg module imports."""
        from agentic_core import completeness_adg

        assert completeness_adg is not None

    def test_completeness_adg_class(self):
        """Test CompletenessAdg class exists."""
        from agentic_core import CompletenessAdg

        assert CompletenessAdg is not None

    def test_completeness_adg_callable(self):
        """Test completeness_adg functions are callable."""
        from agentic_core import validate_completeness_adg

        assert callable(validate_completeness_adg)
