"""Test SQLite memory store functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSqliteMemoryStore:
    """Test SQLite memory store functionality."""

    def test_sqlite_memory_store_imports(self):
        """Test SQLite memory store module imports."""
        from system_learning.memory import sqlite_store
        assert sqlite_store is not None

    def test_sqlite_store_class(self):
        """Test SQLite store class exists."""
        from system_learning.memory.sqlite_store import SQLiteMemoryStore
        assert SQLiteMemoryStore is not None

    def test_sqlite_store_init(self):
        """Test SQLite store initialization."""
        from system_learning.memory.sqlite_store import SQLiteMemoryStore
        store = SQLiteMemoryStore(db_path=":memory:")
        assert store is not None
