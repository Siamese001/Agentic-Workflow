"""Test PrecisionAtKAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPrecisionAtKAdg:
    """Test PrecisionAtKAdg functionality."""

    def test_precision_at_k_adg_imports(self):
        """Test precision_at_k_adg module imports."""
        from agentic_core import precision_at_k_adg

        assert precision_at_k_adg is not None

    def test_precision_at_k_adg_class(self):
        """Test PrecisionAtKAdg class exists."""
        from agentic_core import PrecisionAtKAdg

        assert PrecisionAtKAdg is not None

    def test_precision_at_k_adg_callable(self):
        """Test precision_at_k_adg functions are callable."""
        from agentic_core import validate_precision_at_k_adg

        assert callable(validate_precision_at_k_adg)
