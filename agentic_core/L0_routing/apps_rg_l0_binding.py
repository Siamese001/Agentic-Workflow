"""L0 routing binding for the apps_rg `resume_generation` task class.

LEGACY_SHIM — Migrated to apps_rg/runtime/bindings/l0_binding.py
Per plan apps-rg-golden-state-section-generation-a4f9e1 W2B.

This shim re-exports from the new app-owned location for backward
compatibility during the W2 migration phase. Import from the new
location directly: apps_rg.runtime.bindings.l0_binding

p3.2: ``l0_route_apps_rg`` emits DeprecationWarning on each call — migrate
callers to ``apps_rg.runtime.bindings.l0_binding``.
"""
from __future__ import annotations

import warnings
from typing import Any

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from apps_rg.runtime.bindings import l0_binding as _l0_binding  # guardian: allow-layer-violation -- LEGACY_SHIM TEMPORARY_THIN_ADAPTER re-export per apps-rg-golden-state-section-generation-a4f9e1 W2B; canonical implementation in apps_rg.runtime.bindings.l0_binding

APPS_RG_L0_CERT_REF = _l0_binding.APPS_RG_L0_CERT_REF
APPS_RG_ROUTE_FAMILY = _l0_binding.APPS_RG_ROUTE_FAMILY
APPS_RG_ROUTE_ID = _l0_binding.APPS_RG_ROUTE_ID
APPS_RG_CACHE_ELIGIBILITY = _l0_binding.APPS_RG_CACHE_ELIGIBILITY
APPS_RG_HITL_POSTURE = _l0_binding.APPS_RG_HITL_POSTURE
APPS_RG_FALLBACK_ROUTE_ID = _l0_binding.APPS_RG_FALLBACK_ROUTE_ID
_MANAGED_ROUTE_TEST_FLAG = _l0_binding._MANAGED_ROUTE_TEST_FLAG


def l0_route_apps_rg(plan: L1PlanContract) -> RouteContract:
    warnings.warn(
        "agentic_core.L0_routing.apps_rg_l0_binding.l0_route_apps_rg is deprecated — "
        "import apps_rg.runtime.bindings.l0_binding.l0_route_apps_rg instead (p3.2).",
        DeprecationWarning,
        stacklevel=2,
    )
    return _l0_binding.l0_route_apps_rg(plan)


__all__ = [
    "APPS_RG_L0_CERT_REF",
    "APPS_RG_ROUTE_FAMILY",
    "APPS_RG_ROUTE_ID",
    "APPS_RG_CACHE_ELIGIBILITY",
    "APPS_RG_HITL_POSTURE",
    "APPS_RG_FALLBACK_ROUTE_ID",
    "_MANAGED_ROUTE_TEST_FLAG",
    "l0_route_apps_rg",
]
