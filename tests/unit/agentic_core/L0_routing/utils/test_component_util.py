"""Test ComponentUtil functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestComponentUtil:
    """Test ComponentUtil functionality."""

    def test_component_util_imports(self):
        """Test component_util module imports."""
        from agentic_core import component_util
        assert component_util is not None

    def test_component_util_class(self):
        """Test ComponentUtil class exists."""
        from agentic_core import ComponentUtil
        assert ComponentUtil is not None

    def test_component_util_callable(self):
        """Test component_util functions are callable."""
        from agentic_core import validate_component_util
        assert callable(validate_component_util)
