"""Test BaseResearchEngineMixins functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBaseResearchEngineMixins:
    """Test BaseResearchEngineMixins functionality."""

    def test_base_research_engine_mixins_imports(self):
        """Test base_research_engine_mixins module imports."""
        from agentic_core import base_research_engine_mixins
        assert base_research_engine_mixins is not None

    def test_base_research_engine_mixins_class(self):
        """Test BaseResearchEngineMixins class exists."""
        from agentic_core import BaseResearchEngineMixins
        assert BaseResearchEngineMixins is not None

    def test_base_research_engine_mixins_callable(self):
        """Test base_research_engine_mixins functions are callable."""
        from agentic_core import validate_base_research_engine_mixins
        assert callable(validate_base_research_engine_mixins)
