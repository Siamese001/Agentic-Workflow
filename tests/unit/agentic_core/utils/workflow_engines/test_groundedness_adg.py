"""Test GroundednessAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGroundednessAdg:
    """Test GroundednessAdg functionality."""

    def test_groundedness_adg_imports(self):
        """Test groundedness_adg module imports."""
        from agentic_core import groundedness_adg

        assert groundedness_adg is not None

    def test_groundedness_adg_class(self):
        """Test GroundednessAdg class exists."""
        from agentic_core import GroundednessAdg

        assert GroundednessAdg is not None

    def test_groundedness_adg_callable(self):
        """Test groundedness_adg functions are callable."""
        from agentic_core import validate_groundedness_adg

        assert callable(validate_groundedness_adg)
