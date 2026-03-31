"""Test ReasoningIntensityTypes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReasoningIntensityTypes:
    """Test ReasoningIntensityTypes functionality."""

    def test_reasoning_intensity_types_imports(self):
        """Test reasoning_intensity_types module imports."""
        from agentic_core import reasoning_intensity_types
        assert reasoning_intensity_types is not None

    def test_reasoning_intensity_types_class(self):
        """Test ReasoningIntensityTypes class exists."""
        from agentic_core import ReasoningIntensityTypes
        assert ReasoningIntensityTypes is not None

    def test_reasoning_intensity_types_callable(self):
        """Test reasoning_intensity_types functions are callable."""
        from agentic_core import validate_reasoning_intensity_types
        assert callable(validate_reasoning_intensity_types)
