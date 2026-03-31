"""Test StructureHealers functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestStructureHealers:
    """Test StructureHealers functionality."""

    def test_structure_healers_imports(self):
        """Test structure_healers module imports."""
        from agentic_core import structure_healers
        assert structure_healers is not None

    def test_structure_healers_class(self):
        """Test StructureHealers class exists."""
        from agentic_core import StructureHealers
        assert StructureHealers is not None

    def test_structure_healers_callable(self):
        """Test structure_healers functions are callable."""
        from agentic_core import validate_structure_healers
        assert callable(validate_structure_healers)
