"""Test Schema functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSchema:
    """Test Schema functionality."""

    def test_schema_imports(self):
        """Test schema module imports."""
        from agentic_core import schema
        assert schema is not None

    def test_schema_class(self):
        """Test Schema class exists."""
        from agentic_core import Schema
        assert Schema is not None

    def test_schema_callable(self):
        """Test schema functions are callable."""
        from agentic_core import validate_schema
        assert callable(validate_schema)
