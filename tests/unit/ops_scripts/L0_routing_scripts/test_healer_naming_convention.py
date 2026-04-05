"""Test HealerNamingConvention functionality."""

from __future__ import annotations

import importlib

import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.run_hygiene_naming_audit_util"


@pytest.fixture(scope="module")
def mod():
    return importlib.import_module(MODULE_PATH)


@pytest.mark.unit
class TestHealerNamingConvention:
    """Test HealerNamingConvention functionality."""

    def test_healer_naming_convention_imports(self, mod):
        """Test hygiene naming audit module imports."""
        assert mod.__name__ == MODULE_PATH

    def test_healer_naming_convention_class(self, mod):
        """Test main entry point exists."""
        assert callable(mod.main)

    def test_healer_naming_convention_callable(self, mod):
        """Test hygiene naming audit callable contract."""
        assert callable(mod.main)
