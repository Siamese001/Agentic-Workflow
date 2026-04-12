"""Test CleanDuplicatesEnhanced functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCleanDuplicatesEnhanced:
    """Test CleanDuplicatesEnhanced functionality."""

    def test_clean_duplicates_enhanced_imports(self):
        """Test clean_duplicates_enhanced module imports."""
        from agentic_core import clean_duplicates_enhanced

        assert clean_duplicates_enhanced is not None

    def test_clean_duplicates_enhanced_class(self):
        """Test CleanDuplicatesEnhanced class exists."""
        from agentic_core import CleanDuplicatesEnhanced

        assert CleanDuplicatesEnhanced is not None

    def test_clean_duplicates_enhanced_callable(self):
        """Test clean_duplicates_enhanced functions are callable."""
        from agentic_core import validate_clean_duplicates_enhanced

        assert callable(validate_clean_duplicates_enhanced)
