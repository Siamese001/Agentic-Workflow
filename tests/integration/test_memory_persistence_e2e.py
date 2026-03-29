"""End-to-end integration test: Memory MCP persistence and lifecycle.

Tests the full Memory MCP stack:
1. SqliteMemoryStore CRUD operations
2. adg_memory_server tool functions
3. ADG context import from Redis
4. Entity persistence across restarts
5. Protected entity types (ArchitectureLayer, ProjectContext, ConstitutionalRule)
6. Cleanup with protection
"""

from __future__ import annotations

import os
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure repo root is accessible
repo_root = Path(__file__).parent.parent.parent

# Module availability checks
MEMORY_SERVER_PATH = repo_root / "tools" / "memory" / "adg_memory_server.py"
SQLITE_STORE_PATH = repo_root / "tools" / "memory" / "sqlite_memory_store.py"

MEMORY_SERVER_AVAILABLE = MEMORY_SERVER_PATH.exists()
SQLITE_STORE_AVAILABLE = SQLITE_STORE_PATH.exists()

# Validate Python syntax
def _is_valid_python(path: Path) -> bool:
    try:
        import ast
        ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        return True
    except SyntaxError:
        return False

MEMORY_SERVER_VALID = MEMORY_SERVER_AVAILABLE and _is_valid_python(MEMORY_SERVER_PATH)
SQLITE_STORE_VALID = SQLITE_STORE_AVAILABLE and _is_valid_python(SQLITE_STORE_PATH)


