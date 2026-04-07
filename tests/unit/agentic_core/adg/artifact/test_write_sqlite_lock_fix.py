"""Tests for _write_sqlite lock fix (connection close before rename)."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


class TestWriteSqliteLockFix:
    """Verify connection is closed before temp file rename to avoid Windows lock error."""

    def test_write_failed_cleans_temp_file(self, tmp_path):
        """Temp file must be cleaned up on write failure (write_failed flag)."""
        from agentic_core.adg.artifact.ArtifactPaths import _write_sqlite

        db_path = tmp_path / "test.sqlite"

        # Create minimal NormalizedGraph structure
        from agentic_core.adg.artifact.normalizer import NormalizedGraph
        ng_full = NormalizedGraph(
            schema_version="4.0.0",
            commit_sha="abc123",
            scanner_digest="def456",
            nodes={},
            edges=[],
            meta={},
        )

        # Force failure during write by corrupting executescript
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = mock_connect.return_value
            mock_conn.execute.side_effect = RuntimeError("Write failure")

            with pytest.raises(RuntimeError):
                _write_sqlite(ng_full, db_path)

            # Temp file should be cleaned up
            temp_path = tmp_path / "test.sqlite.tmp"
            assert not temp_path.exists()

    def test_temp_file_unlink_on_startup(self, tmp_path):
        """Existing temp file must be unlinked before new write."""
        from agentic_core.adg.artifact.ArtifactPaths import _write_sqlite

        db_path = tmp_path / "test.sqlite"
        temp_path = tmp_path / "test.sqlite.tmp"

        # Create minimal NormalizedGraph structure
        from agentic_core.adg.artifact.normalizer import NormalizedGraph
        ng_full = NormalizedGraph(
            schema_version="4.0.0",
            commit_sha="abc123",
            scanner_digest="def456",
            nodes={},
            edges=[],
            meta={},
        )

        # Create existing temp file
        temp_path.write_text("old temp")

        _write_sqlite(ng_full, db_path)

        # Temp file should be replaced (unlinked then recreated)
        assert db_path.exists()
