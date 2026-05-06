"""Test sentinel rejection in path_resolver.latest_sqlite() — S-09 verification.

Regression test for SSOT issue S-09: ensures that sentinel files like
``adg_indexed_99999999_9999.sqlite`` (month 99 is invalid) are rejected
by the canonical resolver's timestamp format validation.

The canonical resolver validates timestamps using ``%m%d%Y_%H%M`` format.
Sentinel files with invalid month values (e.g., 99999999) will be rejected.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_adg_dir():
    """Provide a temporary ADG directory for isolated testing."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


def test_sentinel_file_rejected_by_timestamp_validation(temp_adg_dir: Path) -> None:
    """Sentinel with invalid month (99) is rejected by _is_valid_snapshot_file."""
    # Import the function under test
    from tools.adg.shared_modules.path_resolver import latest_sqlite

    # Create a valid snapshot file
    valid_file = temp_adg_dir / "adg_indexed_04282026_2152.sqlite"
    valid_file.write_bytes(b"valid snapshot content")

    # Create a sentinel file with invalid timestamp (month 99)
    sentinel_file = temp_adg_dir / "adg_indexed_99999999_9999.sqlite"
    sentinel_file.write_bytes(b"sentinel content")

    # Set ADG_DIR to temp directory
    original_adg_dir = os.environ.get("ADG_DIR")
    os.environ["ADG_DIR"] = str(temp_adg_dir)

    try:
        # The sentinel should be rejected because 99999999 doesn't match %m%d%Y_%H%M
        result = latest_sqlite()
        assert result is not None
        # Should return the valid file, not the sentinel
        assert result.name == "adg_indexed_04282026_2152.sqlite"
    finally:
        # Restore environment
        if original_adg_dir is None:
            os.environ.pop("ADG_DIR", None)
        else:
            os.environ["ADG_DIR"] = original_adg_dir


def test_sentinel_only_directory_returns_none(temp_adg_dir: Path) -> None:
    """Directory with only sentinel files returns None (no valid snapshots)."""
    from tools.adg.shared_modules.path_resolver import latest_sqlite

    # Create only sentinel files (invalid timestamps)
    sentinel1 = temp_adg_dir / "adg_indexed_99999999_9999.sqlite"
    sentinel1.write_bytes(b"sentinel 1")
    sentinel2 = temp_adg_dir / "adg_indexed_00000000_0000.sqlite"
    sentinel2.write_bytes(b"sentinel 2")

    original_adg_dir = os.environ.get("ADG_DIR")
    os.environ["ADG_DIR"] = str(temp_adg_dir)

    try:
        result = latest_sqlite()
        # Should return None because no valid timestamp files exist
        assert result is None
    finally:
        if original_adg_dir is None:
            os.environ.pop("ADG_DIR", None)
        else:
            os.environ["ADG_DIR"] = original_adg_dir


def test_multiple_valid_files_returns_latest_by_mtime(temp_adg_dir: Path) -> None:
    """With multiple valid files, the newest by mtime is returned."""
    from tools.adg.shared_modules.path_resolver import latest_sqlite

    # Create multiple valid snapshot files
    file1 = temp_adg_dir / "adg_indexed_04272026_1200.sqlite"
    file1.write_bytes(b"older")
    file2 = temp_adg_dir / "adg_indexed_04282026_2152.sqlite"
    file2.write_bytes(b"newer")

    # Ensure different mtimes (file2 should be newer)
    import time

    os.utime(file1, (time.time() - 100, time.time() - 100))
    os.utime(file2, (time.time(), time.time()))

    original_adg_dir = os.environ.get("ADG_DIR")
    os.environ["ADG_DIR"] = str(temp_adg_dir)

    try:
        result = latest_sqlite()
        assert result is not None
        # Should return the newer file
        assert result.name == "adg_indexed_04282026_2152.sqlite"
    finally:
        if original_adg_dir is None:
            os.environ.pop("ADG_DIR", None)
        else:
            os.environ["ADG_DIR"] = original_adg_dir


def test_require_nodes_table_skips_files_without_nodes(temp_adg_dir: Path) -> None:
    """With require_nodes_table=True, files without 'nodes' table are skipped."""
    import sqlite3
    import time

    from tools.adg.shared_modules.path_resolver import latest_sqlite

    # Create a valid-looking file with proper timestamp but no nodes table
    empty_file = temp_adg_dir / "adg_indexed_04282026_2152.sqlite"
    # Create empty SQLite file without nodes table - ensure explicit close
    conn1 = sqlite3.connect(str(empty_file))
    conn1.execute("CREATE TABLE other_table (id INTEGER)")
    conn1.commit()
    conn1.close()

    # Create another file with a nodes table - ensure explicit close
    valid_file = temp_adg_dir / "adg_indexed_04292026_0800.sqlite"
    conn2 = sqlite3.connect(str(valid_file))
    conn2.execute("CREATE TABLE nodes (id INTEGER)")
    conn2.commit()
    conn2.close()

    # Force garbage collection to release any lingering handles
    import gc

    gc.collect()

    # Ensure valid_file is newer
    time.sleep(0.01)  # Small delay to ensure different mtimes
    os.utime(empty_file, (time.time() - 100, time.time() - 100))
    os.utime(valid_file, (time.time(), time.time()))

    original_adg_dir = os.environ.get("ADG_DIR")
    os.environ["ADG_DIR"] = str(temp_adg_dir)

    try:
        # Without require_nodes_table, should return the newest by mtime
        result = latest_sqlite(require_nodes_table=False)
        assert result is not None
        assert result.name == "adg_indexed_04292026_0800.sqlite"

        # With require_nodes_table, should skip the empty file and return the one with nodes
        result = latest_sqlite(require_nodes_table=True)
        assert result is not None
        assert result.name == "adg_indexed_04292026_0800.sqlite"
    finally:
        if original_adg_dir is None:
            os.environ.pop("ADG_DIR", None)
        else:
            os.environ["ADG_DIR"] = original_adg_dir
        # Ensure connections are closed before cleanup
        gc.collect()


def test_empty_directory_returns_none(temp_adg_dir: Path) -> None:
    """Empty ADG directory returns None."""
    from tools.adg.shared_modules.path_resolver import latest_sqlite

    original_adg_dir = os.environ.get("ADG_DIR")
    os.environ["ADG_DIR"] = str(temp_adg_dir)

    try:
        result = latest_sqlite()
        assert result is None
    finally:
        if original_adg_dir is None:
            os.environ.pop("ADG_DIR", None)
        else:
            os.environ["ADG_DIR"] = original_adg_dir
