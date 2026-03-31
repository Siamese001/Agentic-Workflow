"""Test ADG infusion phases verification functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgInfusionPhasesVerification:
    """Test ADG infusion phases verification functionality."""

    def test_infusion_phases_imports(self):
        """Test infusion phases module imports."""
        from tools.adg import adg_lifecycle
        assert adg_lifecycle is not None

    def test_infusion_phases_infrastructure_exists(self):
        """Test infusion phases infrastructure exists."""
        phases_dir = REPO_ROOT / "tools" / "adg"
        assert phases_dir.exists()

    def test_adg_lifecycle_script_exists(self):
        """Test ADG lifecycle script exists."""
        script = REPO_ROOT / "tools" / "adg" / "adg_lifecycle.py"
        assert script.exists()
