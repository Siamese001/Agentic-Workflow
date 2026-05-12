"""apps_research-specific dispatch/parse/required_fields callables for AppIngressRunner.

Per plan apps-research-golden-template-adoption-ag9.

Thin glue between AppIngressRunner's generic ingress envelope flow and the
generic agentic_core spine. Pure functions — no provider calls, no LLM
logic, no state writes, no app-specific policy decisions.

Pipeline: U0 → L1 → L0 → C0 (grounding) → PA → L2 → Exit
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
    RequestEnvelope,
)
from agentic_core.runtime.contracts.x3_disposition import X3Disposition
from agentic_core.L0_routing.apps_research_l0_binding import l0_route_apps_research
from agentic_core.L1_cognition.apps_research_l1_binding import l1_plan_apps_research
from agentic_core.L2_execution.apps_research_l2_binding import l2_execute_apps_research
from agentic_core.prompt_governance.apps_research_pa_binding import (
    pa_compose_apps_research,
)
from agentic_core.runtime.c0.apps_research_c0_binding import c0_retrieve_apps_research
from agentic_core.runtime.entry.u0_runtime_package_binding import (
    u0_resolve_runtime_package,
    U0PackageValidationError,
    RuntimePackageRegistry,
)
from agentic_core.runtime.contracts.runtime_customization_package import (
    RuntimeCustomizationPackage,
    UnknownPackageFieldError,
    PackageDigestMismatchError,
)
from agentic_core.runtime.exit.apps_research_exit_binding import (
    exit_finalize_apps_research,
)

APPS_RESEARCH_REQUIRED_FIELDS: tuple[str, ...] = (
    "target_company",
)



def apps_research_parse(payload: Mapping[str, Any]) -> RequestEnvelope | None:
    """Build RequestEnvelope from a normalized payload dict for apps_research.

    Returns None when target_company is missing or construction fails.
    """
    if not isinstance(payload, dict):
        return None

    target_company = payload.get("target_company") or None
    # topic may substitute for target_company
    topic = (payload.get("topic") or
             (payload.get("user_constraints") or {}).get("topic") or
             None)

    if not target_company and not topic:
        return None

    # Build a minimal AppsRgIngressPayload (reused for apps_research ingress path)
    user_constraints: dict[str, Any] = dict(payload.get("user_constraints") or {})
    if "topic" in payload:
        user_constraints["topic"] = payload["topic"]
    if "depth" in payload:
        user_constraints["depth"] = payload["depth"]

    try:
        ingress = AppsRgIngressPayload(
            app_id="apps_research",
            task_class=APPS_RESEARCH_TASK_CLASS,
            target_company=target_company or topic,
            target_role=payload.get("target_role") or None,
            target_level=payload.get("target_level") or None,
            manual_brief_path=payload.get("manual_brief_path") or None,
            user_constraints=user_constraints,
            output_preferences=payload.get("output_preferences") or {},
            idempotency_key=payload.get("idempotency_key"),
        )
    except (TypeError, ValueError):
        return None

    return RequestEnvelope(
        payload=ingress,
        request_id=payload.get("request_id") or f"research-req-{uuid4().hex[:12]}",
        run_id=payload.get("run_id") or f"research-run-{uuid4().hex[:12]}",
        tenant_id=payload.get("tenant_id") or "apps_research",
        trace_id=payload.get("trace_id") or f"research-trace-{uuid4().hex[:16]}",
        submitted_at=datetime.now(timezone.utc).isoformat(),
    )


def apps_research_dispatch(envelope: RequestEnvelope) -> X3Disposition:
    """Dispatch the apps_research request through the core runtime pipeline.

    Pipeline:
        U0 → L1 → L0 → C0 (grounding) → PA → L2 → Exit

    Returns X3Disposition on all paths (success or failure).
    """
    if not isinstance(envelope, RequestEnvelope):
        return X3Disposition(
            request_id="unknown",
            run_id="unknown",
            app_id="apps_research",
            trace_id="unknown",
            exit_status="error",
            outcome_authorized=False,
            final_output={"error": "apps_research_dispatch received non-RequestEnvelope"},
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            l5_certification_ref="dispatch-error-bad-envelope",
        )

    # ----------------------------------------------------------------- U0
    # Generic U0 runtime package resolution (app-agnostic)
    # Resolves package from app-owned registry or explicit input
    registry = RuntimePackageRegistry()
    try:
        validated_request, pkg_receipt, auto_inject_ctx = u0_resolve_runtime_package(
            envelope, registry=registry
        )
    except (U0PackageValidationError, UnknownPackageFieldError, PackageDigestMismatchError) as u0_err:
        return X3Disposition(
            request_id=envelope.request_id,
            run_id=envelope.run_id,
            app_id="apps_research",
            trace_id=envelope.trace_id,
            exit_status="failure",
            outcome_authorized=False,
            final_output={
                "stage": "U0",
                "rejection_reason": "runtime_package_validation_error",
                "detail": str(u0_err),
                "package_receipt": getattr(u0_err, 'receipt', None),
            },
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            l5_certification_ref="dispatch-error-u0-runtime-package-validation",
        )

    # ----------------------------------------------------------------- L1
    # Generic L1 planning hints from app-owned package refs (NO runtime authority)
    try:
        l1_plan = l1_plan_apps_research(validated_request)
    except (TypeError, ValueError) as l1_err:
        return X3Disposition(
            request_id=validated_request.request_id,
            run_id=validated_request.run_id,
            app_id="apps_research",
            trace_id=validated_request.trace_id,
            tenant_id=validated_request.tenant_id,
            exit_status="failure",
            outcome_authorized=False,
            final_output={
                "stage": "L1",
                "rejection_reason": "l1_planning_error",
                "detail": str(l1_err),
            },
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            l5_certification_ref="dispatch-error-l1-planning",
        )

    # ----------------------------------------------------------------- L0
    try:
        route = l0_route_apps_research(l1_plan)
    except (TypeError, ValueError) as l0_err:
        return X3Disposition(
            request_id=l1_plan.request_id,
            run_id=l1_plan.run_id,
            app_id="apps_research",
            trace_id=l1_plan.trace_id,
            tenant_id=l1_plan.tenant_id,
            exit_status="failure",
            outcome_authorized=False,
            final_output={
                "stage": "L0",
                "rejection_reason": "l0_routing_error",
                "detail": str(l0_err),
            },
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            l5_certification_ref="dispatch-error-l0-routing",
        )

    # ----------------------------------------------------------------- C0
    try:
        fec = c0_retrieve_apps_research(route, validated_request)
    except (TypeError, ValueError, OSError) as c0_err:
        return X3Disposition(
            request_id=route.request_id,
            run_id=route.run_id,
            app_id="apps_research",
            trace_id=route.trace_id,
            tenant_id=route.tenant_id,
            exit_status="failure",
            outcome_authorized=False,
            final_output={
                "stage": "C0",
                "rejection_reason": "c0_retrieval_error",
                "detail": str(c0_err),
            },
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            l5_certification_ref="dispatch-error-c0-retrieval",
        )

    # ----------------------------------------------------------------- PA
    try:
        prompt_artifact = pa_compose_apps_research(
            route, l1_plan, fec, validated_request
        )
    except (TypeError, ValueError) as pa_err:
        return X3Disposition(
            request_id=route.request_id,
            run_id=route.run_id,
            app_id="apps_research",
            trace_id=route.trace_id,
            tenant_id=route.tenant_id,
            exit_status="failure",
            outcome_authorized=False,
            final_output={
                "stage": "PA",
                "rejection_reason": "pa_assembly_error",
                "detail": str(pa_err),
            },
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            l5_certification_ref="dispatch-error-pa-assembly",
        )

    # ----------------------------------------------------------------- L2
    try:
        sealed = l2_execute_apps_research(prompt_artifact)
    except (TypeError, ValueError) as l2_err:
        return X3Disposition(
            request_id=route.request_id,
            run_id=route.run_id,
            app_id="apps_research",
            trace_id=route.trace_id,
            tenant_id=route.tenant_id,
            exit_status="failure",
            outcome_authorized=False,
            final_output={
                "stage": "L2",
                "rejection_reason": "l2_execution_error",
                "detail": str(l2_err),
            },
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            l5_certification_ref="dispatch-error-l2-execution",
        )

    # ----------------------------------------------------------------- Exit
    try:
        disposition = exit_finalize_apps_research(sealed, prompt_artifact)
        return disposition
    except (TypeError, ValueError, OSError) as exit_err:
        return X3Disposition(
            request_id=route.request_id,
            run_id=route.run_id,
            app_id="apps_research",
            trace_id=route.trace_id,
            tenant_id=route.tenant_id,
            exit_status="failure",
            outcome_authorized=False,
            final_output={
                "stage": "EXIT",
                "rejection_reason": "exit_finalization_error",
                "detail": str(exit_err),
                "sealed_compilation_hash": sealed.compilation_hash,
            },
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            l5_certification_ref="dispatch-error-exit-finalization",
        )


__all__ = [
    "APPS_RESEARCH_REQUIRED_FIELDS",
    "apps_research_parse",
    "apps_research_dispatch",
]
