"""L1 cognition binding for the apps_rg `resume_generation` task class.

LEGACY_SHIM — Migrated to apps_rg/runtime/bindings/l1_binding.py
Per plan apps-rg-golden-state-section-generation-a4f9e1 W2A.

This shim re-exports from the new app-owned location for backward
compatibility during the W2 migration phase. Import from the new
location directly: apps_rg.runtime.bindings.l1_binding
"""
from __future__ import annotations

# Re-export from the new app-owned location
from apps_rg.runtime.bindings.l1_binding import (  # guardian: allow-layer-violation -- LEGACY_SHIM TEMPORARY_THIN_ADAPTER per apps-rg-golden-state-section-generation-a4f9e1 W2A
    APPS_RG_L1_CERT_REF,
    l1_plan_apps_rg,
)

__all__ = [
    "APPS_RG_L1_CERT_REF",
    "l1_plan_apps_rg",
]
