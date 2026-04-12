"""Test NormalizerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestNormalizerAdg:
    """Test NormalizerAdg functionality."""

    def test_normalizer_adg_imports(self):
        """Test normalizer_adg module imports."""
        from agentic_core import normalizer_adg

        assert normalizer_adg is not None

    def test_normalizer_adg_class(self):
        """Test NormalizerAdg class exists."""
        from agentic_core import NormalizerAdg

        assert NormalizerAdg is not None

    def test_normalizer_adg_callable(self):
        """Test normalizer_adg functions are callable."""
        from agentic_core import validate_normalizer_adg

        assert callable(validate_normalizer_adg)
