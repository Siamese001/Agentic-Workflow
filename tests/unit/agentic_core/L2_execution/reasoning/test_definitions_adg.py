"""Test DefinitionsAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDefinitionsAdg:
    """Test DefinitionsAdg functionality."""

    def test_definitions_adg_imports(self):
        """Test definitions_adg module imports."""
        from agentic_core import definitions_adg

        assert definitions_adg is not None

    def test_definitions_adg_class(self):
        """Test DefinitionsAdg class exists."""
        from agentic_core import DefinitionsAdg

        assert DefinitionsAdg is not None

    def test_definitions_adg_callable(self):
        """Test definitions_adg functions are callable."""
        from agentic_core import validate_definitions_adg

        assert callable(validate_definitions_adg)
