"""Test MlWriteIntentTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMlWriteIntentTypesAdg:
    """Test MlWriteIntentTypesAdg functionality."""

    def test_ml_write_intent_types_adg_imports(self):
        """Test ml_write_intent_types_adg module imports."""
        from agentic_core import ml_write_intent_types_adg

        assert ml_write_intent_types_adg is not None

    def test_ml_write_intent_types_adg_class(self):
        """Test MlWriteIntentTypesAdg class exists."""
        from agentic_core import MlWriteIntentTypesAdg

        assert MlWriteIntentTypesAdg is not None

    def test_ml_write_intent_types_adg_callable(self):
        """Test ml_write_intent_types_adg functions are callable."""
        from agentic_core import validate_ml_write_intent_types_adg

        assert callable(validate_ml_write_intent_types_adg)
