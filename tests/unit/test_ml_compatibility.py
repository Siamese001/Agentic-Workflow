"""Test MlCompatibility functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMlCompatibility:
    """Test MlCompatibility functionality."""

    def test_ml_compatibility_imports(self):
        """Test ml_compatibility module imports."""
        from agentic_core import ml_compatibility
        assert ml_compatibility is not None

    def test_ml_compatibility_class(self):
        """Test MlCompatibility class exists."""
        from agentic_core import MlCompatibility
        assert MlCompatibility is not None

    def test_ml_compatibility_callable(self):
        """Test ml_compatibility functions are callable."""
        from agentic_core import validate_ml_compatibility
        assert callable(validate_ml_compatibility)
