"""Test L2executionbaseAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestL2executionbaseAdg:
    """Test L2executionbaseAdg functionality."""

    def test_L2ExecutionBase_adg_imports(self):
        """Test L2ExecutionBase_adg module imports."""
        from agentic_core import L2ExecutionBase_adg

        assert L2ExecutionBase_adg is not None

    def test_L2ExecutionBase_adg_class(self):
        """Test L2executionbaseAdg class exists."""
        from agentic_core import L2executionbaseAdg

        assert L2executionbaseAdg is not None

    def test_L2ExecutionBase_adg_callable(self):
        """Test L2ExecutionBase_adg functions are callable."""
        from agentic_core import validate_L2ExecutionBase_adg

        assert callable(validate_L2ExecutionBase_adg)
