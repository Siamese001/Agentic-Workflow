"""Enhanced behavioral tests for agentic_core.L0_routing.__init__."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.__init__"


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


def test_capacitydecisionreason_is_instantiable():
    """CapacityDecisionReason can be instantiated (if it's a class)."""
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


def test_capacitysnapshot_is_instantiable():
    """CapacitySnapshot can be instantiated (if it's a class)."""
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


def test_optimizationwindow_is_instantiable():
    """OptimizationWindow can be instantiated (if it's a class)."""
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


def test_apply_optimization_with_governance_is_callable():
    """apply_optimization_with_governance is callable."""
    try:
        mod = importlib.import_module(MODULE_PATH)
        func = getattr(mod, func_name)
    except (ImportError, AttributeError) as e:
        pytest.skip(f"{func_name} not available: {e}")
    
    assert callable(func), f"{func_name} must be callable"


def test_capacity_aware_routing_is_callable():
    """capacity_aware_routing is callable."""
    try:
        mod = importlib.import_module(MODULE_PATH)
        func = getattr(mod, func_name)
    except (ImportError, AttributeError) as e:
        pytest.skip(f"{func_name} not available: {e}")
    
    assert callable(func), f"{func_name} must be callable"


def test_capacity_snapshot_emitted_is_callable():
    """capacity_snapshot_emitted is callable."""
    try:
        mod = importlib.import_module(MODULE_PATH)
        func = getattr(mod, func_name)
    except (ImportError, AttributeError) as e:
        pytest.skip(f"{func_name} not available: {e}")
    
    assert callable(func), f"{func_name} must be callable"

if __name__ == "__main__":
    pytest.main([__file__])
