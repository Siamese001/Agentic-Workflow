"""Test ActionCallGeneratorTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestActionCallGeneratorTypesAdg:
    """Test ActionCallGeneratorTypesAdg functionality."""

    def test_action_call_generator_types_adg_imports(self):
        """Test action_call_generator_types_adg module imports."""
        from agentic_core import action_call_generator_types_adg
        assert action_call_generator_types_adg is not None

    def test_action_call_generator_types_adg_class(self):
        """Test ActionCallGeneratorTypesAdg class exists."""
        from agentic_core import ActionCallGeneratorTypesAdg
        assert ActionCallGeneratorTypesAdg is not None

    def test_action_call_generator_types_adg_callable(self):
        """Test action_call_generator_types_adg functions are callable."""
        from agentic_core import validate_action_call_generator_types_adg
        assert callable(validate_action_call_generator_types_adg)
