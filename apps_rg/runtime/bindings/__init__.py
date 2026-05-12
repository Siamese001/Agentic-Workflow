"""apps_rg runtime bindings package.

Contains layer bindings (U0, L1, L0, C0, PA, L2, Exit) for the apps_rg
resume_generation pipeline. These bindings are pure functions that
consume typed contracts from upstream layers and emit contracts for
downstream consumption.

Per plan apps-rg-golden-state-section-generation-a4f9e1 W2A.
"""
from __future__ import annotations

# U0 binding — migrated from agentic_core/runtime/entry/u0_apps_rg_binding.py
from apps_rg.runtime.bindings.u0_binding import (
    APPS_RG_TASK_CLASS,
    APPS_RG_U0_CERT_REF,
    u0_validate_apps_rg,
)

# L1 binding — migrated from agentic_core/L1_cognition/apps_rg_l1_binding.py
from apps_rg.runtime.bindings.l1_binding import (
    APPS_RG_L1_CERT_REF,
    l1_plan_apps_rg,
)

# L0 binding — migrated from agentic_core/L0_routing/apps_rg_l0_binding.py
from apps_rg.runtime.bindings.l0_binding import (
    APPS_RG_L0_CERT_REF,
    APPS_RG_ROUTE_FAMILY,
    APPS_RG_ROUTE_ID,
    APPS_RG_CACHE_ELIGIBILITY,
    APPS_RG_HITL_POSTURE,
    APPS_RG_FALLBACK_ROUTE_ID,
    l0_route_apps_rg,
)

# C0 binding — migrated from agentic_core/runtime/c0/apps_rg_c0_binding.py
from apps_rg.runtime.bindings.c0_binding import (
    APPS_RG_C0_CERT_REF,
    c0_retrieve_apps_rg,
)

# PA binding — migrated from agentic_core/prompt_governance/apps_rg_pa_binding.py
from apps_rg.runtime.bindings.pa_binding import (
    APPS_RG_PA_CERT_REF,
    APPS_RG_TARGET_MODEL,
    APPS_RG_TARGET_PROVIDER,
    pa_compose_apps_rg,
)

# L2 binding — migrated from agentic_core/L2_execution/apps_rg_l2_binding.py
from apps_rg.runtime.bindings.l2_binding import (
    APPS_RG_L2_CERT_REF,
    AppsRGQualityGatePolicy,
    extract_apps_rg_quality_gate_policy,
    evaluate_apps_rg_l2_quality_precheck,
    l2_execute_apps_rg,
)

# Exit binding — migrated from agentic_core/runtime/exit/apps_rg_exit_binding.py
from apps_rg.runtime.bindings.exit_binding import (
    APPS_RG_EXIT_CERT_REF,
    ExitBindingResult,
    build_apps_rg_exit_harness,
    exit_finalize_apps_rg,
    extract_apps_rg_exit_gate_policy,
)

__all__ = [
    # U0 exports
    "APPS_RG_TASK_CLASS",
    "APPS_RG_U0_CERT_REF",
    "u0_validate_apps_rg",
    # L1 exports
    "APPS_RG_L1_CERT_REF",
    "l1_plan_apps_rg",
    # L0 exports
    "APPS_RG_L0_CERT_REF",
    "APPS_RG_ROUTE_FAMILY",
    "APPS_RG_ROUTE_ID",
    "APPS_RG_CACHE_ELIGIBILITY",
    "APPS_RG_HITL_POSTURE",
    "APPS_RG_FALLBACK_ROUTE_ID",
    "l0_route_apps_rg",
    # C0 exports
    "APPS_RG_C0_CERT_REF",
    "c0_retrieve_apps_rg",
    # PA exports
    "APPS_RG_PA_CERT_REF",
    "APPS_RG_TARGET_MODEL",
    "APPS_RG_TARGET_PROVIDER",
    "pa_compose_apps_rg",
    # L2 exports
    "APPS_RG_L2_CERT_REF",
    "AppsRGQualityGatePolicy",
    "extract_apps_rg_quality_gate_policy",
    "evaluate_apps_rg_l2_quality_precheck",
    "l2_execute_apps_rg",
    # Exit exports
    "APPS_RG_EXIT_CERT_REF",
    "ExitBindingResult",
    "build_apps_rg_exit_harness",
    "exit_finalize_apps_rg",
    "extract_apps_rg_exit_gate_policy",
]
