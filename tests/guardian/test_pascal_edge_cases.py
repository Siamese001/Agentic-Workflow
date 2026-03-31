"""Test PascalEdgeCases functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPascalEdgeCases:
    """Test PascalEdgeCases functionality."""

    def test_pascal_edge_cases_imports(self):
        """Test pascal_edge_cases module imports."""
        from agentic_core import pascal_edge_cases
        assert pascal_edge_cases is not None

    def test_pascal_edge_cases_class(self):
        """Test PascalEdgeCases class exists."""
        from agentic_core import PascalEdgeCases
        assert PascalEdgeCases is not None

    def test_pascal_edge_cases_callable(self):
        """Test pascal_edge_cases functions are callable."""
        from agentic_core import validate_pascal_edge_cases
        assert callable(validate_pascal_edge_cases)
