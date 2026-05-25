"""Single boundary facade for apps_* code that needs ``system_learning`` surfaces.

This is the ONLY place ``apps_eval`` / ``apps_lic`` / future apps should import
``system_learning`` symbols from. Centralizing the dependency:

- Records exactly one ``apps_shared.adapters \u2192 system_learning`` edge in the
  ADG, instead of 10 edges scattered across app code (per plan
  ``apps-runtime-first-principles-e6ba58`` W3.2 + W3.3).
- Lets us swap or stub ``system_learning`` in one place if its API changes.
- Documents which ``system_learning`` symbols apps may consume.

Re-exports are resolved lazily via PEP 562 module ``__getattr__`` so that
environments without ``system_learning`` installed can still import this
facade without ``ImportError`` at module load time. ImportError surfaces
only at first use of a re-exported symbol \u2014 same behavior as the pre-W3
lazy-imports inside function bodies. Callers must keep their existing
``try/except ImportError`` wrappers if they want graceful degradation.

Symbols re-exported:

- ``get_sl_memory_bridge`` (memory bridge for regression / drift detection)
- ``get_process_bus``, ``MetaLearningChangePackage`` (meta-learning bus
  publish API)
- ``MetaLearningBus`` (port interface used by ``apps_lic`` spine adapter)
- ``get_current_adapter``, ``seal_step`` (runtime-ADG span emitter for
  Tier-3 step seals)
"""

from __future__ import annotations

from typing import Any

# Map facade attribute -> (upstream module path, upstream symbol name).
# Symbols are resolved on first access; subsequent accesses hit module globals
# (cached by ``__getattr__``).
_LAZY_SYMBOLS: dict[str, tuple[str, str]] = {
    "get_sl_memory_bridge": (
        "agentic_core.L6_system_learning.adapters.system_learning_memory_bridge",
        "get_sl_memory_bridge",
    ),
    "get_process_bus": (
        "agentic_core.L6_system_learning.meta_learning.meta_learning_bus",
        "get_process_bus",
    ),
    "MetaLearningChangePackage": (
        "agentic_core.L6_system_learning.meta_learning.meta_learning_bus",
        "MetaLearningChangePackage",
    ),
    "MetaLearningBus": (
        "agentic_core.L6_system_learning.ports.meta_learning_bus",
        "MetaLearningBus",
    ),
    "get_current_adapter": (
        "agentic_core.L6_system_learning.runtime_adg.runtime_span_emitter",
        "get_current_adapter",
    ),
    "seal_step": (
        "agentic_core.L6_system_learning.runtime_adg.runtime_span_emitter",
        "seal_step",
    ),
}


def __getattr__(name: str) -> Any:
    """PEP 562 lazy-resolve facade symbols on first access."""
    if name in _LAZY_SYMBOLS:
        import importlib  # noqa: PLC0415 \u2014 deferred to keep facade import lightweight

        mod_path, sym = _LAZY_SYMBOLS[name]
        module = importlib.import_module(mod_path)
        attr = getattr(module, sym)
        # Cache on the facade module so subsequent attribute lookups bypass
        # __getattr__ entirely.
        globals()[name] = attr
        return attr
    raise AttributeError(
        f"module 'apps_shared.adapters.system_learning_facade' has no attribute {name!r}"
    )


def __dir__() -> list[str]:
    """Expose lazy symbols to ``dir()`` and IDE introspection."""
    return sorted(set(globals().keys()) | set(_LAZY_SYMBOLS.keys()))


__all__ = list(_LAZY_SYMBOLS.keys())
