"""Test HandlerAdg functionality."""

from __future__ import annotations

import importlib

import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.handler"


@pytest.fixture(scope="module")
def mod():
    return importlib.import_module(MODULE_PATH)


@pytest.mark.unit
class TestHandlerAdg:
    """Test HandlerAdg functionality."""

    def test_handler_adg_imports(self, mod):
        """Test handler module imports."""
        assert mod.__name__ == MODULE_PATH

    def test_handler_adg_callable(self, mod):
        """Test handler module exposes the dashboard debugger."""
        assert callable(mod.debug_dashboard)
