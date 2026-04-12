"""Test ResourcePredictionTypes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestResourcePredictionTypes:
    """Test ResourcePredictionTypes functionality."""

    def test_resource_prediction_types_imports(self):
        """Test resource_prediction_types module imports."""
        from agentic_core import resource_prediction_types

        assert resource_prediction_types is not None

    def test_resource_prediction_types_class(self):
        """Test ResourcePredictionTypes class exists."""
        from agentic_core import ResourcePredictionTypes

        assert ResourcePredictionTypes is not None

    def test_resource_prediction_types_callable(self):
        """Test resource_prediction_types functions are callable."""
        from agentic_core import validate_resource_prediction_types

        assert callable(validate_resource_prediction_types)
