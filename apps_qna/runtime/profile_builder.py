"""apps_qna profile builder — W1 one-spine migration canonical form.

Builds AppRuntimeProfile for apps_qna with all 7 real stage binding refs.
AppIngressRunner(profile=profile).run(payload) sequences those refs directly;
no app-owned dispatch callable.

Stage bindings are in apps_qna/runtime/bindings/:
    u0  → qna_u0   (envelope → ValidatedRequest via u0_intake)
    l1  → qna_l1   (ValidatedRequest → L1PlanContract via l1_planner)
    l0  → qna_l0   (L1PlanContract → QnaRouteContract via l0_router)
    c0  → qna_c0   (route+validated → FinalEvidenceContract dict via c0_adapter)
    pa  → qna_pa   (route+l1+fec+validated → QnaPromptArtifact via pa_adapter)
    l2  → qna_l2   (QnaPromptArtifact → SealedQnaArtifact via E1/E2/E3)
    exit → qna_exit (SealedQnaArtifact → QnaExitResult via exit_wiring)

Plan: docs/archive/windsurf/legacy-tree/plans/one-spine-qna-rfp-migration-d2e8f1.md W1.P2
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

APPS_QNA_REQUIRED_FIELDS: tuple[str, ...] = (
    "interview_slug",
)


def parse_payload(payload: Mapping[str, Any]) -> RequestEnvelope | None:
    """Convert a normalized payload dict into a typed RequestEnvelope for apps_qna.

    Signature matches AppRuntimeProfile.parse:
        (payload: Mapping[str, Any]) -> RequestEnvelope | None
    Returns None when payload cannot be parsed (surfaces ClarificationRequired).
    """
    if not isinstance(payload, dict):
        return None

    interview_slug = payload.get("interview_slug") or None
    target_role = payload.get("target_role") or None

    if not interview_slug and not target_role:
        return None

    user_constraints: dict[str, Any] = dict(payload.get("user_constraints") or {})
    if interview_slug:
        user_constraints["interview_slug"] = interview_slug

    try:
        ingress = AppsRgIngressPayload(
            app_id="apps_qna",
            task_class="card_pack_build",
            target_company=payload.get("target_company") or None,
            target_role=target_role or interview_slug,
            target_level=payload.get("target_level") or None,
            manual_brief_path=payload.get("manual_brief_path") or payload.get("briefing_artifact_ref") or None,
            user_constraints=user_constraints,
            output_preferences=payload.get("output_preferences") or {},
            idempotency_key=payload.get("idempotency_key"),
        )
    except (TypeError, ValueError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return None

    return RequestEnvelope(
        payload=ingress,
        request_id=payload.get("request_id") or f"qna-req-{uuid4().hex[:12]}",
        run_id=payload.get("run_id") or f"qna-run-{uuid4().hex[:12]}",
        tenant_id=payload.get("tenant_id") or "apps_qna",
        trace_id=payload.get("trace_id") or f"qna-trace-{uuid4().hex[:16]}",
        submitted_at=datetime.now(timezone.utc).isoformat(),
    )


def build_app_runtime_contract() -> AppRuntimeProfile:
    """Construct and return the canonical AppRuntimeProfile for apps_qna.

    All 7 stage bindings are wired to real apps_qna binding functions.
    AppIngressRunner sequences stages directly; no app-owned dispatch callable.

    Returns
    -------
    AppRuntimeProfile
        Ready to pass as AppIngressRunner(profile=profile).run(payload).
    """
    from apps_qna.runtime.bindings.u0_binding import qna_u0
    from apps_qna.runtime.bindings.l1_binding import qna_l1
    from apps_qna.runtime.bindings.l0_binding import qna_l0
    from apps_qna.runtime.bindings.c0_binding import qna_c0
    from apps_qna.runtime.bindings.pa_binding import qna_pa
    from apps_qna.runtime.bindings.l2_binding import qna_l2
    from apps_qna.runtime.bindings.exit_binding import qna_exit

    return AppRuntimeProfile(
        app_id="apps_qna",
        required_fields=APPS_QNA_REQUIRED_FIELDS,
        parse=parse_payload,
        u0=qna_u0,
        l1=qna_l1,
        l0=qna_l0,
        c0=qna_c0,
        pa=qna_pa,
        l2=qna_l2,
        exit=qna_exit,
        profile_version="2",
    )


__all__ = [
    "build_app_runtime_contract",
    "parse_payload",
    "APPS_QNA_REQUIRED_FIELDS",
]
