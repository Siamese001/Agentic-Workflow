"""Test HygieneRegistry functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHygieneRegistry:
    """Test HygieneRegistry functionality."""

    def test_hygiene_registry_imports(self):
        """Test hygiene_registry module imports."""
        from agentic_core import hygiene_registry
        assert hygiene_registry is not None

    def test_hygiene_registry_class(self):
        """Test HygieneRegistry class exists."""
        from agentic_core import HygieneRegistry
        assert HygieneRegistry is not None

    def test_hygiene_registry_callable(self):
        """Test hygiene_registry functions are callable."""
        from agentic_core import validate_hygiene_registry
        assert callable(validate_hygiene_registry)
