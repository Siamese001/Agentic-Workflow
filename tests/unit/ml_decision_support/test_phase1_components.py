"""Test Phase1Components functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPhase1Components:
    """Test Phase1Components functionality."""

    def test_phase1_components_imports(self):
        """Test phase1_components module imports."""
        from agentic_core import phase1_components
        assert phase1_components is not None

    def test_phase1_components_class(self):
        """Test Phase1Components class exists."""
        from agentic_core import Phase1Components
        assert Phase1Components is not None

    def test_phase1_components_callable(self):
        """Test phase1_components functions are callable."""
        from agentic_core import validate_phase1_components
        assert callable(validate_phase1_components)
