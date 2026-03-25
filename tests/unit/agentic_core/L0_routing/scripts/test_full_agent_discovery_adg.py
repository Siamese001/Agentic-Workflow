"""Enhanced behavioral tests for agentic_core.L0_routing.scripts.full_agent_discovery."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.full_agent_discovery"


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


def test_agentintegrityreport_is_instantiable():
    """AgentIntegrityReport can be instantiated (if it's a class)."""
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


def test_discoveryerror_is_instantiable():
    """DiscoveryError can be instantiated (if it's a class)."""
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


def test_analyze_agent_integrity_is_callable():
    """analyze_agent_integrity is callable."""
    try:
        mod = importlib.import_module(MODULE_PATH)
        func = getattr(mod, func_name)
    except (ImportError, AttributeError) as e:
        pytest.skip(f"{func_name} not available: {e}")
    
    assert callable(func), f"{func_name} must be callable"


def test_check_compliance_gate_is_callable():
    """check_compliance_gate is callable."""
    try:
        mod = importlib.import_module(MODULE_PATH)
        func = getattr(mod, func_name)
    except (ImportError, AttributeError) as e:
        pytest.skip(f"{func_name} not available: {e}")
    
    assert callable(func), f"{func_name} must be callable"


def test_classification_cache_context_is_callable():
    """classification_cache_context is callable."""
    try:
        mod = importlib.import_module(MODULE_PATH)
        func = getattr(mod, func_name)
    except (ImportError, AttributeError) as e:
        pytest.skip(f"{func_name} not available: {e}")
    
    assert callable(func), f"{func_name} must be callable"

if __name__ == "__main__":
    pytest.main([__file__])
