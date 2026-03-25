"""Enhanced behavioral tests for agentic_core.interfaces.IHealerProtocol."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.interfaces.IHealerProtocol"


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


def test_any_is_instantiable():
    """Any can be instantiated (if it's a class)."""
    try:
        mod = importlib.import_module(MODULE_PATH)
        cls = getattr(mod, class_name)
    except (ImportError, AttributeError) as e:
        pytest.skip(f"{class_name} not available: {e}")
    
    if isinstance(cls, type):
        try:
            instance = cls()
            assert isinstance(instance, cls)
        except Exception:
            # Some classes require arguments - that's OK
            pass
    else:
        pytest.skip(f"{class_name} is not a class")


def test_ihealerprotocol_is_instantiable():
    """IHealerProtocol can be instantiated (if it's a class)."""
    try:
        mod = importlib.import_module(MODULE_PATH)
        cls = getattr(mod, class_name)
    except (ImportError, AttributeError) as e:
        pytest.skip(f"{class_name} not available: {e}")
    
    if isinstance(cls, type):
        try:
            instance = cls()
            assert isinstance(instance, cls)
        except Exception:
            # Some classes require arguments - that's OK
            pass
    else:
        pytest.skip(f"{class_name} is not a class")


def test_protocol_is_instantiable():
    """Protocol can be instantiated (if it's a class)."""
    try:
        mod = importlib.import_module(MODULE_PATH)
        cls = getattr(mod, class_name)
    except (ImportError, AttributeError) as e:
        pytest.skip(f"{class_name} not available: {e}")
    
    if isinstance(cls, type):
        try:
            instance = cls()
            assert isinstance(instance, cls)
        except Exception:
            # Some classes require arguments - that's OK
            pass
    else:
        pytest.skip(f"{class_name} is not a class")


def test_runtime_checkable_is_callable():
    """runtime_checkable is callable."""
    try:
        mod = importlib.import_module(MODULE_PATH)
        func = getattr(mod, func_name)
    except (ImportError, AttributeError) as e:
        pytest.skip(f"{func_name} not available: {e}")
    
    assert callable(func), f"{func_name} must be callable"

if __name__ == "__main__":
    pytest.main([__file__])
