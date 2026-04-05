"""Test NestedLcdPrevention functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestNestedLcdPrevention:
    """Test NestedLcdPrevention functionality."""

    def test_nested_lcd_prevention_imports(self):
        """Test nested_lcd_prevention module imports."""
        from agentic_core import nested_lcd_prevention
        assert nested_lcd_prevention is not None

    def test_nested_lcd_prevention_class(self):
        """Test NestedLcdPrevention class exists."""
        from agentic_core import NestedLcdPrevention
        assert NestedLcdPrevention is not None

    def test_nested_lcd_prevention_callable(self):
        """Test nested_lcd_prevention functions are callable."""
        from agentic_core import validate_nested_lcd_prevention
        assert callable(validate_nested_lcd_prevention)
