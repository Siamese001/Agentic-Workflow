"""Test StructureDrift functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestStructureDrift:
    """Test StructureDrift functionality."""

    def test_structure_drift_imports(self):
        """Test structure_drift module imports."""
        from agentic_core import structure_drift
        assert structure_drift is not None

    def test_structure_drift_class(self):
        """Test StructureDrift class exists."""
        from agentic_core import StructureDrift
        assert StructureDrift is not None

    def test_structure_drift_callable(self):
        """Test structure_drift functions are callable."""
        from agentic_core import validate_structure_drift
        assert callable(validate_structure_drift)
