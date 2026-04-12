"""Test TypesInitAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestTypesInitAdg:
    """Test TypesInitAdg functionality."""

    def test_types_init_adg_imports(self):
        """Test types_init_adg module imports."""
        from agentic_core import types_init_adg

        assert types_init_adg is not None

    def test_types_init_adg_class(self):
        """Test TypesInitAdg class exists."""
        from agentic_core import TypesInitAdg

        assert TypesInitAdg is not None

    def test_types_init_adg_callable(self):
        """Test types_init_adg functions are callable."""
        from agentic_core import validate_types_init_adg

        assert callable(validate_types_init_adg)
