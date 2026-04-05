"""Pytest fixtures for tests/adg."""

import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure repo root is on sys.path so tools.adg is importable in all workers
_REPO_ROOT = str(Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)


@pytest.fixture
def adg_fixture_db():
    """Create a synthetic ADG SQLite database for testing.

    Returns the path to a temporary database with the standard ADG schema:
    - nodes table
    - edges table
    - meta table
    - violations table
    """
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = Path(f.name)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create nodes table
    cur.execute("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adg_name TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            layer TEXT NOT NULL,
            identity_kind TEXT NOT NULL,
            confidence TEXT NOT NULL,
            resolved_path TEXT NOT NULL
        )
    """)

    # Create edges table
    cur.execute("""
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            edge_kind TEXT NOT NULL,
            source_file TEXT NOT NULL,
            line_no INTEGER NOT NULL,
            symbol TEXT NOT NULL DEFAULT ''
        )
    """)

    # Create meta table
    cur.execute("""
        CREATE TABLE meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # Create violations table
    cur.execute("""
        CREATE TABLE violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edge_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            evidence TEXT NOT NULL DEFAULT '',
            file_path TEXT NOT NULL DEFAULT '',
            line_no INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Insert some sample data
    cur.execute("INSERT INTO meta VALUES ('schema_version', '1.0')")
    cur.execute("INSERT INTO meta VALUES ('total_nodes', '0')")
    cur.execute("INSERT INTO meta VALUES ('total_edges', '0')")

    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def adg_fixture_with_edges():
    """Create a synthetic ADG SQLite database with sample edges."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = Path(f.name)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create tables
    cur.execute("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adg_name TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            layer TEXT NOT NULL,
            identity_kind TEXT NOT NULL,
            confidence TEXT NOT NULL,
            resolved_path TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            edge_kind TEXT NOT NULL,
            source_file TEXT NOT NULL,
            line_no INTEGER NOT NULL,
            symbol TEXT NOT NULL DEFAULT ''
        )
    """)

    cur.execute("""
        CREATE TABLE meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # Insert sample nodes
    sample_nodes = [
        (1, "test_module.py::test_func", "function", "L3", "identity", "HIGH", "test_module.py"),
        (2, "test_module2.py::test_func2", "function", "L3", "identity", "HIGH", "test_module2.py"),
    ]
    cur.executemany(
        "INSERT INTO nodes (id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path) VALUES (?, ?, ?, ?, ?, ?, ?)",
        sample_nodes,
    )

    # Insert sample edges with various relation types
    sample_edges = [
        (1, 1, 2, "records_execution_trace", "structural", "test_module.py", 10, "test_func"),
        (2, 1, 2, "emits_replay_key", "structural", "test_module.py", 15, "test_func"),
        (3, 1, 2, "applies_guardrail", "structural", "test_module.py", 20, "test_func"),
        (4, 2, 1, "validated_by_safety_plane", "structural", "test_module2.py", 5, "test_func2"),
    ]
    cur.executemany(
        "INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        sample_edges,
    )

    cur.execute("INSERT INTO meta VALUES ('schema_version', '1.0')")
    cur.execute("INSERT INTO meta VALUES ('total_nodes', '2')")
    cur.execute("INSERT INTO meta VALUES ('total_edges', '4')")

    conn.commit()
    conn.close()

    return db_path
