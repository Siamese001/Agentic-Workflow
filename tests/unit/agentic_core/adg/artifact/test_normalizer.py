"""Test Normalizer functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestNormalizer:
    """Test Normalizer functionality."""

    def test_normalizer_imports(self):
        """Test normalizer module imports."""
        from agentic_core import normalizer

        assert normalizer is not None

    def test_normalizer_class(self):
        """Test Normalizer class exists."""
        from agentic_core import Normalizer

        assert Normalizer is not None

    def test_normalizer_callable(self):
        """Test normalizer functions are callable."""
        from agentic_core import validate_normalizer

        assert callable(validate_normalizer)
