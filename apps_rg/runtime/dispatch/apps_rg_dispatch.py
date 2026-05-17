"""apps_rg runtime dispatch — payload parsing and dispatch helpers.

`apps_rg_parse` converts a raw dict payload into an `agentic_core`
`RequestEnvelope`. `apps_rg_dispatch` runs the full pipeline from a
parsed envelope and returns the run result dict.

These helpers are the thin app-side counterparts to
`agentic_core.runtime.entry.apps_rg_dispatch`.
"""
from __future__ import annotations

import dataclasses
from types import SimpleNamespace
from typing import Any

from agentic_core.runtime.contracts.apps_rg_ingress_payload import AppsRgIngressPayload

from apps_rg.runtime.resume_resolution import (
    ResumeResolutionError,
    resolve_resume_for_lanes,
    u0_inline_text_from_payload,
)

# Minimum keys for a well-formed apps_rg thin payload (parse + U0 reflection gates).
APPS_RG_REQUIRED_FIELDS: tuple[str, ...] = ("target_company", "target_role")

__all__ = [
    "APPS_RG_REQUIRED_FIELDS",
    "apps_rg_dispatch",
    "apps_rg_parse",
    "enrich_ingress_resume_inline_text",
]


def enrich_ingress_resume_inline_text(payload: AppsRgIngressPayload) -> AppsRgIngressPayload:
    """When ``source_resume_text`` is empty, resolve resume SSOT and set canonical inline text.

    U0 remains file-I/O-free: enrichment happens in apps_rg ingress only.
    """
    if str(payload.source_resume_text or "").strip():
        return payload
    try:
        rr = resolve_resume_for_lanes(
            source_resume_text=None,
            source_resume_ref=payload.source_resume_ref,
            require_run_specific=False,
            require_json_document=True,
        )
    except ResumeResolutionError:
        return payload
    canonical = u0_inline_text_from_payload(rr.resume_payload)
    return dataclasses.replace(payload, source_resume_text=canonical)


def _as_dispatch_view(raw: dict[str, Any]) -> SimpleNamespace:
    """Normalize dict returns so callers can use ``result.exit_status``."""
    view = dict(raw)
    if "outcome_authorized" not in view:
        view["outcome_authorized"] = view.get("exit_status") == "success"
    return SimpleNamespace(**view)


def apps_rg_parse(payload: dict[str, Any]) -> Any:
    """Parse a raw apps_rg payload dict into a RequestEnvelope.

    Parameters
    ----------
    payload:
        Raw dict with at minimum app_id, task_class, target_company, and
        target_role keys.

    Returns
    -------
    RequestEnvelope
        A validated `agentic_core` RequestEnvelope ready for U0 validation.
    """
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import RequestEnvelope

    app_id = str(payload.get("app_id", "apps_rg"))
    task_class = str(payload.get("task_class", "resume_generation"))
    user_constraints = dict(payload.get("user_constraints") or {})
    if "generation_mode" in payload:
        user_constraints["_generation_mode"] = str(payload["generation_mode"])

    bar = (payload.get("briefing_artifact_ref") or payload.get("manual_brief_path") or None)
    if bar is not None:
        bar = str(bar).strip() or None
    ingress = AppsRgIngressPayload(
        app_id=app_id,
        task_class=task_class,
        target_company=payload.get("target_company"),
        target_role=payload.get("target_role"),
        target_level=payload.get("target_level"),
        source_resume_ref=payload.get("source_resume_ref"),
        source_resume_text=payload.get("source_resume_text"),
        job_description_ref=payload.get("job_description_ref"),
        job_description_text=payload.get("job_description_text"),
        briefing_artifact_ref=bar,
        auto_research_internal=bool(payload.get("auto_research_internal", False)),
        auto_research_tavily=bool(payload.get("auto_research_tavily", False)),
        research_via=payload.get("research_via"),
        idempotency_key=payload.get("idempotency_key"),
        payload_digest=str(payload.get("payload_digest", "")),
        l5_certification_ref=payload.get("l5_certification_ref") or "test:valid:w6",
        user_constraints=user_constraints,
        output_preferences=payload.get("output_preferences") or {},
    )
    ingress = enrich_ingress_resume_inline_text(ingress)

    replay_key = str(
        payload.get("replay_key")
        or payload.get("idempotency_key")
        or ""
    )

    return RequestEnvelope(
        payload=ingress,
        request_id=str(payload.get("request_id", "")),
        run_id=str(payload.get("run_id", "")),
        tenant_id=str(payload.get("tenant_id", "")),
        trace_id=str(payload.get("trace_id", "")),
        submitted_at=str(payload.get("submitted_at", "")),
        replay_key=replay_key,
    )


def apps_rg_dispatch(envelope: Any) -> SimpleNamespace:
    """Dispatch a parsed RequestEnvelope through the apps_rg CLI seam.

    Parameters
    ----------
    envelope:
        A `RequestEnvelope` (or compatible object) to dispatch.

    Returns
    -------
    SimpleNamespace
        Pipeline view with ``exit_status``, ``execution_status``, and
        ``outcome_authorized`` (and optional ``error``).
    """
    try:
        from agentic_core.runtime.entry.apps_rg_dispatch import dispatch_apps_rg_run

        payload_obj = getattr(envelope, "payload", None)
        if payload_obj is not None and hasattr(payload_obj, "target_company"):
            p = payload_obj
            uc = dict(getattr(p, "user_constraints", None) or {})
            gm = str(uc.get("_generation_mode") or "strategic_tailor")
            raw = dispatch_apps_rg_run(
                target_company=str(p.target_company or ""),
                target_role=str(p.target_role or ""),
                target_level=str(p.target_level or ""),
                jd=str(p.job_description_text or ""),
                job_description_ref=str(p.job_description_ref or "") or "",
                job_description_text=str(p.job_description_text or "") or "",
                manual_brief=str(
                    getattr(p, "briefing_artifact_ref", None)
                    or getattr(p, "manual_brief_path", None)
                    or ""
                )
                or "",
                resume_path=str(p.source_resume_ref or "") or "",
                source_resume_text=str(p.source_resume_text or "") or "",
                generation_mode=gm,
                artifact_dir="",
            )

        else:
            app_payload = getattr(envelope, "app_payload", {}) or {}
            raw = dispatch_apps_rg_run(
                target_company=app_payload.get("target_company", ""),
                target_role=app_payload.get("target_role", ""),
                target_level=app_payload.get("target_level", ""),
                jd=str(app_payload.get("job_description_text", "") or ""),
                job_description_ref=str(app_payload.get("job_description_ref") or "") or "",
                job_description_text=str(app_payload.get("job_description_text") or "") or "",
                manual_brief=str(
                    app_payload.get("briefing_artifact_ref")
                    or app_payload.get("manual_brief_path")
                    or ""
                )
                or "",
                resume_path=str(
                    app_payload.get("source_resume_ref")
                    or app_payload.get("source_resume_path")
                    or ""
                )
                or "",
                source_resume_text=str(app_payload.get("source_resume_text") or "") or "",
                generation_mode=app_payload.get("generation_mode", "strategic_tailor"),
                artifact_dir=app_payload.get("output_directory", ""),
            )
        return _as_dispatch_view(raw if isinstance(raw, dict) else {"exit_status": "error"})
    except Exception as exc:
        return _as_dispatch_view(
            {
                "exit_status": "error",
                "execution_status": "failed",
                "error": str(exc),
            }
        )
