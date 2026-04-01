"""Test InitAdg functionality."""

from __future__ import annotations

import importlib

import pytest


@pytest.mark.unit
class TestInitAdg:
    """Test InitAdg functionality."""

    def test___init___adg_imports(self):
        """Test __init___adg module imports."""
        mod = importlib.import_module("agentic_core")
        assert hasattr(mod, "__init___adg")

    def test___init___adg_class(self):
        """Test InitAdg class exists."""
        mod = importlib.import_module("agentic_core")
        assert hasattr(mod, "InitAdg")

    def test___init___adg_callable(self):
        """Test __init___adg functions are callable."""
        mod = importlib.import_module("agentic_core")
        assert callable(mod.validate___init___adg)
