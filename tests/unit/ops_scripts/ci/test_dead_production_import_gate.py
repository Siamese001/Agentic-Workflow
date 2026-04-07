"""Unit tests for dead_production_import_gate.py"""

import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ops_scripts.ci.dead_production_import_gate import run_gate


@pytest.fixture
def temp_sqlite(tmp_path: Path) -> Path:
    """Create a temporary SQLite database with test ADG data."""
    sqlite_path = tmp_path / "test_adg.sqlite"
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()

    # Create tables
    cur.execute("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            resolved_path TEXT NOT NULL,
            layer TEXT NOT NULL,
            entity_type TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            FOREIGN KEY (src_id) REFERENCES nodes(id),
            FOREIGN KEY (dst_id) REFERENCES nodes(id)
        )
    """)

    # Insert test nodes
    cur.execute(
        "INSERT INTO nodes (id, resolved_path, layer, entity_type) VALUES "
        "(1, 'agentic_core/L4_state/cache/gptcache_client.py', 'L4', 'module'),"
        "(2, 'agentic_core/L4_state/utils/memory/semantic_cache_manager.py', 'L4', 'module'),"
        "(3, 'agentic_core/L4_state/cache/__init__.py', 'L4', 'module'),"
        "(4, 'tests/test_cache.py', 'L_TEST', 'module'),"
        "(5, 'ops_scripts/ci/test_gate.py', 'L_OPS', 'module')"
    )

    # Insert test edges (semantic_cache_manager imports gptcache_client)
    cur.execute(
        "INSERT INTO edges (src_id, dst_id, relation_type) VALUES "
        "(2, 1, 'imports')"
    )

    conn.commit()
    conn.close()
    return sqlite_path


def test_gate_passes_with_fan_in(temp_sqlite: Path) -> None:
    """Test that gate passes when modules have production fan-in."""
    with patch.object(sys, 'exit') as mock_exit:
        run_gate(temp_sqlite)
        # Should exit with code 0 (success)
        mock_exit.assert_called_once_with(0)


def test_gate_fails_with_zero_fan_in(tmp_path: Path) -> None:
    """Test that gate fails when modules have zero production fan-in."""
    sqlite_path = tmp_path / "test_adg_no_fanin.sqlite"
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()

    # Create tables
    cur.execute("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            resolved_path TEXT NOT NULL,
            layer TEXT NOT NULL,
            entity_type TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            FOREIGN KEY (src_id) REFERENCES nodes(id),
            FOREIGN KEY (dst_id) REFERENCES nodes(id)
        )
    """)

    # Insert test nodes (gptcache_client with no fan-in)
    cur.execute(
        "INSERT INTO nodes (id, resolved_path, layer, entity_type) VALUES "
        "(1, 'agentic_core/L4_state/cache/gptcache_client.py', 'L4', 'module'),"
        "(2, 'tests/test_cache.py', 'L_TEST', 'module')"
    )

    # No edges from production to gptcache_client
    conn.commit()
    conn.close()

    with patch.object(sys, 'exit') as mock_exit:
        run_gate(sqlite_path)
        # Should exit with code 1 (failure)
        mock_exit.assert_called_once_with(1)


def test_gate_handles_missing_file(tmp_path: Path) -> None:
    """Test that gate fails gracefully when SQLite file doesn't exist."""
    missing_path = tmp_path / "nonexistent.sqlite"
    
    with patch.object(sys, 'exit') as mock_exit:
        run_gate(missing_path)
        # Should exit with code 2 (error)
        mock_exit.assert_called_once_with(2)


def test_gate_filters_by_allowlist(tmp_path: Path) -> None:
    """Test that gate respects allowlist patterns."""
    sqlite_path = tmp_path / "test_adg_allowlist.sqlite"
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()

    # Create tables
    cur.execute("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            resolved_path TEXT NOT NULL,
            layer TEXT NOT NULL,
            entity_type TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            FOREIGN KEY (src_id) REFERENCES nodes(id),
            FOREIGN KEY (dst_id) REFERENCES nodes(id)
        )
    """)

    # Insert test nodes (including apps_shared which is allowlisted)
    cur.execute(
        "INSERT INTO nodes (id, resolved_path, layer, entity_type) VALUES "
        "(1, 'agentic_core/L4_state/cache/gptcache_client.py', 'L4', 'module'),"
        "(2, 'apps_shared/utils/test_util.py', 'L_APP', 'module')"
    )

    conn.commit()
    conn.close()

    # Should fail because gptcache_client has no fan-in
    with patch('ops_scripts.ci.dead_production_import_gate.DEFAULT_ALLOWLIST', ['apps_*']):
        with patch.object(sys, 'exit') as mock_exit:
            run_gate(sqlite_path)
            # Should exit with code 1 (failure) - gptcache_client still caught
            mock_exit.assert_called_once_with(1)


def test_gate_ignores_test_ops_fan_in(tmp_path: Path) -> None:
    """Test that gate ignores fan-in from test/ops layers."""
    sqlite_path = tmp_path / "test_adg_test_fanin.sqlite"
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()

    # Create tables
    cur.execute("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            resolved_path TEXT NOT NULL,
            layer TEXT NOT NULL,
            entity_type TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            FOREIGN KEY (src_id) REFERENCES nodes(id),
            FOREIGN KEY (dst_id) REFERENCES nodes(id)
        )
    """)

    # Insert test nodes
    cur.execute(
        "INSERT INTO nodes (id, resolved_path, layer, entity_type) VALUES "
        "(1, 'agentic_core/L4_state/cache/gptcache_client.py', 'L4', 'module'),"
        "(2, 'tests/test_cache.py', 'L_TEST', 'module'),"
        "(3, 'ops_scripts/ci/test_gate.py', 'L_OPS', 'module')"
    )

    # Test imports gptcache_client (should be ignored)
    cur.execute("INSERT INTO edges (src_id, dst_id, relation_type) VALUES (2, 1, 'imports')")
    # Ops imports gptcache_client (should be ignored)
    cur.execute("INSERT INTO edges (src_id, dst_id, relation_type) VALUES (3, 1, 'imports')")

    conn.commit()
    conn.close()

    with patch.object(sys, 'exit') as mock_exit:
        run_gate(sqlite_path)
        # Should exit with code 1 (failure) - test/ops fan-in ignored
        mock_exit.assert_called_once_with(1)


def test_gate_targets_l4_state_cache_only(tmp_path: Path) -> None:
    """Test that gate only checks agentic_core/L4_state/cache/*."""
    sqlite_path = tmp_path / "test_adg_targeted.sqlite"
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()

    # Create tables
    cur.execute("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            resolved_path TEXT NOT NULL,
            layer TEXT NOT NULL,
            entity_type TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            FOREIGN KEY (src_id) REFERENCES nodes(id),
            FOREIGN KEY (dst_id) REFERENCES nodes(id)
        )
    """)

    # Insert test nodes (dead module outside L4_state/cache)
    cur.execute(
        "INSERT INTO nodes (id, resolved_path, layer, entity_type) VALUES "
        "(1, 'agentic_core/L4_state/utils/other_util.py', 'L4', 'module'),"
        "(2, 'agentic_core/L4_state/cache/gptcache_client.py', 'L4', 'module')"
    )

    conn.commit()
    conn.close()

    with patch.object(sys, 'exit') as mock_exit:
        run_gate(sqlite_path)
        # Should exit with code 0 (success) - only gptcache_client checked
        mock_exit.assert_called_once_with(1)  # gptcache_client still caught
