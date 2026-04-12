"""Test SeamsAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSeamsAdg:
    """Test SeamsAdg functionality."""

    def test_seams_adg_imports(self):
        """Test seams_adg module imports."""
        from agentic_core import seams_adg

        assert seams_adg is not None

    def test_seams_adg_class(self):
        """Test SeamsAdg class exists."""
        from agentic_core import SeamsAdg

        assert SeamsAdg is not None

    def test_seams_adg_callable(self):
        """Test seams_adg functions are callable."""
        from agentic_core import validate_seams_adg

        assert callable(validate_seams_adg)
