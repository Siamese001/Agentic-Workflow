"""Test MixinEnforcement functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMixinEnforcement:
    """Test MixinEnforcement functionality."""

    def test_mixin_enforcement_imports(self):
        """Test mixin_enforcement module imports."""
        from agentic_core import mixin_enforcement

        assert mixin_enforcement is not None

    def test_mixin_enforcement_class(self):
        """Test MixinEnforcement class exists."""
        from agentic_core import MixinEnforcement

        assert MixinEnforcement is not None

    def test_mixin_enforcement_callable(self):
        """Test mixin_enforcement functions are callable."""
        from agentic_core import validate_mixin_enforcement

        assert callable(validate_mixin_enforcement)
