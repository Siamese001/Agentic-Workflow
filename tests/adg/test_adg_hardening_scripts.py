"""Test ADG hardening scripts functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgHardeningScripts:
    """Test ADG hardening scripts functionality."""

    def test_p0_batch_wirer_script_exists(self):
        """Test P0 batch wirer script exists."""
        script = REPO_ROOT / "tools" / "p0_batch_wirer.py"
        assert script.exists()

    def test_p1_batch_wire_script_exists(self):
        """Test P1 batch wire script exists."""
        script = REPO_ROOT / "tools" / "p1_batch_wire.py"
        assert script.exists()

    def test_adg_harden_script_exists(self):
        """Test ADG harden script exists."""
        script = REPO_ROOT / "tools" / "adg" / "adg_harden.py"
        assert script.exists()

    def test_accelerator_hardening_dir_exists(self):
        """Test accelerator hardening directory exists."""
        hardening_dir = REPO_ROOT / "tools" / "adg" / "accelerators" / "hardening"
        assert hardening_dir.exists()
