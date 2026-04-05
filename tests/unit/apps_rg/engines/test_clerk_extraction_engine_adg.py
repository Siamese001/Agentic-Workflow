"""Test ClerkExtractionEngineAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestClerkExtractionEngineAdg:
    """Test ClerkExtractionEngineAdg functionality."""

    def test_clerk_extraction_engine_adg_imports(self):
        """Test clerk_extraction_engine_adg module imports."""
        from agentic_core import clerk_extraction_engine_adg
        assert clerk_extraction_engine_adg is not None

    def test_clerk_extraction_engine_adg_class(self):
        """Test ClerkExtractionEngineAdg class exists."""
        from agentic_core import ClerkExtractionEngineAdg
        assert ClerkExtractionEngineAdg is not None

    def test_clerk_extraction_engine_adg_callable(self):
        """Test clerk_extraction_engine_adg functions are callable."""
        from agentic_core import validate_clerk_extraction_engine_adg
        assert callable(validate_clerk_extraction_engine_adg)