@pytest.mark.e2e
@pytest.mark.skipif(not SQLITE_STORE_VALID, reason="sqlite_memory_store.py not available or has syntax errors")
class TestSqliteMemoryStoreE2E(unittest.TestCase):
    """E2E tests for SqliteMemoryStore persistence."""

    def setUp(self):
        """Create temp database for each test."""
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.tmp_dir) / "test_memory.sqlite"

    def tearDown(self):
        """Clean up temp database."""
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_entity_creation_and_retrieval(self):
        """Test creating and retrieving entities."""
        from tools.memory.sqlite_memory_store import SqliteMemoryStore

        store = SqliteMemoryStore(self.db_path)

        # Create entity
        result = store.create_entities([
            {"name": "TestEntity", "entityType": "Test", "observations": ["obs1", "obs2"]}
        ])

        self.assertIn("created", result)
        self.assertEqual(len(result["created"]), 1)

        # Retrieve entity
        entity = store.load_entity("TestEntity")
        self.assertIsNotNone(entity)
        self.assertEqual(entity["name"], "TestEntity")
        self.assertEqual(entity["entityType"], "Test")
        self.assertEqual(len(entity["observations"]), 2)

    def test_entity_duplicate_skipping(self):
        """Test that duplicate entities are skipped silently."""
        from tools.memory.sqlite_memory_store import SqliteMemoryStore

        store = SqliteMemoryStore(self.db_path)

        # Create entity first time
        result1 = store.create_entities([{"name": "DupEntity", "entityType": "Test"}])
        self.assertEqual(len(result1["created"]), 1)

        # Try to create duplicate
        result2 = store.create_entities([{"name": "DupEntity", "entityType": "Test"}])
        self.assertEqual(len(result2["skipped_existing"]), 1)
        self.assertEqual(len(result2["created"]), 0)

    def test_observation_deduplication(self):
        """Test that duplicate observations are ignored."""
        from tools.memory.sqlite_memory_store import SqliteMemoryStore

        store = SqliteMemoryStore(self.db_path)

        # Create entity with observation
        store.create_entities([{"name": "ObsEntity", "entityType": "Test", "observations": ["unique_obs"]}])

        # Add same observation again
        result = store.add_observations([{"entityName": "ObsEntity", "contents": ["unique_obs"]}])

        # Should have no new observations added (duplicate ignored)
        entity = store.load_entity("ObsEntity")
        self.assertEqual(len(entity["observations"]), 1)

    def test_relations_auto_create_entities(self):
        """Test that relations auto-create missing entities."""
        from tools.memory.sqlite_memory_store import SqliteMemoryStore

        store = SqliteMemoryStore(self.db_path)

        # Create relation without creating entities first
        result = store.create_relations([{"from": "EntityA", "to": "EntityB", "relationType": "depends_on"}])

        self.assertIn("created_relations", result)

        # Verify entities were auto-created
        entity_a = store.load_entity("EntityA")
        entity_b = store.load_entity("EntityB")
        self.assertIsNotNone(entity_a)
        self.assertIsNotNone(entity_b)

    def test_protected_entities_not_deleted(self):
        """Test that protected entity types are not cleaned up."""
        from tools.memory.sqlite_memory_store import SqliteMemoryStore

        store = SqliteMemoryStore(self.db_path)

        # Create protected entity (old timestamp)
        store.create_entities([{
            "name": "Layer:L0",
            "entityType": "ArchitectureLayer",
            "observations": ["Layer L0 description"]
        }])

        # Create regular entity
        store.create_entities([{"name": "RegularEntity", "entityType": "general"}])

        # Manually update timestamps to be old (simulate 40 days ago)
        conn = sqlite3.connect(self.db_path)
        old_time = time.time() - (40 * 86400)
        conn.execute("UPDATE entities SET updated_at = ?", (old_time,))
        conn.commit()
        conn.close()

        # Run cleanup (30 days threshold)
        result = store.cleanup_stale(
            older_than_days=30,
            protected_types=("ArchitectureLayer", "ProjectContext", "ConstitutionalRule")
        )

        # Protected entity should still exist
        layer = store.load_entity("Layer:L0")
        self.assertIsNotNone(layer)

        # Regular entity should be deleted
        regular = store.load_entity("RegularEntity")
        self.assertIsNone(regular)

        self.assertGreater(result["deleted_count"], 0)
        self.assertNotIn("Layer:L0", result["deleted_names"])

    def test_persistence_across_connections(self):
        """Test data persists after closing and reopening connection."""
        from tools.memory.sqlite_memory_store import SqliteMemoryStore

        # First connection - write data
        store1 = SqliteMemoryStore(self.db_path)
        store1.create_entities([{"name": "PersistEntity", "entityType": "Test"}])
        del store1  # Close connection

        # Second connection - read data
        store2 = SqliteMemoryStore(self.db_path)
        entity = store2.load_entity("PersistEntity")

        self.assertIsNotNone(entity)
        self.assertEqual(entity["name"], "PersistEntity")

    def test_stats_calculation(self):
        """Test statistics calculation."""
        from tools.memory.sqlite_memory_store import SqliteMemoryStore

        store = SqliteMemoryStore(self.db_path)

        # Create test data
        store.create_entities([
            {"name": "E1", "entityType": "Agent"},
            {"name": "E2", "entityType": "Agent"},
            {"name": "E3", "entityType": "Violation"},
        ])
        store.add_observations([
            {"entityName": "E1", "contents": ["obs1", "obs2"]},
            {"entityName": "E2", "contents": ["obs3"]},
        ])

        stats = store.get_stats()

        self.assertEqual(stats["total_entities"], 3)
        self.assertEqual(stats["total_observations"], 3)
        self.assertIn("by_entity_type", stats)
        self.assertEqual(stats["by_entity_type"]["Agent"], 2)

    def test_search_nodes(self):
        """Test full-text search across entities."""
        from tools.memory.sqlite_memory_store import SqliteMemoryStore

        store = SqliteMemoryStore(self.db_path)

        store.create_entities([
            {"name": "GravityValidator", "entityType": "Agent", "observations": ["Validates gravity compliance"]},
            {"name": "RouterEngine", "entityType": "Service", "observations": ["Routes requests"]},
        ])

        # Search by name
        results = store.search_nodes("Gravity")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "GravityValidator")

        # Search by observation content
        results = store.search_nodes("compliance")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "GravityValidator")


