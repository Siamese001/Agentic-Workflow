"""Test NestedLcdDetectionHook functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestNestedLcdDetectionHook:
    """Test NestedLcdDetectionHook functionality."""

    def test_nested_lcd_detection_hook_imports(self):
        """Test nested_lcd_detection_hook module imports."""
        from agentic_core import nested_lcd_detection_hook

        assert nested_lcd_detection_hook is not None

    def test_nested_lcd_detection_hook_class(self):
        """Test NestedLcdDetectionHook class exists."""
        from agentic_core import NestedLcdDetectionHook

        assert NestedLcdDetectionHook is not None

    def test_nested_lcd_detection_hook_callable(self):
        """Test nested_lcd_detection_hook functions are callable."""
        from agentic_core import validate_nested_lcd_detection_hook

        assert callable(validate_nested_lcd_detection_hook)
