"""apps_rg runtime dispatch — canonical parse/dispatch package surface.

Re-exports the app-owned entry helpers from ``apps_rg_dispatch`` so callers
can use ``from apps_rg.runtime.dispatch import apps_rg_parse`` (CI gates,
U0 reflection harness, contract tests) without reaching into the submodule.
"""

from __future__ import annotations

from apps_rg.runtime.dispatch.apps_rg_dispatch import (
    APPS_RG_REQUIRED_FIELDS,
    apps_rg_dispatch,
    apps_rg_parse,
)

__all__ = ["APPS_RG_REQUIRED_FIELDS", "apps_rg_dispatch", "apps_rg_parse"]
