"""Test PopulateSsotFoldersUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPopulateSsotFoldersUtilAdg:
    """Test PopulateSsotFoldersUtilAdg functionality."""

    def test_populate_ssot_folders_util_adg_imports(self):
        """Test populate_ssot_folders_util_adg module imports."""
        from agentic_core import populate_ssot_folders_util_adg

        assert populate_ssot_folders_util_adg is not None

    def test_populate_ssot_folders_util_adg_class(self):
        """Test PopulateSsotFoldersUtilAdg class exists."""
        from agentic_core import PopulateSsotFoldersUtilAdg

        assert PopulateSsotFoldersUtilAdg is not None

    def test_populate_ssot_folders_util_adg_callable(self):
        """Test populate_ssot_folders_util_adg functions are callable."""
        from agentic_core import validate_populate_ssot_folders_util_adg

        assert callable(validate_populate_ssot_folders_util_adg)
