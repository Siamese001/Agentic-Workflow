"""Boundary facade for apps_* code that needs canonical ``apps_rg`` product dispatch.

Cross-app coupling is limited to ``run_canonical_apps_rg_from_cli_primitives`` (W11-M3A).
Legacy ``RgResumeOrchestrator`` was removed in plan ``apps-rg-reasoning-deletion-d4e8f1``.

Lazy-resolution semantics
-------------------------
PEP 562 ``__getattr__`` defers the underlying import until first access.
"""

from __future__ import annotations

from typing import Any

CANONICAL_PRODUCT_MODULE = "apps_rg"
CANONICAL_DISPATCH_MODULE = "apps_rg.runtime.orchestration.canonical_dispatch"
CANONICAL_DISPATCH_SYMBOL = "run_canonical_apps_rg_from_cli_primitives"
CANONICAL_SECTION_LANE_PACKAGE = "apps_rg.runtime.sections"

_LAZY_SYMBOLS: dict[str, tuple[str, str]] = {
    "run_canonical_apps_rg_from_cli_primitives": (
        CANONICAL_DISPATCH_MODULE,
        CANONICAL_DISPATCH_SYMBOL,
    ),
}


def __getattr__(name: str) -> Any:
    """PEP 562 lazy-resolve facade symbols on first access."""
    if name in _LAZY_SYMBOLS:
        import importlib  # noqa: PLC0415

        mod_path, sym = _LAZY_SYMBOLS[name]
        module = importlib.import_module(mod_path)
        attr = getattr(module, sym)
        globals()[name] = attr
        return attr
    raise AttributeError(
        f"module 'apps_shared.adapters.rg_orchestrator_facade' has no attribute {name!r}"
    )


def __dir__() -> list[str]:
    return sorted(set(globals().keys()) | set(_LAZY_SYMBOLS.keys()))


__all__ = list(_LAZY_SYMBOLS.keys())
