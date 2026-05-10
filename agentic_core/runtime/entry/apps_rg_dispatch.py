"""apps_rg-specific dispatch/parse/required_fields callables for AppIngressRunner.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §5 (re-opens c8b3e1 W6/W7).

These three callables are the thin glue between AppIngressRunner's generic
ingress envelope flow and the apps_rg domain runtime. They are pure
functions — no provider calls, no LLM logic, no state writes.

W2 (this file) lands the callable shape and a STUB dispatcher that emits a
well-formed X3Disposition with exit_status='stub_pending_w3'. The real
U0 -> L1 -> L0 -> [C0] -> [PA] -> L2 -> Exit pipeline binding lands in W3.

This is the W4 governance pattern from c8b3e1 §4.1: apps_rg builds an
ingress payload; core dispatches it; apps_rg never plans/routes/executes.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
    RequestEnvelope,
)
from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import (
    AppsRgAuthorityViolation,
)
from agentic_core.runtime.contracts.x3_disposition import X3Disposition
from agentic_core.L1_cognition.apps_rg_l1_binding import l1_plan_apps_rg
from agentic_core.runtime.entry.u0_apps_rg_binding import (
    APPS_RG_TASK_CLASS,
    u0_validate_apps_rg,
)

# ---------------------------------------------------------------------------
# Required fields — the payload keys that MUST be present and non-empty
# for AppIngressRunner to dispatch the request without surfacing a
# ClarificationRequired. Per c8b3e1 §4.1, target_company OR target_role
# AND a resume source are the minimum. AppIngressRunner only validates
# string-non-empty; we relax the OR-rules in parse() below.
# ---------------------------------------------------------------------------
APPS_RG_REQUIRED_FIELDS: tuple[str, ...] = (
    "target_company",
    "target_role",
)


# ---------------------------------------------------------------------------
# parse() — convert the normalized payload dict into a typed RequestEnvelope.
# Returns None to surface ClarificationRequired when payload cannot be parsed.
# ---------------------------------------------------------------------------
def apps_rg_parse(payload: Mapping[str, Any]) -> RequestEnvelope | None:
    """Build RequestEnvelope from a normalized payload dict.

    Returns None when:
      - payload is missing both target_company and target_role
      - payload is missing both source_resume_ref and source_resume_text
      - dataclass construction fails (validation error in __post_init__)
    """
    if not isinstance(payload, dict):
        return None

    target_company = payload.get("target_company") or None
    target_role = payload.get("target_role") or None
    source_resume_ref = payload.get("source_resume_ref") or None
    source_resume_text = payload.get("source_resume_text") or None

    # Per AppsRgIngressPayload.__post_init__ invariant:
    #   at least one of (target_company, target_role) or (source_resume_ref, source_resume_text)
    if not (target_company or target_role):
        if not (source_resume_ref or source_resume_text):
            return None

    try:
        ingress = AppsRgIngressPayload(
            target_company=target_company,
            target_role=target_role,
            target_level=payload.get("target_level"),
            source_resume_ref=source_resume_ref,
            source_resume_text=source_resume_text,
            job_description_ref=payload.get("job_description_ref"),
            job_description_text=payload.get("job_description_text"),
            candidate_profile_path=payload.get("candidate_profile_path"),
            manual_brief_path=payload.get("manual_brief_path"),
            auto_research_internal=bool(payload.get("auto_research_internal", False)),
            auto_research_tavily=bool(payload.get("auto_research_tavily", False)),
            research_via=payload.get("research_via"),
            user_constraints=payload.get("user_constraints", {}) or {},
            output_preferences=payload.get("output_preferences", {}) or {},
            idempotency_key=payload.get("idempotency_key"),
        )
    except (TypeError, ValueError):
        return None

    return RequestEnvelope(
        payload=ingress,
        request_id=payload.get("request_id") or f"rg-req-{uuid4().hex[:12]}",
        run_id=payload.get("run_id") or f"rg-run-{uuid4().hex[:12]}",
        trace_id=payload.get("trace_id") or f"rg-trace-{uuid4().hex[:16]}",
        submitted_at=datetime.now(timezone.utc).isoformat(),
    )


# ---------------------------------------------------------------------------
# dispatch() — invoke the apps_rg pipeline with the parsed RequestEnvelope.
# Returns an X3Disposition.
#
# W2 STUB: returns exit_status='stub_pending_w3' to prove the pipeline
# is reachable end-to-end. W3 replaces this with the real U0 -> L1 -> L0 ->
# [C0] -> [PA] -> L2 -> Exit chain via per-layer bindings.
# ---------------------------------------------------------------------------
def apps_rg_dispatch(envelope: RequestEnvelope) -> X3Disposition:
    """Dispatch the apps_rg request through the core runtime pipeline.

    Pipeline progress (per plan apps-rg-runtime-wiring-completion-d4e8a1 §6):
        ✅ W3.P1 — U0 ingress validator         (real)
        ✅ W3.P2 — L1 plan contract              (real)
        ⏸️ W3.P3 — L0 route contract             (next turn)
        ⏸️ W3.P4 — [C0] / [PA] conditional emit (next turn)
        ⏸️ W3.P5 — L2 execution + Exit          (next turn)

    Each landed stage replaces a 'pending' marker in the disposition until
    the entire chain is real and exit_status='success'.
    """
    if not isinstance(envelope, RequestEnvelope):
        # Defensive: wrong shape from parse() — surface as error disposition
        return X3Disposition(
            request_id="unknown",
            run_id="unknown",
            app_id="apps_rg",
            trace_id="unknown",
            exit_status="error",
            outcome_authorized=False,
            final_output={"error": "apps_rg_dispatch received non-RequestEnvelope"},
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
        )

    # ----------------------------------------------------------------- U0
    try:
        validated_request = u0_validate_apps_rg(envelope)
    except AppsRgAuthorityViolation as violation:
        return X3Disposition(
            request_id=envelope.request_id,
            run_id=envelope.run_id,
            app_id="apps_rg",
            trace_id=envelope.trace_id,
            exit_status="failure",
            outcome_authorized=False,
            final_output={
                "stage": "U0",
                "rejection_reason": "authority_violation",
                "detail": str(violation),
            },
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            disposition_version="W3.P1",
        )

    # ----------------------------------------------------------------- L1
    try:
        l1_plan = l1_plan_apps_rg(validated_request)
    except (TypeError, ValueError) as l1_err:
        return X3Disposition(
            request_id=validated_request.request_id,
            run_id=validated_request.run_id,
            app_id="apps_rg",
            trace_id=validated_request.trace_id,
            exit_status="failure",
            outcome_authorized=False,
            final_output={
                "stage": "L1",
                "rejection_reason": "l1_planning_error",
                "detail": str(l1_err),
            },
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            disposition_version="W3.P2",
        )

    # U0 + L1 passed — L0 routing pending.
    return X3Disposition(
        request_id=l1_plan.request_id,
        run_id=l1_plan.run_id,
        app_id="apps_rg",
        trace_id=l1_plan.trace_id,
        exit_status="stub_pending_w3p3",
        outcome_authorized=False,
        final_output={
            "stage": "U0_L1_PASSED_L0_PENDING",
            "task_class": validated_request.task_class,
            "payload_digest": validated_request.payload_digest,
            "u0_receipt": {
                "allowed": validated_request.authority_validation_receipt.allowed,
                "checked_fields_count": len(
                    validated_request.authority_validation_receipt.checked_fields
                ),
                "forbidden_fields_detected": list(
                    validated_request.authority_validation_receipt.forbidden_fields_detected
                ),
                "policy_version": validated_request.authority_validation_receipt.policy_version,
            },
            "l1_plan": {
                "task_plan": list(l1_plan.task_plan),
                "required_capabilities": list(l1_plan.required_capabilities),
                "grounding_required": l1_plan.grounding_required,
                "model_generation_required": l1_plan.model_generation_required,
                "write_authority_present": l1_plan.write_authority_present,
                "profile_manifest_digest": l1_plan.profile_manifest_digest,
                "plan_version": l1_plan.plan_version,
            },
            "next_stage_pending": (
                "L0 route contract for capabilities="
                f"{list(l1_plan.required_capabilities)}. "
                "Follow-up turn lands W3.P3 — agentic_core/L0_routing/apps_rg_l0_binding.py."
            ),
            "echoed_target_company": envelope.payload.target_company,
            "echoed_target_role": envelope.payload.target_role,
        },
        exit_timestamp=datetime.now(timezone.utc).isoformat(),
        disposition_version="W3.P2",
    )


__all__ = [
    "APPS_RG_REQUIRED_FIELDS",
    "apps_rg_parse",
    "apps_rg_dispatch",
]
