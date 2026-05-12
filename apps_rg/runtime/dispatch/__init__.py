"""apps_rg runtime dispatch package.

Contains the dispatch, parse, and required_fields callables for the
AppIngressRunner to integrate apps_rg with the generic agentic_core runtime.

Per plan apps-rg-golden-state-section-generation-a4f9e1 W2G.
"""
from __future__ import annotations

from apps_rg.runtime.dispatch.apps_rg_dispatch import (
    APPS_RG_REQUIRED_FIELDS,
    apps_rg_dispatch,
    apps_rg_parse,
)

__all__ = [
    "APPS_RG_REQUIRED_FIELDS",
    "apps_rg_dispatch",
    "apps_rg_parse",
]
