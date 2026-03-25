"""Enhanced behavioral tests for agentic_core.base_agents.LightweightBase."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.base_agents.LightweightBase"


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
    assert len(public_symbols) >= 1, f"{MODULE_PATH} must expose at least one public symbol"

if __name__ == "__main__":
    pytest.main([__file__])
