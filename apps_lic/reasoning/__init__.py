"""Lazy public exports for live reasoning agents."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS: dict[str, tuple[str, str]] = {
    "GovernanceShieldAgent": (
        "apps_lic.reasoning.GovernanceShieldAgent",
        "GovernanceShieldAgent",
    ),
    "LicHealingOrchestrator": (
        "apps_lic.reasoning.LicHealingOrchestrator",
        "LicHealingOrchestrator",
    ),
    "LicReflectionAgent": (
        "apps_lic.reasoning.LicReflectionAgent",
        "LicReflectionAgent",
    ),
    "LICValidationExecutor": (
        "apps_lic.reasoning.LICValidationExecutor",
        "LICValidationExecutor",
    ),
    "MessageComplianceAgent": (
        "apps_lic.reasoning.MessageComplianceAgent",
        "MessageComplianceAgent",
    ),
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr_name = _EXPORTS[name]
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
