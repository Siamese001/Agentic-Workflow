"""Lazy public exports for reasoning agents.

Do not eagerly import heavy agent modules at package import time. Several of
them pull optional repo-only dependencies; eager imports make unrelated tests
and consumers fail during collection.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS: dict[str, tuple[str, str]] = {
    "OutreachLearningAgent": (
        "apps_lic.reasoning.OutreachLearningAgent",
        "OutreachLearningAgent",
    ),
    "OutreachValidationExecutorAgent": (
        "apps_lic.reasoning.OutreachValidationExecutorAgent",
        "OutreachValidationExecutorAgent",
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
