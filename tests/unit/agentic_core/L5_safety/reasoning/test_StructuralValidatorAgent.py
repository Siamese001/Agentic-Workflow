"""Test Structuralvalidatoragent functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestStructuralvalidatoragent:
    """Test Structuralvalidatoragent functionality."""

    def test_StructuralValidatorAgent_imports(self):
        """Test StructuralValidatorAgent module imports."""
        from agentic_core import StructuralValidatorAgent

        assert StructuralValidatorAgent is not None

    def test_StructuralValidatorAgent_class(self):
        """Test Structuralvalidatoragent class exists."""
        from agentic_core import Structuralvalidatoragent

        assert Structuralvalidatoragent is not None

    def test_StructuralValidatorAgent_callable(self):
        """Test StructuralValidatorAgent functions are callable."""
        from agentic_core import validate_StructuralValidatorAgent

        assert callable(validate_StructuralValidatorAgent)
