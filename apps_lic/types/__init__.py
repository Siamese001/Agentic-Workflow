"""Stable public type exports for apps_lic.

Expose the lightweight public contract from one place and lazy-load heavier
types only when explicitly requested. This prevents package-level import
explosions and keeps `from apps_lic.types import ...` stable.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

from .lic_types import (
    CampaignConfig,
    CampaignRequest,
    CampaignResult,
    CampaignRunSummary,
    Draft,
    DraftPackage,
    ValidationResult,
)

_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "OutreachMission": ("apps_lic.types.lic_models_types", "OutreachMission"),
    "TraceRegistry": ("apps_lic.types.TraceRegistry", "TraceRegistry"),
}

__all__ = [
    "CampaignConfig",
    "CampaignRequest",
    "CampaignResult",
    "CampaignRunSummary",
    "Draft",
    "DraftPackage",
    "ValidationResult",
    "OutreachMission",
    "TraceRegistry",
]


def __getattr__(name: str) -> Any:
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr_name = _LAZY_EXPORTS[name]
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
