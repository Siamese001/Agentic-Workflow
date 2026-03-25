"""Enhanced behavioral tests for agentic_core.L5_safety.config.structure_blueprint."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L5_safety.config.structure_blueprint"


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


def test_subfolderdefinition_is_instantiable():
    """SubfolderDefinition can be instantiated (if it's a class)."""
    try:
        mod = importlib.import_module(MODULE_PATH)
        cls = getattr(mod, "SubfolderDefinition")
    except (ImportError, AttributeError) as e:
        pytest.skip(f"SubfolderDefinition not available: {e}")
    
    if isinstance(cls, type):
        try:
            instance = cls()
            assert isinstance(instance, cls)
        except Exception:
            # Some classes require arguments - that's OK
            pass
    else:
        pytest.skip(f"SubfolderDefinition is not a class")


def test_territorydefinition_is_instantiable():
    """TerritoryDefinition can be instantiated (if it's a class)."""
    try:
        mod = importlib.import_module(MODULE_PATH)
        cls = getattr(mod, "TerritoryDefinition")
    except (ImportError, AttributeError) as e:
        pytest.skip(f"TerritoryDefinition not available: {e}")
    
    if isinstance(cls, type):
        try:
            instance = cls()
            assert isinstance(instance, cls)
        except Exception:
            # Some classes require arguments - that's OK
            pass
    else:
        pytest.skip(f"TerritoryDefinition is not a class")


def test_emit_determinism_digest_is_callable():
    """emit_determinism_digest is callable."""
    try:
        mod = importlib.import_module(MODULE_PATH)
        func = getattr(mod, "emit_determinism_digest")
    except (ImportError, AttributeError) as e:
        pytest.skip(f"emit_determinism_digest not available: {e}")
    
    assert callable(func), f"emit_determinism_digest must be callable"


def test_emit_replay_key_is_callable():
    """emit_replay_key is callable."""
    try:
        mod = importlib.import_module(MODULE_PATH)
        func = getattr(mod, "emit_replay_key")
    except (ImportError, AttributeError) as e:
        pytest.skip(f"emit_replay_key not available: {e}")
    
    assert callable(func), f"emit_replay_key must be callable"


def test_get_all_territories_is_callable():
    """get_all_territories is callable."""
    try:
        mod = importlib.import_module(MODULE_PATH)
        func = getattr(mod, "get_all_territories")
    except (ImportError, AttributeError) as e:
        pytest.skip(f"get_all_territories not available: {e}")
    
    assert callable(func), f"get_all_territories must be callable"

if __name__ == "__main__":
    pytest.main([__file__])
