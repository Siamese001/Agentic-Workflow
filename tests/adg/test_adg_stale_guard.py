"""Test ADG stale guard functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgStaleGuard:
    """Test ADG stale guard functionality."""

    def test_stale_guard_imports(self):
        """Test stale guard module imports."""
        from tools.adg import adg_stale_guard
        assert adg_stale_guard is not None

    def test_stale_guard_script_exists(self):
        """Test stale guard script exists."""
        script = REPO_ROOT / "tools" / "adg" / "adg_stale_guard.py"
        assert script.exists()

    def test_stale_guard_cli_function(self):
        """Test stale guard CLI function."""
        from tools.adg.adg_stale_guard import main
        assert callable(main)
