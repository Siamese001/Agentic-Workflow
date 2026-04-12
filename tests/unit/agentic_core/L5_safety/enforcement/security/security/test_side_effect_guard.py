"""Test SideEffectGuard functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSideEffectGuard:
    """Test SideEffectGuard functionality."""

    def test_side_effect_guard_imports(self):
        """Test side_effect_guard module imports."""
        from agentic_core import side_effect_guard

        assert side_effect_guard is not None

    def test_side_effect_guard_class(self):
        """Test SideEffectGuard class exists."""
        from agentic_core import SideEffectGuard

        assert SideEffectGuard is not None

    def test_side_effect_guard_callable(self):
        """Test side_effect_guard functions are callable."""
        from agentic_core import validate_side_effect_guard

        assert callable(validate_side_effect_guard)
