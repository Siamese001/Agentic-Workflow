"""Test HealSchemaVisitorAdg functionality."""

from __future__ import annotations

import importlib

import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.heal_schema_visitor"


@pytest.fixture(scope="module")
def mod():
    return importlib.import_module(MODULE_PATH)


@pytest.mark.unit
class TestHealSchemaVisitorAdg:
    """Test HealSchemaVisitorAdg functionality."""

    def test_heal_schema_visitor_adg_imports(self, mod):
        """Test heal_schema_visitor module imports."""
        assert mod.__name__ == MODULE_PATH

    def test_heal_schema_visitor_adg_class(self, mod):
        """Test HealSchemaVisitor class exists."""
        assert hasattr(mod, "HealSchemaVisitor")

    def test_heal_schema_visitor_adg_callable(self, mod):
        """Test heal_schema_visitor functions are callable."""
        assert callable(mod.check_file)
        assert callable(mod.main)
