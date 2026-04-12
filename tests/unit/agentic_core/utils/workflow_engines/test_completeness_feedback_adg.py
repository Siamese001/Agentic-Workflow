"""Test CompletenessFeedbackAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCompletenessFeedbackAdg:
    """Test CompletenessFeedbackAdg functionality."""

    def test_completeness_feedback_adg_imports(self):
        """Test completeness_feedback_adg module imports."""
        from agentic_core import completeness_feedback_adg

        assert completeness_feedback_adg is not None

    def test_completeness_feedback_adg_class(self):
        """Test CompletenessFeedbackAdg class exists."""
        from agentic_core import CompletenessFeedbackAdg

        assert CompletenessFeedbackAdg is not None

    def test_completeness_feedback_adg_callable(self):
        """Test completeness_feedback_adg functions are callable."""
        from agentic_core import validate_completeness_feedback_adg

        assert callable(validate_completeness_feedback_adg)
