"""Test CitationEnforcement functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCitationEnforcement:
    """Test CitationEnforcement functionality."""

    def test_citation_enforcement_imports(self):
        """Test citation_enforcement module imports."""
        from agentic_core import citation_enforcement
        assert citation_enforcement is not None

    def test_citation_enforcement_class(self):
        """Test CitationEnforcement class exists."""
        from agentic_core import CitationEnforcement
        assert CitationEnforcement is not None

    def test_citation_enforcement_callable(self):
        """Test citation_enforcement functions are callable."""
        from agentic_core import validate_citation_enforcement
        assert callable(validate_citation_enforcement)
