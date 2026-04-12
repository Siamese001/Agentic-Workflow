"""Test Builder functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBuilder:
    """Test Builder functionality."""

    def test_builder_imports(self):
        """Test builder module imports."""
        from agentic_core import builder

        assert builder is not None

    def test_builder_class(self):
        """Test Builder class exists."""
        from agentic_core import Builder

        assert Builder is not None

    def test_builder_callable(self):
        """Test builder functions are callable."""
        from agentic_core import validate_builder

        assert callable(validate_builder)
