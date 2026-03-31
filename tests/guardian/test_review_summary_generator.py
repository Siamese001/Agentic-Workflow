"""Test ReviewSummaryGenerator functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReviewSummaryGenerator:
    """Test ReviewSummaryGenerator functionality."""

    def test_review_summary_generator_imports(self):
        """Test review_summary_generator module imports."""
        from agentic_core import review_summary_generator
        assert review_summary_generator is not None

    def test_review_summary_generator_class(self):
        """Test ReviewSummaryGenerator class exists."""
        from agentic_core import ReviewSummaryGenerator
        assert ReviewSummaryGenerator is not None

    def test_review_summary_generator_callable(self):
        """Test review_summary_generator functions are callable."""
        from agentic_core import validate_review_summary_generator
        assert callable(validate_review_summary_generator)
