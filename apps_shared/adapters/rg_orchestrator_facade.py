"""Boundary facade for apps_* code that needs to consume ``apps_rg`` surfaces.

Today the only consumer is ``apps_eval`` (evaluation framework drives the
``RgResumeOrchestrator`` as part of resume-generation eval scenarios). This
facade centralizes that cross-app coupling so the ADG records one
``apps_shared.adapters \u2192 apps_rg`` edge instead of N edges from deep
``apps_eval`` modules.

Per plan ``apps-runtime-first-principles-e6ba58`` W3.1.

W11-M3A: documents and lazy-exports canonical product surfaces alongside the
legacy ``RgResumeOrchestrator`` eval symbol (legacy symbol retained for eval parity).

Lazy-resolution semantics
-------------------------
PEP 562 ``__getattr__`` defers the underlying import until first access.
Callers that previously wrapped the import in ``try/except`` (e.g. for
test environments where ``apps_rg`` may not be importable) keep that
behavior \u2014 the facade itself imports cleanly even when ``apps_rg`` is
missing, but first symbol access raises whatever the upstream raises.
"""

from __future__ import annotations

from typing import Any

# Canonical product path (W8 hygiene) — metadata for routing docs and new callers.
CANONICAL_PRODUCT_MODULE = "apps_rg"
CANONICAL_DISPATCH_MODULE = "apps_rg.runtime.orchestration.canonical_dispatch"
CANONICAL_DISPATCH_SYMBOL = "run_canonical_apps_rg_from_cli_primitives"
CANONICAL_SECTION_LANE_PACKAGE = "apps_rg.runtime.sections"

# Cross-app coupling surface. Keep this list tight \u2014 every entry here is a
# documented exception to the "apps_* should not depend on sibling apps" rule.
_LAZY_SYMBOLS: dict[str, tuple[str, str]] = {
    "RgResumeOrchestrator": (
        "apps_rg.reasoning.RgResumeOrchestrator",
        "RgResumeOrchestrator",
    ),
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
