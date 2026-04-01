"""Test HygieneRegistry functionality."""

from __future__ import annotations

import importlib

import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.root_hygiene_util"


@pytest.fixture(scope="module")
def mod():
    return importlib.import_module(MODULE_PATH)


@pytest.mark.unit
class TestHygieneRegistry:
    """Test HygieneRegistry functionality."""

    def test_hygiene_registry_imports(self, mod):
        """Test root hygiene utility module imports."""
        assert mod.__name__ == MODULE_PATH

    def test_hygiene_registry_class(self, mod):
        """Test root hygiene utility exposes the project root resolver."""
        assert callable(mod.get_project_root)

    def test_hygiene_registry_callable(self, mod):
        """Test hygiene utility functions are callable."""
        assert callable(mod.get_project_root)
        assert callable(mod.enforce_root_hygiene)
