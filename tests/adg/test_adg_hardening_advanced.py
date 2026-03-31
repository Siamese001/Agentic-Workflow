"""Test ADG hardening advanced functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgHardeningAdvanced:
    """Test ADG hardening advanced functionality."""

    def test_hardening_advanced_imports(self):
        """Test hardening advanced module imports."""
        from tools.adg import adg_harden
        assert adg_harden is not None

    def test_hardening_p0_wirer_exists(self):
        """Test P0 wirer hardening exists."""
        from tools.p0_batch_wirer import main
        assert callable(main)

    def test_hardening_p1_wire_exists(self):
        """Test P1 wire hardening exists."""
        from tools.p1_batch_wire import main
        assert callable(main)

    def test_hardening_dimension_config_valid(self):
        """Test hardening dimension config is valid."""
        from tools.p0_batch_wirer import DIMENSION_CONFIG
        assert isinstance(DIMENSION_CONFIG, dict)
        assert len(DIMENSION_CONFIG) >= 4
