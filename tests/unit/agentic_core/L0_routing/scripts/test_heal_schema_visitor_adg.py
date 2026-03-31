"""Test HealSchemaVisitorAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHealSchemaVisitorAdg:
    """Test HealSchemaVisitorAdg functionality."""

    def test_heal_schema_visitor_adg_imports(self):
        """Test heal_schema_visitor_adg module imports."""
        from agentic_core import heal_schema_visitor_adg
        assert heal_schema_visitor_adg is not None

    def test_heal_schema_visitor_adg_class(self):
        """Test HealSchemaVisitorAdg class exists."""
        from agentic_core import HealSchemaVisitorAdg
        assert HealSchemaVisitorAdg is not None

    def test_heal_schema_visitor_adg_callable(self):
        """Test heal_schema_visitor_adg functions are callable."""
        from agentic_core import validate_heal_schema_visitor_adg
        assert callable(validate_heal_schema_visitor_adg)
