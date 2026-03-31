"""Test drift lifecycle functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDriftLifecycle:
    """Test drift lifecycle functionality."""

    def test_drift_lifecycle_imports(self):
        """Test drift lifecycle module imports."""
        from tools.adg import drift_lifecycle
        assert drift_lifecycle is not None

    def test_drift_lifecycle_script_exists(self):
        """Test drift lifecycle script exists."""
        script = REPO_ROOT / "tools" / "adg" / "drift_lifecycle.py"
        assert script.exists()

    def test_drift_lifecycle_main_function(self):
        """Test drift lifecycle main function."""
        from tools.adg.drift_lifecycle import main
        assert callable(main)
