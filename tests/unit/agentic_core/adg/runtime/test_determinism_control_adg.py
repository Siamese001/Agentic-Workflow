"""Test DeterminismControlAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDeterminismControlAdg:
    """Test DeterminismControlAdg functionality."""

    def test_determinism_control_adg_imports(self):
        """Test determinism_control_adg module imports."""
        from agentic_core import determinism_control_adg
        assert determinism_control_adg is not None

    def test_determinism_control_adg_class(self):
        """Test DeterminismControlAdg class exists."""
        from agentic_core import DeterminismControlAdg
        assert DeterminismControlAdg is not None

    def test_determinism_control_adg_callable(self):
        """Test determinism_control_adg functions are callable."""
        from agentic_core import validate_determinism_control_adg
        assert callable(validate_determinism_control_adg)
