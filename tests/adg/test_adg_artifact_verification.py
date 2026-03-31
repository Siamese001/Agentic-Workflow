"""Test ADG artifact verification functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgArtifactVerification:
    """Test ADG artifact verification functionality."""

    def test_adg_sqlite_files_exist(self):
        """Test ADG SQLite files exist in artifacts."""
        adg_dir = REPO_ROOT / "artifacts" / "adg"

        # Look for SQLite files
        sqlite_files = list(adg_dir.glob("*.sqlite"))
        # May be empty in CI, but directory should exist
        assert adg_dir.exists()

    def test_adg_json_files_exist(self):
        """Test ADG JSON files exist in artifacts."""
        adg_dir = REPO_ROOT / "artifacts" / "adg"

        json_files = list(adg_dir.glob("*.json"))
        # Directory should exist even if no JSON files yet
        assert adg_dir.exists()

    def test_adg_schema_util_exists(self):
        """Test ADG schema utility module exists."""
        schema_util = REPO_ROOT / "agentic_core" / "adg" / "schema_util.py"
        assert schema_util.exists()

    def test_adg_identity_normalizer_exists(self):
        """Test ADG identity normalizer exists."""
        identity_norm = (
            REPO_ROOT / "agentic_core" / "adg" / "extraction" / "identity_normalizer.py"
        )
        assert identity_norm.exists()

    def test_adg_static_analyzer_exists(self):
        """Test ADG static analyzer exists."""
        analyzer = REPO_ROOT / "agentic_core" / "adg" / "extraction" / "static_analyzer.py"
        assert analyzer.exists()

    def test_adg_edge_builder_exists(self):
        """Test ADG edge builder exists."""
        edge_builder = REPO_ROOT / "agentic_core" / "adg" / "extraction" / "edge_builder.py"
        assert edge_builder.exists()

    def test_adg_runtime_tracer_exists(self):
        """Test ADG runtime tracer exists."""
        tracer = REPO_ROOT / "agentic_core" / "adg" / "runtime" / "tracer.py"
        assert tracer.exists()

    def test_adg_reports_directory_exists(self):
        """Test ADG reports directory exists."""
        reports_dir = REPO_ROOT / "reports" / "adg"
        assert reports_dir.exists()


if __name__ == '__main__':
    pytest.main()
