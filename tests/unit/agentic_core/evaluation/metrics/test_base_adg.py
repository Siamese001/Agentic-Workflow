"""Test BaseAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBaseAdg:
    """Test BaseAdg functionality."""

    def test_base_adg_imports(self):
        """Test base_adg module imports."""
        from agentic_core import base_adg

        assert base_adg is not None

    def test_base_adg_class(self):
        """Test BaseAdg class exists."""
        from agentic_core import BaseAdg

        assert BaseAdg is not None

    def test_base_adg_callable(self):
        """Test base_adg functions are callable."""
        from agentic_core import validate_base_adg

        assert callable(validate_base_adg)
