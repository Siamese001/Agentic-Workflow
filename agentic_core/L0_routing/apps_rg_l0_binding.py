"""L0 routing binding for the apps_rg `resume_generation` task class.

LEGACY_SHIM — Migrated to apps_rg/runtime/bindings/l0_binding.py
Per plan apps-rg-golden-state-section-generation-a4f9e1 W2B.

This shim re-exports from the new app-owned location for backward
compatibility during the W2 migration phase. Import from the new
location directly: apps_rg.runtime.bindings.l0_binding
"""
from __future__ import annotations

# Re-export from the new app-owned location
from apps_rg.runtime.bindings.l0_binding import (
    APPS_RG_L0_CERT_REF,
    APPS_RG_ROUTE_FAMILY,
    APPS_RG_ROUTE_ID,
    APPS_RG_CACHE_ELIGIBILITY,
    APPS_RG_HITL_POSTURE,
    APPS_RG_FALLBACK_ROUTE_ID,
    l0_route_apps_rg,
)

__all__ = [
    "APPS_RG_L0_CERT_REF",
    "APPS_RG_ROUTE_FAMILY",
    "APPS_RG_ROUTE_ID",
    "APPS_RG_CACHE_ELIGIBILITY",
    "APPS_RG_HITL_POSTURE",
    "APPS_RG_FALLBACK_ROUTE_ID",
    "l0_route_apps_rg",
]
