"""Test QueryEngine functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestQueryEngine:
    """Test QueryEngine functionality."""

    def test_query_engine_imports(self):
        """Test query_engine module imports."""
        from agentic_core import query_engine

        assert query_engine is not None

    def test_query_engine_class(self):
        """Test QueryEngine class exists."""
        from agentic_core import QueryEngine

        assert QueryEngine is not None

    def test_query_engine_callable(self):
        """Test query_engine functions are callable."""
        from agentic_core import validate_query_engine

        assert callable(validate_query_engine)
