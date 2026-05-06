"""Tests for Memory MCP schema versioning.

Location: tests/unit/tools/memory/test_schema_versioning.py
"""
import tempfile
from pathlib import Path

import pytest

from tools.memory.sqlite_memory_store import SqliteMemoryStore, _SCHEMA_FILE, _load_schema


class TestSchemaLoading:
    """Test schema loading from canonical location."""

    def test_schema_file_exists(self):
        """Canonical schema file should exist in .windsurf/schemas/."""
        assert _SCHEMA_FILE.exists(), f"Schema file not found: {_SCHEMA_FILE}"

    def test_schema_file_contains_entities_table(self):
        """Schema file should define entities table."""
        schema = _SCHEMA_FILE.read_text(encoding="utf-8")
        assert "CREATE TABLE IF NOT EXISTS entities" in schema

    def test_schema_file_contains_observations_table(self):
        """Schema file should define observations table."""
        schema = _SCHEMA_FILE.read_text(encoding="utf-8")
        assert "CREATE TABLE IF NOT EXISTS observations" in schema

    def test_schema_file_contains_relations_table(self):
        """Schema file should define relations table."""
        schema = _SCHEMA_FILE.read_text(encoding="utf-8")
        assert "CREATE TABLE IF NOT EXISTS relations" in schema

    def test_schema_file_contains_version_table(self):
        """Schema file should define _schema_version table."""
        schema = _SCHEMA_FILE.read_text(encoding="utf-8")
        assert "CREATE TABLE IF NOT EXISTS _schema_version" in schema

    def test_load_schema_returns_string(self):
        """_load_schema should return a string."""
        schema = _load_schema()
        assert isinstance(schema, str)
        assert len(schema) > 0

    def test_load_schema_contains_core_tables(self):
        """Loaded schema should contain core tables."""
        schema = _load_schema()
        assert "CREATE TABLE IF NOT EXISTS entities" in schema
        assert "CREATE TABLE IF NOT EXISTS observations" in schema
        assert "CREATE TABLE IF NOT EXISTS relations" in schema


class TestSchemaVersioning:
    """Test schema version tracking in database."""

    def test_new_database_has_schema_version(self):
        """New database should record schema version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            store = SqliteMemoryStore(db_path)
            
            version_info = store.get_schema_version()
            
            assert version_info["version"] == "1.0.0"
            assert version_info["applied_at"] is not None
            assert "Initial schema" in version_info["description"]

    def test_schema_version_idempotent(self):
        """Schema version recording should be idempotent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            store = SqliteMemoryStore(db_path)
            
            # First check
            v1 = store.get_schema_version()
            
            # Re-open same database
            store2 = SqliteMemoryStore(db_path)
            v2 = store2.get_schema_version()
            
            assert v1["version"] == v2["version"]
            assert v1["applied_at"] == v2["applied_at"]

    def test_schema_version_returns_all_versions(self):
        """get_schema_version should return all applied versions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            store = SqliteMemoryStore(db_path)
            
            version_info = store.get_schema_version()
            
            assert "all_versions" in version_info
            assert len(version_info["all_versions"]) >= 1

    def test_pre_versioning_schema_detected(self):
        """Database without _schema_version table should be detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            # Create a pre-versioning schema manually
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE entities (name TEXT PRIMARY KEY)")
            conn.close()
            
            store = SqliteMemoryStore(db_path)
            version_info = store.get_schema_version()
            
            # After _ensure_schema runs, version should be recorded
            assert version_info["version"] == "1.0.0"


class TestSchemaSync:
    """Test that Python code and schema file are in sync."""

    def test_embedded_schema_matches_file(self):
        """Embedded fallback schema should match canonical file (core tables only)."""
        from ops_scripts.ci.check_memory_schema_sync import _extract_embedded_schema, _normalize_sql
        
        repo_root = Path(__file__).resolve().parents[4]
        python_file = repo_root / "tools" / "memory" / "sqlite_memory_store.py"
        schema_file = repo_root / ".windsurf" / "schemas" / "knowledge_graph.schema.sql"
        
        embedded = _extract_embedded_schema(python_file)
        canonical = schema_file.read_text(encoding="utf-8")
        
        embedded_norm = _normalize_sql(embedded)
        # Remove _schema_version from canonical for comparison
        canonical_core = _normalize_sql(canonical).split("create table if not exists _schema_version")[0].strip()
        
        assert embedded_norm == canonical_core, "Embedded schema should match canonical (minus version table)"
