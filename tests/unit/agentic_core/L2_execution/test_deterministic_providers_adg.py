"""Test DeterministicProvidersAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDeterministicProvidersAdg:
    """Test DeterministicProvidersAdg functionality."""

    def test_deterministic_providers_adg_imports(self):
        """Test deterministic_providers_adg module imports."""
        from agentic_core import deterministic_providers_adg
        assert deterministic_providers_adg is not None

    def test_deterministic_providers_adg_class(self):
        """Test DeterministicProvidersAdg class exists."""
        from agentic_core import DeterministicProvidersAdg
        assert DeterministicProvidersAdg is not None

    def test_deterministic_providers_adg_callable(self):
        """Test deterministic_providers_adg functions are callable."""
        from agentic_core import validate_deterministic_providers_adg
        assert callable(validate_deterministic_providers_adg)
