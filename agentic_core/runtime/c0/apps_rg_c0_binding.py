"""C0 grounding-retrieval binding for apps_rg `resume_generation` task class.

LEGACY_SHIM — Migrated to apps_rg/runtime/bindings/c0_binding.py
Per plan apps-rg-golden-state-section-generation-a4f9e1 W2C.

This shim re-exports from the new app-owned location for backward
compatibility during the W2 migration phase. Import from the new
location directly: apps_rg.runtime.bindings.c0_binding
"""
from __future__ import annotations

# Re-export from the new app-owned location
from apps_rg.runtime.bindings.c0_binding import (  # guardian: allow-layer-violation -- LEGACY_SHIM TEMPORARY_THIN_ADAPTER per apps-rg-golden-state-section-generation-a4f9e1 W2C
    APPS_RG_C0_CERT_REF,
    c0_retrieve_apps_rg,
)

__all__ = [
    "APPS_RG_C0_CERT_REF",
    "c0_retrieve_apps_rg",
]
