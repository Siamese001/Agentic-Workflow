"""
agentic_core package initialization.
"""
import importlib
from typing import Any

# Map of names to their module paths for lazy loading
_MODULE_MAP = {
    "InferenceEngine": "agentic_core.L1_cognition.inference.inference_engine",
    "SPIFFEManager": "agentic_core.L1_cognition.identity.spiffe_manager_impl",
    "SignalContext": "agentic_core.L1_cognition.context.signal_context",
    "tools": "agentic_core.tools.core"
}

def __getattr__(name: str) -> Any:
    """
    Lazy-load core components to prevent circular gravity leaks 
    during initial package discovery.
    """
    if name in _MODULE_MAP:
        module_path = _MODULE_MAP[name]
        module = importlib.import_module(module_path)
        
        # Handle both module-level imports and class-level exports
        if hasattr(module, name):
            return getattr(module, name)
        return module

    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = list(_MODULE_MAP.keys())
