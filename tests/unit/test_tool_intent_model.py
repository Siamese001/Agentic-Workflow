"""Test ToolIntentModel functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestToolIntentModel:
    """Test ToolIntentModel functionality."""

    def test_tool_intent_model_imports(self):
        """Test tool_intent_model module imports."""
        from agentic_core import tool_intent_model
        assert tool_intent_model is not None

    def test_tool_intent_model_class(self):
        """Test ToolIntentModel class exists."""
        from agentic_core import ToolIntentModel
        assert ToolIntentModel is not None

    def test_tool_intent_model_callable(self):
        """Test tool_intent_model functions are callable."""
        from agentic_core import validate_tool_intent_model
        assert callable(validate_tool_intent_model)
