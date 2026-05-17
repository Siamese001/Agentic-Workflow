"""Thin import surface — canonical L2 binding lives in ``l2_binding_adapter``."""

from __future__ import annotations

from apps_rg.runtime.bindings.l2_binding_adapter import (
    APPS_RG_L2_CERT_REF,
    AppsRGQualityGatePolicy,
    evaluate_apps_rg_l2_quality_precheck,
    extract_apps_rg_quality_gate_policy,
    l2_execute_apps_rg,
    _use_v4_l2_envelope,
)

__all__ = [
    "APPS_RG_L2_CERT_REF",
    "AppsRGQualityGatePolicy",
    "evaluate_apps_rg_l2_quality_precheck",
    "extract_apps_rg_quality_gate_policy",
    "l2_execute_apps_rg",
    "_use_v4_l2_envelope",
]
