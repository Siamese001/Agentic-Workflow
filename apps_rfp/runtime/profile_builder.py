"""apps_rfp profile builder — W2 one-spine migration canonical form.

Builds AppRuntimeProfile for apps_rfp with all 7 real stage binding refs.
AppIngressRunner(profile=profile).run(payload) sequences those refs directly;
no app-owned dispatch callable.

Stage bindings are in apps_rfp/runtime/bindings/:
    u0   → rfp_u0   (envelope → ValidatedRequest via U0 intake)
    l1   → rfp_l1   (ValidatedRequest → L1PlanContract)
    l0   → rfp_l0   (L1PlanContract → RouteContract pointing at rfp_docs)
    c0   → rfp_c0   (route+validated → FinalEvidenceContract via rfp_docs retrieval)
    pa   → rfp_pa   (route+l1+fec+validated → RfpPromptArtifact)
    l2   → rfp_l2   (RfpPromptArtifact → SealedRfpArtifact via RfpOrchestrator [internal])
    exit → rfp_exit (SealedRfpArtifact → RfpExitResult with .disposition)

RfpOrchestrator and RfpHopOrchestrator are private implementation details of
rfp_l2 (Option A, W0 decision). They are NOT imported here or at module level
in any binding except l2_binding.py.

MIGRATION_DEFERRED: REMOVED — W2 complete (2026-05-14).
Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W2.P2
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
    RequestEnvelope,
)
from agentic_core.runtime.entry.app_ingress_runner import AppRuntimeProfile

APPS_RFP_REQUIRED_FIELDS: tuple[str, ...] = (
    "rfp_document_path",
)


def parse_payload(payload: Mapping[str, Any]) -> RequestEnvelope | None:
    """Convert a normalized payload dict into a typed RequestEnvelope for apps_rfp.

    Signature matches AppRuntimeProfile.parse:
        (payload: Mapping[str, Any]) -> RequestEnvelope | None
    Returns None when payload cannot be parsed (surfaces ClarificationRequired).
    """
    if not isinstance(payload, dict):
        return None

    rfp_document_path = payload.get("rfp_document_path") or None
    target_company = payload.get("target_company") or None

    if not rfp_document_path and not target_company:
        return None

    user_constraints: dict[str, Any] = dict(payload.get("user_constraints") or {})
    if rfp_document_path:
        user_constraints["rfp_document_path"] = rfp_document_path

    try:
        ingress = AppsRgIngressPayload(
            app_id="apps_rfp",
            task_class="proposal_assembly",
            target_company=target_company or None,
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
        request_id=payload.get("request_id") or f"rfp-req-{uuid4().hex[:12]}",
        run_id=payload.get("run_id") or f"rfp-run-{uuid4().hex[:12]}",
        tenant_id=payload.get("tenant_id") or "apps_rfp",
        trace_id=payload.get("trace_id") or f"rfp-trace-{uuid4().hex[:16]}",
        submitted_at=datetime.now(timezone.utc).isoformat(),
    )


def build_app_runtime_contract() -> AppRuntimeProfile:
    """Construct and return the canonical AppRuntimeProfile for apps_rfp.

    All 7 stage bindings are wired to real apps_rfp binding functions.
    AppIngressRunner sequences stages directly; no app-owned dispatch callable.
    RfpOrchestrator and RfpHopOrchestrator are private to the l2 binding —
    they are NOT imported here.

    Returns
    -------
    AppRuntimeProfile
        Ready to pass as AppIngressRunner(profile=profile).run(payload).
    """
    from apps_rfp.runtime.bindings.u0_binding import rfp_u0
    from apps_rfp.runtime.bindings.l1_binding import rfp_l1
    from apps_rfp.runtime.bindings.l0_binding import rfp_l0
    from apps_rfp.runtime.bindings.c0_binding import rfp_c0
    from apps_rfp.runtime.bindings.pa_binding import rfp_pa
    from apps_rfp.runtime.bindings.l2_binding import rfp_l2
    from apps_rfp.runtime.bindings.exit_binding import rfp_exit

    return AppRuntimeProfile(
        app_id="apps_rfp",
        required_fields=APPS_RFP_REQUIRED_FIELDS,
        parse=parse_payload,
        u0=rfp_u0,
        l1=rfp_l1,
        l0=rfp_l0,
        c0=rfp_c0,
        pa=rfp_pa,
        l2=rfp_l2,
        exit=rfp_exit,
        profile_version="2",
    )


__all__ = [
    "build_app_runtime_contract",
    "parse_payload",
    "APPS_RFP_REQUIRED_FIELDS",
]
