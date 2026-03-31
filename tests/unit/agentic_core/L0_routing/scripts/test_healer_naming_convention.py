"""Test HealerNamingConvention functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHealerNamingConvention:
    """Test HealerNamingConvention functionality."""

    def test_healer_naming_convention_imports(self):
        """Test healer_naming_convention module imports."""
        from agentic_core import healer_naming_convention
        assert healer_naming_convention is not None

    def test_healer_naming_convention_class(self):
        """Test HealerNamingConvention class exists."""
        from agentic_core import HealerNamingConvention
        assert HealerNamingConvention is not None

    def test_healer_naming_convention_callable(self):
        """Test healer_naming_convention functions are callable."""
        from agentic_core import validate_healer_naming_convention
        assert callable(validate_healer_naming_convention)
