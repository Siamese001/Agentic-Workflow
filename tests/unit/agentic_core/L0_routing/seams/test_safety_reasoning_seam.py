"""Test SafetyReasoningSeam functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSafetyReasoningSeam:
    """Test SafetyReasoningSeam functionality."""

    def test_safety_reasoning_seam_imports(self):
        """Test safety_reasoning_seam module imports."""
        from agentic_core import safety_reasoning_seam

        assert safety_reasoning_seam is not None

    def test_safety_reasoning_seam_class(self):
        """Test SafetyReasoningSeam class exists."""
        from agentic_core import SafetyReasoningSeam

        assert SafetyReasoningSeam is not None

    def test_safety_reasoning_seam_callable(self):
        """Test safety_reasoning_seam functions are callable."""
        from agentic_core import validate_safety_reasoning_seam

        assert callable(validate_safety_reasoning_seam)
