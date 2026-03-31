"""Test zip creation functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestZipCreation:
    """Test zip creation functionality."""

    def test_zip_creation_imports(self):
        """Test zip creation module imports."""
        from tools.adg import adg_lifecycle
        assert adg_lifecycle is not None

    def test_create_zip_function(self):
        """Test create zip function."""
        from tools.adg.adg_lifecycle import create_zip_archive
        assert callable(create_zip_archive)

    def test_zip_artifacts_function(self):
        """Test zip artifacts function."""
        from tools.adg.adg_lifecycle import zip_artifacts
        assert callable(zip_artifacts)
