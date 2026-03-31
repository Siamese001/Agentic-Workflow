"""Test BuilderAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBuilderAdg:
    """Test BuilderAdg functionality."""

    def test_builder_adg_imports(self):
        """Test builder_adg module imports."""
        from agentic_core import builder_adg
        assert builder_adg is not None

    def test_builder_adg_class(self):
        """Test BuilderAdg class exists."""
        from agentic_core import BuilderAdg
        assert BuilderAdg is not None

    def test_builder_adg_callable(self):
        """Test builder_adg functions are callable."""
        from agentic_core import validate_builder_adg
        assert callable(validate_builder_adg)
