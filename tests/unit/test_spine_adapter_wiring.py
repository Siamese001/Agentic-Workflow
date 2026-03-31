"""Test SpineAdapterWiring functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSpineAdapterWiring:
    """Test SpineAdapterWiring functionality."""

    def test_spine_adapter_wiring_imports(self):
        """Test spine_adapter_wiring module imports."""
        from agentic_core import spine_adapter_wiring
        assert spine_adapter_wiring is not None

    def test_spine_adapter_wiring_class(self):
        """Test SpineAdapterWiring class exists."""
        from agentic_core import SpineAdapterWiring
        assert SpineAdapterWiring is not None

    def test_spine_adapter_wiring_callable(self):
        """Test spine_adapter_wiring functions are callable."""
        from agentic_core import validate_spine_adapter_wiring
        assert callable(validate_spine_adapter_wiring)
