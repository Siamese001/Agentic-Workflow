"""Test SsotMixinStack functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSsotMixinStack:
    """Test SsotMixinStack functionality."""

    def test_ssot_mixin_stack_imports(self):
        """Test ssot_mixin_stack module imports."""
        from agentic_core import ssot_mixin_stack
        assert ssot_mixin_stack is not None

    def test_ssot_mixin_stack_class(self):
        """Test SsotMixinStack class exists."""
        from agentic_core import SsotMixinStack
        assert SsotMixinStack is not None

    def test_ssot_mixin_stack_callable(self):
        """Test ssot_mixin_stack functions are callable."""
        from agentic_core import validate_ssot_mixin_stack
        assert callable(validate_ssot_mixin_stack)
