"""Test StructuredengineagentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestStructuredengineagentAdg:
    """Test StructuredengineagentAdg functionality."""

    def test_StructuredEngineAgent_adg_imports(self):
        """Test StructuredEngineAgent_adg module imports."""
        from agentic_core import StructuredEngineAgent_adg

        assert StructuredEngineAgent_adg is not None

    def test_StructuredEngineAgent_adg_class(self):
        """Test StructuredengineagentAdg class exists."""
        from agentic_core import StructuredengineagentAdg

        assert StructuredengineagentAdg is not None

    def test_StructuredEngineAgent_adg_callable(self):
        """Test StructuredEngineAgent_adg functions are callable."""
        from agentic_core import validate_StructuredEngineAgent_adg

        assert callable(validate_StructuredEngineAgent_adg)
