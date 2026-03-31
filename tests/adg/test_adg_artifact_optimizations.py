"""Test ADG artifact optimizations functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgArtifactOptimizations:
    """Test ADG artifact optimizations functionality."""

    def test_adg_artifact_builder_types_exists(self):
        """Test ADG artifact builder types module exists."""
        builder_types = (
            REPO_ROOT / "agentic_core" / "adg" / "artifact" / "builder_types.py"
        )
        assert builder_types.exists()

    def test_adg_artifact_normalizer_exists(self):
        """Test ADG artifact normalizer exists."""
        normalizer = (
            REPO_ROOT / "agentic_core" / "adg" / "artifact" / "normalizer.py"
        )
        assert normalizer.exists()

    def test_adg_artifact_paths_exists(self):
        """Test ADG artifact paths module exists."""
        paths = REPO_ROOT / "agentic_core" / "adg" / "artifact" / "paths.py"
        assert paths.exists()

    def test_adg_artifact_writer_exists(self):
        """Test ADG artifact writer module exists."""
        writer = REPO_ROOT / "agentic_core" / "adg" / "artifact" / "writer.py"
        assert writer.exists()

    def test_adg_multi_writer_exists(self):
        """Test ADG multi-writer module exists."""
        multi_writer = (
            REPO_ROOT / "agentic_core" / "adg" / "artifact" / "multi_writer.py"
        )
        assert multi_writer.exists()

    def test_generate_full_adg_script_exists(self):
        """Test generate_full_adg.py script exists."""
        script = REPO_ROOT / "tools" / "generate_full_adg.py"
        assert script.exists()

    def test_adg_incremental_update_script_exists(self):
        """Test incremental update script exists."""
        script = REPO_ROOT / "tools" / "adg_incremental_update.py"
        assert script.exists()

    def test_adg_artifact_directory_structure(self):
        """Test ADG artifact directory has expected structure."""
        artifact_dir = REPO_ROOT / "agentic_core" / "adg" / "artifact"

        required_files = [
            "__init__.py",
            "builder.py",
            "builder_types.py",
            "normalizer.py",
            "paths.py",
        ]
        for f in required_files:
            assert (artifact_dir / f).exists(), f"Missing {f}"


if __name__ == '__main__':
    pytest.main()
