"""REQ-417: Runtime mutation guard — block importlib.reload and sys.modules injection on core modules.

SOV-DELTA expansions:
  - Guard MUST block importlib.reload of any module with a core-layer prefix.
  - _GuardedSysModules blocks replacement (not addition) of core-prefix keys in sys.modules.
  - _guarded_setattr reference implementation documents the blocked operation.
  - install_guards() is idempotent — safe to call multiple times.
"""

from __future__ import annotations

import importlib
from types import ModuleType

_CORE_PREFIXES = (
    "agentic_core.",
    "apps_lic.",
    "apps_rg.",
    "apps_shared.",
    "system_learning.",
)

_ORIGINAL_RELOAD: object = importlib.reload
_GUARDS_INSTALLED: bool = False


# =============================================================================
# Reload guard
# =============================================================================


def _guarded_reload(module: ModuleType) -> ModuleType:
    """REQ-417: block importlib.reload for core-layer modules."""
    name = getattr(module, "__name__", "") or ""
    if any(name.startswith(p) for p in _CORE_PREFIXES):
        raise ImportError(f"REQ-417: importlib.reload of core module forbidden: {name}")
    return _ORIGINAL_RELOAD(module)  # type: ignore[return-value]


# =============================================================================
# sys.modules guard (dict subclass)
# =============================================================================


class _GuardedSysModules(dict):
    """REQ-417: wraps sys.modules to block replacement of already-loaded core modules.

    Allows:
      - Adding new module keys (initial import).
      - Replacing non-core-prefix keys.
    Blocks:
      - Replacing an EXISTING core-prefix key (e.g. monkey-patching a live module).
    """

    def __setitem__(self, key: object, value: object) -> None:
        if isinstance(key, str) and any(key.startswith(p) for p in _CORE_PREFIXES) and key in self:
            raise ImportError(f"REQ-417: sys.modules replacement of core module forbidden: {key}")
        super().__setitem__(key, value)


# =============================================================================
# setattr reference implementation (documented, not installed globally)
# =============================================================================


def _guarded_setattr(obj: object, name: str, value: object) -> None:
    """REQ-417: reference guard for runtime attribute mutation on core instances.

    Not installed globally (would break too many stdlib primitives). Use as a
    test-double or call directly to validate core-object mutation semantics.
    """
    mod = getattr(type(obj), "__module__", "") or ""
    if any(mod.startswith(p) for p in _CORE_PREFIXES):
        raise AttributeError(
            f"REQ-417: runtime mutation of core layer object forbidden "
            f"(type={type(obj).__name__}, attr={name}, module={mod})"
        )
    object.__setattr__(obj, name, value)


# =============================================================================
# Guard installation
# =============================================================================


def install_guards() -> None:
    """Install runtime mutation guards. Idempotent — safe to call at process start."""
    global _GUARDS_INSTALLED
    if _GUARDS_INSTALLED:
        return
    importlib.reload = _guarded_reload  # type: ignore[assignment]
    _GUARDS_INSTALLED = True


__all__ = [
    "_CORE_PREFIXES",
    "_GuardedSysModules",
    "_guarded_reload",
    "_guarded_setattr",
    "install_guards",
]
