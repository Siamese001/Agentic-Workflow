"""Test ADG type check functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgTypeCheck:
    """Test ADG type check functionality."""

    def test_type_check_imports(self):
        """Test type check module imports."""
        from tools.adg import adg_type_check
        assert adg_type_check is not None

    def test_type_check_script_exists(self):
        """Test type check script exists."""
        script = REPO_ROOT / "tools" / "adg" / "adg_type_check.py"
        assert script.exists()

    def test_type_check_function(self):
        """Test type check function."""
        from tools.adg.adg_type_check import check_types
        assert callable(check_types)
