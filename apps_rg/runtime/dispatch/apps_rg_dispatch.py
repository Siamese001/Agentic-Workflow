"""apps_rg runtime dispatch — payload parsing and dispatch helpers.

`apps_rg_parse` converts a raw dict payload into an `agentic_core`
`RequestEnvelope`. `apps_rg_dispatch` runs the full pipeline from a
parsed envelope and returns the run result dict.

These helpers are the thin app-side counterparts to
`agentic_core.runtime.entry.apps_rg_dispatch`.
"""
from __future__ import annotations

from typing import Any

__all__ = ["apps_rg_dispatch", "apps_rg_parse"]


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

    app_id = payload.get("app_id", "apps_rg")
    task_class = payload.get("task_class", "resume_generation")

    app_payload: dict[str, Any] = {
        k: v
        for k, v in payload.items()
        if k not in ("app_id", "task_class")
    }

    return RequestEnvelope(
        app_id=app_id,
        task_class=task_class,
        app_payload=app_payload,
    )


def apps_rg_dispatch(envelope: Any) -> dict[str, Any]:
    """Dispatch a parsed RequestEnvelope through the full apps_rg pipeline.

    Parameters
    ----------
    envelope:
        A `RequestEnvelope` (or compatible object) to dispatch.

    Returns
    -------
    dict
        Pipeline result with at minimum ``exit_status`` and
        ``execution_status`` keys.
    """
    try:
        from agentic_core.runtime.entry.apps_rg_dispatch import (
            dispatch_apps_rg_run,
        )

        app_payload = getattr(envelope, "app_payload", {}) or {}
        return dispatch_apps_rg_run(
            target_company=app_payload.get("target_company", ""),
            target_role=app_payload.get("target_role", ""),
            target_level=app_payload.get("target_level", ""),
            jd=app_payload.get("job_description_text", ""),
            manual_brief=app_payload.get("manual_brief_path", "") or "",
            resume_path=app_payload.get("source_resume_path", "") or "",
            generation_mode=app_payload.get("generation_mode", "strategic_tailor"),
            artifact_dir=app_payload.get("output_directory", ""),
        )
    except Exception as exc:
        return {
            "exit_status": "error",
            "execution_status": "failed",
            "error": str(exc),
        }
