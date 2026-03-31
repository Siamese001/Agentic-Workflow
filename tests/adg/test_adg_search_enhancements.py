"""Test ADG search enhancements functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgSearchEnhancements:
    """Test ADG search enhancements functionality."""

    def test_search_enhancements_imports(self):
        """Test search enhancements module imports."""
        from tools.adg import adg_redis_query
        assert adg_redis_query is not None

    def test_adg_search_function_exists(self):
        """Test ADG search function exists."""
        from tools.adg.adg_redis_query import search_nodes
        assert callable(search_nodes)

    def test_adg_query_bridge_exists(self):
        """Test ADG query bridge exists."""
        from tools.adg.adg_query_bridge import query_bridge
        assert callable(query_bridge)
