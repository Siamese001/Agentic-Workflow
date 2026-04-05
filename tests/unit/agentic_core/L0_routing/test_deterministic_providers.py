"""Test DeterministicProviders functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDeterministicProviders:
    """Test DeterministicProviders functionality."""

    def test_deterministic_providers_imports(self):
        """Test deterministic_providers module imports."""
        from agentic_core import deterministic_providers
        assert deterministic_providers is not None

    def test_deterministic_providers_class(self):
        """Test DeterministicProviders class exists."""
        from agentic_core import DeterministicProviders
        assert DeterministicProviders is not None

    def test_deterministic_providers_callable(self):
        """Test deterministic_providers functions are callable."""
        from agentic_core import validate_deterministic_providers
        assert callable(validate_deterministic_providers)
