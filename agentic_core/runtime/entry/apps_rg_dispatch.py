"""apps_rg runtime entry — signed-preflight product dispatch and AG-2 C0/PA wiring.

``dispatch_apps_rg_run`` is the canonical product entrypoint. The AG-2 helper
threads the verified L1 plan into C0 before prompt assembly.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "apps_rg_dispatch",
    "apps_rg_parse",
    "dispatch_apps_rg_run",
    "run_ag2_retrieval_and_prompt",
]

_MISSING_APP_ATTR = object()


def _load_app_attr(module_name: str, attr_name: str) -> Any:
    """Resolve app-owned entrypoints without static core-to-app import edges."""

    module = import_module(module_name)
    value = getattr(module, attr_name, _MISSING_APP_ATTR)
    if value is _MISSING_APP_ATTR:
        raise AttributeError(f"{module.__name__!r} does not export {attr_name!r}")
    return value


def apps_rg_parse(payload: dict[str, Any]) -> Any:
    app_parse = _load_app_attr(
        "apps_rg.runtime.dispatch.apps_rg_dispatch",
        "apps_rg_parse",
    )
    return app_parse(payload)


def dispatch_apps_rg_run(
    *,
    target_company: str = "",
    target_role: str = "",
    target_level: str = "",
    jd: str = "",
    manual_brief: str = "",
    resume_path: str = "",
    generation_mode: str = "strategic_tailor",
    artifact_dir: str = "",
) -> dict[str, Any]:
    """Canonical product entry — delegate to the app-owned fresh-E2E facade."""

    if not str(target_company).strip() or not str(target_role).strip():
        return {
            "exit_status": "error",
            "execution_status": "failed",
            "outcome_authorized": False,
            "error": "target_company and target_role are required",
        }
    run_canonical_apps_rg_from_cli_primitives = _load_app_attr(
        "apps_rg.runtime.orchestration.canonical_dispatch",
        "run_canonical_apps_rg_from_cli_primitives",
    )
    return run_canonical_apps_rg_from_cli_primitives(
        target_company=target_company,
        target_role=target_role,
        target_level=target_level,
        jd=jd,
        manual_brief=manual_brief,
        resume_path=resume_path,
        generation_mode=generation_mode,
        artifact_dir=artifact_dir,
    )


def run_ag2_retrieval_and_prompt(
    route: Any,
    plan: Any,
    validated_request: Any,
) -> Any:
    """AG-2 slice: verified L1 plan -> C0 -> PA."""

    c0_retrieve_apps_rg = _load_app_attr(
        "apps_rg.runtime.bindings.c0_planned_binding",
        "c0_retrieve_apps_rg_planned",
    )
    pa_compose_apps_rg = _load_app_attr(
        "apps_rg.runtime.bindings.pa_planned_binding",
        "pa_compose_apps_rg_planned",
    )
    fec = c0_retrieve_apps_rg(
        route,
        validated_request,
        l1_plan=plan,
    )
    return pa_compose_apps_rg(
        route,
        plan,
        fec,
        validated_request,
    )


def apps_rg_dispatch(envelope: Any) -> Any:
    app_dispatch = _load_app_attr(
        "apps_rg.runtime.dispatch.apps_rg_dispatch",
        "apps_rg_dispatch",
    )
    return app_dispatch(envelope)
