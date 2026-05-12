"""U0 ingress validator binding for the apps_rg `resume_generation` task class.

LEGACY_SHIM — Migrated to apps_rg/runtime/bindings/u0_binding.py
Per plan apps-rg-golden-state-section-generation-a4f9e1 W2A.

This shim re-exports from the new app-owned location for backward
compatibility during the W2 migration phase. Import from the new
location directly: apps_rg.runtime.bindings.u0_binding
"""
from __future__ import annotations

# Re-export from the new app-owned location
from apps_rg.runtime.bindings.u0_binding import (
    APPS_RG_TASK_CLASS,
    APPS_RG_U0_CERT_REF,
    u0_validate_apps_rg,
)

__all__ = [
    "APPS_RG_TASK_CLASS",
    "APPS_RG_U0_CERT_REF",
    "u0_validate_apps_rg",
]
