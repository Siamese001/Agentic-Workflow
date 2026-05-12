"""LEGACY_SHIM — MIGRATED to apps_rg/runtime/bindings/l2_binding.py

Per plan apps-rg-golden-state-section-generation-a4f9e1 W2E.

This shim re-exports from the new canonical location.
It is a TEMPORARY compatibility shim for existing callers.
Do not modify; the canonical implementation lives in apps_rg.
"""
from __future__ import annotations

# Re-export all public API from the migrated location
from apps_rg.runtime.bindings.l2_binding import (
    APPS_RG_L2_CERT_REF,
    AppsRGQualityGatePolicy,
    extract_apps_rg_quality_gate_policy,
    evaluate_apps_rg_l2_quality_precheck,
    l2_execute_apps_rg,
)

__all__ = [
    "APPS_RG_L2_CERT_REF",
    "AppsRGQualityGatePolicy",
    "extract_apps_rg_quality_gate_policy",
    "evaluate_apps_rg_l2_quality_precheck",
    "l2_execute_apps_rg",
]
