"""Test DeterminismAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDeterminismAdg:
    """Test DeterminismAdg functionality."""

    def test_determinism_adg_imports(self):
        """Test determinism_adg module imports."""
        from agentic_core import determinism_adg
        assert determinism_adg is not None

    def test_determinism_adg_class(self):
        """Test DeterminismAdg class exists."""
        from agentic_core import DeterminismAdg
        assert DeterminismAdg is not None

    def test_determinism_adg_callable(self):
        """Test determinism_adg functions are callable."""
        from agentic_core import validate_determinism_adg
        assert callable(validate_determinism_adg)
