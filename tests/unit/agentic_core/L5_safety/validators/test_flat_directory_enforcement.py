"""Test FlatDirectoryEnforcement functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFlatDirectoryEnforcement:
    """Test FlatDirectoryEnforcement functionality."""

    def test_flat_directory_enforcement_imports(self):
        """Test flat_directory_enforcement module imports."""
        from agentic_core import flat_directory_enforcement

        assert flat_directory_enforcement is not None

    def test_flat_directory_enforcement_class(self):
        """Test FlatDirectoryEnforcement class exists."""
        from agentic_core import FlatDirectoryEnforcement

        assert FlatDirectoryEnforcement is not None

    def test_flat_directory_enforcement_callable(self):
        """Test flat_directory_enforcement functions are callable."""
        from agentic_core import validate_flat_directory_enforcement

        assert callable(validate_flat_directory_enforcement)
