"""apps_underwriting_ai runtime bindings package.

Contains layer bindings (U0, L1, L0, C0, PA, L2, Exit) for the
underwriting_decision pipeline. These bindings are pure functions (or
thin deterministic adapters) that consume typed contracts from upstream
layers and emit contracts for downstream consumption.

Plan: apps-underwriting-ai-profile-migration (Bundle B).
"""
from __future__ import annotations

from apps_underwriting_ai.runtime.bindings.u0_binding import (
    TASK_CLASS,
    APP_ID,
    U0_CERT_REF,
    u0_validate_underwriting,
)

from apps_underwriting_ai.runtime.bindings.l1_binding import (
    UW_L1_CERT_REF,
    UWL1Plan,
    l1_plan_underwriting,
)

from apps_underwriting_ai.runtime.bindings.l0_binding import (
    UW_L0_CERT_REF,
    UW_ROUTE_ID,
    UW_ROUTE_FAMILY,
    UWRoute,
    l0_route_underwriting,
)

from apps_underwriting_ai.runtime.bindings.c0_binding import (
    UW_C0_CERT_REF,
    UWC0PipelineError,
    UWEvidenceResult,
    c0_run_underwriting,
)

from apps_underwriting_ai.runtime.bindings.pa_binding import (
    UW_PA_CERT_REF,
    UW_PA_TARGET_MODEL,
    UW_PA_TARGET_PROVIDER,
    pa_compose_underwriting,
    pa_compose_underwriting_profile,
)

from apps_underwriting_ai.runtime.bindings.l2_binding import (
    UW_L2_CERT_REF,
    UWSealedArtifact,
    l2_execute_underwriting,
)

from apps_underwriting_ai.runtime.bindings.exit_binding import (
    UW_EXIT_CERT_REF,
    UWExitResult,
    exit_finalize_underwriting,
)

__all__ = [
    "TASK_CLASS",
    "APP_ID",
    "U0_CERT_REF",
    "u0_validate_underwriting",
    "UW_L1_CERT_REF",
    "UWL1Plan",
    "l1_plan_underwriting",
    "UW_L0_CERT_REF",
    "UW_ROUTE_ID",
    "UW_ROUTE_FAMILY",
    "UWRoute",
    "l0_route_underwriting",
    "UW_C0_CERT_REF",
    "UWC0PipelineError",
    "UWEvidenceResult",
    "c0_run_underwriting",
    "UW_PA_CERT_REF",
    "UW_PA_TARGET_MODEL",
    "UW_PA_TARGET_PROVIDER",
    "pa_compose_underwriting",
    "pa_compose_underwriting_profile",
    "UW_L2_CERT_REF",
    "UWSealedArtifact",
    "l2_execute_underwriting",
    "UW_EXIT_CERT_REF",
    "UWExitResult",
    "exit_finalize_underwriting",
]
