"""Test ADG analysis modules functionality."""

import ast
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgAnalysisModules:
    """Test ADG analysis modules functionality."""

    def test_adg_tools_directory_structure(self):
        """Test ADG tools directory has expected structure."""
        adg_dir = REPO_ROOT / "tools" / "adg"
        assert adg_dir.exists()

        # Check for key modules
        key_files = [
            "adg_mcp_server.py",
            "adg_redis_ingest.py",
            "adg_query_bridge.py",
            "adg_stale_guard.py",
        ]
        for f in key_files:
            assert (adg_dir / f).exists(), f"Missing {f}"

    def test_adg_static_scanner_exists(self):
        """Test ADG static scanner module exists."""
        scanner = REPO_ROOT / "agentic_core" / "adg" / "extraction" / "static_scanner.py"
        assert scanner.exists()

    def test_adg_schema_exists(self):
        """Test ADG schema module exists."""
        schema = REPO_ROOT / "agentic_core" / "adg" / "schema.py"
        assert schema.exists()

    def test_adg_artifact_builder_exists(self):
        """Test ADG artifact builder exists."""
        builder = REPO_ROOT / "agentic_core" / "adg" / "artifact" / "builder.py"
        assert builder.exists()

    def test_adg_artifacts_directory_exists(self):
        """Test ADG artifacts directory exists."""
        artifacts_dir = REPO_ROOT / "artifacts" / "adg"
        assert artifacts_dir.exists()

    def test_adg_redis_query_module(self):
        """Test ADG Redis query module is importable."""
        from tools.adg.adg_redis_query import ADGRedisQuery

        assert ADGRedisQuery is not None

    def test_adg_stale_guard_module(self):
        """Test ADG stale guard module is importable."""
        from tools.adg.adg_stale_guard import main

        assert callable(main)
