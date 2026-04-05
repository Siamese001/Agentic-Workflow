"""Test StructuralStrictness functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestStructuralStrictness:
    """Test StructuralStrictness functionality."""

    def test_structural_strictness_imports(self):
        """Test structural_strictness module imports."""
        from agentic_core import structural_strictness
        assert structural_strictness is not None

    def test_structural_strictness_class(self):
        """Test StructuralStrictness class exists."""
        from agentic_core import StructuralStrictness
        assert StructuralStrictness is not None

    def test_structural_strictness_callable(self):
        """Test structural_strictness functions are callable."""
        from agentic_core import validate_structural_strictness
        assert callable(validate_structural_strictness)
