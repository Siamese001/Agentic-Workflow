"""Test RegistryCompleteness functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRegistryCompleteness:
    """Test RegistryCompleteness functionality."""

    def test_registry_completeness_imports(self):
        """Test registry_completeness module imports."""
        from agentic_core import registry_completeness
        assert registry_completeness is not None

    def test_registry_completeness_class(self):
        """Test RegistryCompleteness class exists."""
        from agentic_core import RegistryCompleteness
        assert RegistryCompleteness is not None

    def test_registry_completeness_callable(self):
        """Test registry_completeness functions are callable."""
        from agentic_core import validate_registry_completeness
        assert callable(validate_registry_completeness)
