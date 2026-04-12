"""Test PowershellBanAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPowershellBanAdg:
    """Test PowershellBanAdg functionality."""

    def test_powershell_ban_adg_imports(self):
        """Test powershell_ban_adg module imports."""
        from agentic_core import powershell_ban_adg

        assert powershell_ban_adg is not None

    def test_powershell_ban_adg_class(self):
        """Test PowershellBanAdg class exists."""
        from agentic_core import PowershellBanAdg

        assert PowershellBanAdg is not None

    def test_powershell_ban_adg_callable(self):
        """Test powershell_ban_adg functions are callable."""
        from agentic_core import validate_powershell_ban_adg

        assert callable(validate_powershell_ban_adg)
