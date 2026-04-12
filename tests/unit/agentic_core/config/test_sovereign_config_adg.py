"""Test SovereignConfigAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSovereignConfigAdg:
    """Test SovereignConfigAdg functionality."""

    def test_sovereign_config_adg_imports(self):
        """Test sovereign_config_adg module imports."""
        from agentic_core import sovereign_config_adg

        assert sovereign_config_adg is not None

    def test_sovereign_config_adg_class(self):
        """Test SovereignConfigAdg class exists."""
        from agentic_core import SovereignConfigAdg

        assert SovereignConfigAdg is not None

    def test_sovereign_config_adg_callable(self):
        """Test sovereign_config_adg functions are callable."""
        from agentic_core import validate_sovereign_config_adg

        assert callable(validate_sovereign_config_adg)
