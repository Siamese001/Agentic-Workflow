"""Integrations-tree mirror of ``apps_shared.adapters.rg_orchestrator_facade``.

Delegates PEP 562 lazy resolution to the primary facade module (W11-M3A).
"""

from __future__ import annotations

from typing import Any

from apps_shared.adapters import rg_orchestrator_facade as _primary

CANONICAL_PRODUCT_MODULE = _primary.CANONICAL_PRODUCT_MODULE
CANONICAL_DISPATCH_MODULE = _primary.CANONICAL_DISPATCH_MODULE
CANONICAL_DISPATCH_SYMBOL = _primary.CANONICAL_DISPATCH_SYMBOL
CANONICAL_SECTION_LANE_PACKAGE = _primary.CANONICAL_SECTION_LANE_PACKAGE

_LAZY_SYMBOLS = _primary._LAZY_SYMBOLS


def __getattr__(name: str) -> Any:
    return getattr(_primary, name)


def __dir__() -> list[str]:
    return sorted(set(globals().keys()) | set(_LAZY_SYMBOLS.keys()))


__all__ = list(_LAZY_SYMBOLS.keys())
