"""Test ReasoningIntensityTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReasoningIntensityTypesAdg:
    """Test ReasoningIntensityTypesAdg functionality."""

    def test_reasoning_intensity_types_adg_imports(self):
        """Test reasoning_intensity_types_adg module imports."""
        from agentic_core import reasoning_intensity_types_adg

        assert reasoning_intensity_types_adg is not None

    def test_reasoning_intensity_types_adg_class(self):
        """Test ReasoningIntensityTypesAdg class exists."""
        from agentic_core import ReasoningIntensityTypesAdg

        assert ReasoningIntensityTypesAdg is not None

    def test_reasoning_intensity_types_adg_callable(self):
        """Test reasoning_intensity_types_adg functions are callable."""
        from agentic_core import validate_reasoning_intensity_types_adg

        assert callable(validate_reasoning_intensity_types_adg)
