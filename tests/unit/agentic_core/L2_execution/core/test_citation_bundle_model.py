"""Test CitationBundleModel functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCitationBundleModel:
    """Test CitationBundleModel functionality."""

    def test_citation_bundle_imports(self):
        """Test citation bundle module imports."""
        from agentic_core.L1_cognition import citation_bundle_model

        assert citation_bundle_model is not None

    def test_citation_bundle_class(self):
        """Test citation bundle class exists."""
        from agentic_core.L1_cognition.citation_bundle_model import CitationBundle

        assert CitationBundle is not None

    def test_validate_citation_bundle(self):
        """Test validate citation bundle function."""
        from agentic_core.L1_cognition.citation_bundle_model import validate_citation_bundle

        assert callable(validate_citation_bundle)
