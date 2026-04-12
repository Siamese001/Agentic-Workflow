"""Test MroTypeSafety functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMroTypeSafety:
    """Test MroTypeSafety functionality."""

    def test_mro_type_safety_imports(self):
        """Test mro_type_safety module imports."""
        from agentic_core import mro_type_safety

        assert mro_type_safety is not None

    def test_mro_type_safety_class(self):
        """Test MroTypeSafety class exists."""
        from agentic_core import MroTypeSafety

        assert MroTypeSafety is not None

    def test_mro_type_safety_callable(self):
        """Test mro_type_safety functions are callable."""
        from agentic_core import validate_mro_type_safety

        assert callable(validate_mro_type_safety)
