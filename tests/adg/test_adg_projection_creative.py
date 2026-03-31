"""Test ADG projection creative functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgProjectionCreative:
    """Test ADG projection creative functionality."""

    def test_projection_creative_imports(self):
        """Test projection creative module imports."""
        from tools.adg import adg_redis_query
        assert adg_redis_query is not None

    def test_adg_redis_projection_exists(self):
        """Test ADG Redis projection exists."""
        from tools.adg.adg_redis_query import project_to_redis
        assert callable(project_to_redis)

    def test_adg_sqlite_projection_exists(self):
        """Test ADG SQLite projection exists."""
        from tools.adg.adg_redis_query import project_to_sqlite
        assert callable(project_to_sqlite)
