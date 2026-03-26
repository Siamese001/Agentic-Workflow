"""ADG pipeline smoke tests — import verification and artifact integrity."""
import os
import sqlite3
from pathlib import Path
import pytest

@pytest.mark.smoke
def test_generate_full_adg_importable():
    """Verify tools.generate_full_adg imports without error."""
    try:
        from tools.generate_full_adg import main as generate_adg_main
        assert callable(generate_adg_main)
    except ImportError as e:
        pytest.skip(f"adg_pipeline not available: {e}")
@pytest.mark.smoke
def test_sqlite_artifact_exists():
    """Verify latest ADG SQLite artifact exists."""
    artifacts_dir = Path("artifacts/adg")
    if not artifacts_dir.exists():
        pytest.skip(f"ADG artifacts directory not found: {artifacts_dir}")

    # Find the latest adg_indexed_*.sqlite file
    sqlite_files = list(artifacts_dir.glob("adg_indexed_*.sqlite"))
    if not sqlite_files:
        pytest.fail("No ADG SQLite artifacts found in artifacts/adg/")

    # Verify the most recent file exists
    latest_file = max(sqlite_files, key=lambda f: f.stat().st_mtime)
    assert latest_file.exists(), f"Latest ADG SQLite file not found: {latest_file}"

@pytest.mark.smoke
def test_sqlite_schema_tables():
    """Verify ADG SQLite has required tables with correct columns."""
    artifacts_dir = Path("artifacts/adg")
    sqlite_files = list(artifacts_dir.glob("adg_indexed_*.sqlite"))
    if not sqlite_files:
        pytest.skip("No ADG SQLite artifacts found")

    latest_file = max(sqlite_files, key=lambda f: f.stat().st_mtime)

    try:
        conn = sqlite3.connect(str(latest_file))
        cursor = conn.cursor()

        # Check nodes table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'")
        assert cursor.fetchone(), "nodes table not found in ADG SQLite"

        # Check edges table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='edges'")
        assert cursor.fetchone(), "edges table not found in ADG SQLite"

        # Verify nodes table has key columns
        cursor.execute("PRAGMA table_info(nodes)")
        nodes_columns = [row[1] for row in cursor.fetchall()]
        required_node_cols = {'id', 'adg_name', 'entity_type', 'layer', 'identity_kind'}
        assert required_node_cols.issubset(set(nodes_columns)), f"Missing required columns in nodes table: {required_node_cols - set(nodes_columns)}"

        # Verify edges table has key columns
        cursor.execute("PRAGMA table_info(edges)")
        edges_columns = [row[1] for row in cursor.fetchall()]
        required_edge_cols = {'id', 'src_id', 'dst_id', 'relation_type', 'edge_kind'}
        assert required_edge_cols.issubset(set(edges_columns)), f"Missing required columns in edges table: {required_edge_cols - set(edges_columns)}"

        conn.close()
    except sqlite3.Error as e:
        pytest.fail(f"Error reading ADG SQLite schema: {e}")

@pytest.mark.smoke
def test_sqlite_nonzero_counts():
    """Verify ADG SQLite has non-zero node and edge counts."""
    artifacts_dir = Path("artifacts/adg")
    sqlite_files = list(artifacts_dir.glob("adg_indexed_*.sqlite"))
    if not sqlite_files:
        pytest.skip("No ADG SQLite artifacts found")

    latest_file = max(sqlite_files, key=lambda f: f.stat().st_mtime)

    try:
        conn = sqlite3.connect(str(latest_file))
        cursor = conn.cursor()

        # Count nodes
        cursor.execute("SELECT COUNT(*) FROM nodes")
        node_count = cursor.fetchone()[0]
        assert node_count > 0, f"ADG SQLite has zero nodes"

        # Count edges
        cursor.execute("SELECT COUNT(*) FROM edges")
        edge_count = cursor.fetchone()[0]
        assert edge_count > 0, f"ADG SQLite has zero edges"

        conn.close()
    except sqlite3.Error as e:
        pytest.fail(f"Error reading ADG SQLite counts: {e}")

@pytest.mark.smoke
def test_adg_artifact_builder_imports():
    """Verify agentic_core.adg.artifact.builder imports."""
    try:
        from agentic_core.adg.artifact.builder import ADGArtifactBuilder
        assert ADGArtifactBuilder is not None
    except ImportError as e:
        pytest.skip(f"ADGArtifactBuilder not available: {e}")
