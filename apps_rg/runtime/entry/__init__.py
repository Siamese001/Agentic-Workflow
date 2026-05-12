"""apps_rg runtime entrypoints.

Contains app-specific dispatch callables for AppIngressRunner.
"""
from __future__ import annotations

from apps_rg.runtime.entry.dispatch import (
    apps_rg_parse,
    apps_rg_dispatch,
    APPS_RG_REQUIRED_FIELDS,
)

__all__ = [
    "apps_rg_parse",
    "apps_rg_dispatch",
    "APPS_RG_REQUIRED_FIELDS",
]
