"""Test ExecuteMessageGenerationAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestExecuteMessageGenerationAdg:
    """Test ExecuteMessageGenerationAdg functionality."""

    def test_execute_message_generation_adg_imports(self):
        """Test execute_message_generation_adg module imports."""
        from agentic_core import execute_message_generation_adg
        assert execute_message_generation_adg is not None

    def test_execute_message_generation_adg_class(self):
        """Test ExecuteMessageGenerationAdg class exists."""
        from agentic_core import ExecuteMessageGenerationAdg
        assert ExecuteMessageGenerationAdg is not None

    def test_execute_message_generation_adg_callable(self):
        """Test execute_message_generation_adg functions are callable."""
        from agentic_core import validate_execute_message_generation_adg
        assert callable(validate_execute_message_generation_adg)
