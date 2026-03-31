"""Test Mixins functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMixins:
    """Test Mixins functionality."""

    def test_mixins_imports(self):
        """Test mixins module imports."""
        from agentic_core import mixins
        assert mixins is not None

    def test_mixins_class(self):
        """Test Mixins class exists."""
        from agentic_core import Mixins
        assert Mixins is not None

    def test_mixins_callable(self):
        """Test mixins functions are callable."""
        from agentic_core import validate_mixins
        assert callable(validate_mixins)
