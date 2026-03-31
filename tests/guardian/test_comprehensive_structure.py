"""Test ComprehensiveStructure functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestComprehensiveStructure:
    """Test ComprehensiveStructure functionality."""

    def test_comprehensive_structure_imports(self):
        """Test comprehensive_structure module imports."""
        from agentic_core import comprehensive_structure
        assert comprehensive_structure is not None

    def test_comprehensive_structure_class(self):
        """Test ComprehensiveStructure class exists."""
        from agentic_core import ComprehensiveStructure
        assert ComprehensiveStructure is not None

    def test_comprehensive_structure_callable(self):
        """Test comprehensive_structure functions are callable."""
        from agentic_core import validate_comprehensive_structure
        assert callable(validate_comprehensive_structure)
