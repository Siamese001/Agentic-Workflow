"""Test KeywordClassificationTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestKeywordClassificationTypesAdg:
    """Test KeywordClassificationTypesAdg functionality."""

    def test_keyword_classification_types_adg_imports(self):
        """Test keyword_classification_types_adg module imports."""
        from agentic_core import keyword_classification_types_adg

        assert keyword_classification_types_adg is not None

    def test_keyword_classification_types_adg_class(self):
        """Test KeywordClassificationTypesAdg class exists."""
        from agentic_core import KeywordClassificationTypesAdg

        assert KeywordClassificationTypesAdg is not None

    def test_keyword_classification_types_adg_callable(self):
        """Test keyword_classification_types_adg functions are callable."""
        from agentic_core import validate_keyword_classification_types_adg

        assert callable(validate_keyword_classification_types_adg)
