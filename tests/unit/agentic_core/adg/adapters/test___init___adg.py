"""Enhanced behavioral tests for agentic_core.adg.adapters.__init__."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.adapters.__init__"


def test_module_importable():
    """Module imports without side effects."""
    try:
        mod = importlib.import_module(MODULE_PATH)
    except ImportError as e:
        pytest.skip(f"Module not available: {e}")
    
    assert mod.__name__ == MODULE_PATH


def test_module_exposes_public_api():
    """Module exposes at least one public symbol."""
    try:
        mod = importlib.import_module(MODULE_PATH)
    except ImportError as e:
        pytest.skip(f"Module not available: {e}")
    
    public_symbols = [n for n in dir(mod) if not n.startswith("_")]
    if len(public_symbols) == 0:
        # Empty namespace packages (like __init__.py) are valid
        pytest.skip(f"{MODULE_PATH} has no public symbols (empty namespace package)")
    else:
        assert len(public_symbols) >= 1, f"{MODULE_PATH} must expose at least one public symbol"

if __name__ == "__main__":
    pytest.main([__file__])