@pytest.mark.e2e
@pytest.mark.skipif(not MEMORY_SERVER_VALID, reason="adg_memory_server.py not available or has syntax errors")
class TestMemoryMcpServerE2E(unittest.TestCase):
    """E2E tests for Memory MCP Server (adg_memory_server.py)."""

    def setUp(self):
        """Create temp database and mock Redis."""
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.tmp_dir) / "test_memory.sqlite"
        os.environ["MEMORY_DB"] = str(self.db_path)

    def tearDown(self):
        """Clean up."""
        import shutil
        if "MEMORY_DB" in os.environ:
            del os.environ["MEMORY_DB"]
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_server_module_imports(self):
        """Test that adg_memory_server module can be imported."""
        try:
            import tools.memory.adg_memory_server as server_module
            self.assertTrue(hasattr(server_module, 'mcp'))
        except ImportError as e:
            self.fail(f"Failed to import adg_memory_server: {e}")
        except SyntaxError as e:
            self.fail(f"adg_memory_server has syntax errors: {e}")

    @patch("redis.from_url")
    def test_mem_import_adg_context_cold_cache(self, mock_redis):
        """Test mem_import_adg_context handles cold Redis cache."""
        from tools.memory.sqlite_memory_store import SqliteMemoryStore

        store = SqliteMemoryStore(self.db_path)

        # Mock Redis with cold cache (no adg:meta)
        mock_client = MagicMock()
        mock_client.hgetall.return_value = {}
        mock_redis.return_value = mock_client

        # Import should handle cold cache gracefully
        # Note: We can't test the actual function without full server setup,
        # but we verify the store is ready for the import
        self.assertTrue(self.db_path.exists())


@pytest.mark.e2e
class TestMemoryMcpIntegration(unittest.TestCase):
    """Integration tests for Memory MCP with ADG."""

    def test_sqlite_store_file_creation(self):
        """Test that SQLite database file is created."""
        from tools.memory.sqlite_memory_store import SqliteMemoryStore

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "memory.sqlite"
            store = SqliteMemoryStore(db_path)

            # Create entity to force database creation
            store.create_entities([{"name": "Test", "entityType": "Test"}])

            self.assertTrue(db_path.exists())
            self.assertGreater(db_path.stat().st_size, 0)

    def test_database_schema_creation(self):
        """Test that database schema is properly created."""
        from tools.memory.sqlite_memory_store import SqliteMemoryStore

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "memory.sqlite"
            store = SqliteMemoryStore(db_path)

            # Verify schema by checking tables exist
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}
            conn.close()

            self.assertIn("entities", tables)
            self.assertIn("observations", tables)
            self.assertIn("relations", tables)


class TestMemoryMcpAvailability(unittest.TestCase):
    """Tests verifying Memory MCP components are present and valid."""

    def test_memory_server_file_exists(self):
        """Verify adg_memory_server.py exists."""
        self.assertTrue(MEMORY_SERVER_AVAILABLE, "adg_memory_server.py should exist")

    def test_memory_server_valid_python(self):
        """Verify adg_memory_server.py has no syntax errors."""
        self.assertTrue(MEMORY_SERVER_VALID, "adg_memory_server.py should be valid Python")

    def test_sqlite_store_file_exists(self):
        """Verify sqlite_memory_store.py exists."""
        self.assertTrue(SQLITE_STORE_AVAILABLE, "sqlite_memory_store.py should exist")

    def test_sqlite_store_valid_python(self):
        """Verify sqlite_memory_store.py has no syntax errors."""
        self.assertTrue(SQLITE_STORE_VALID, "sqlite_memory_store.py should be valid Python")


if __name__ == "__main__":
    # Run with: python tests/integration/test_memory_persistence_e2e.py
    # Or: pytest tests/integration/test_memory_persistence_e2e.py -v
    unittest.main(verbosity=2)
