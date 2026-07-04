"""apps_rg runtime entry — canonical product dispatch and AG-2 C0/PA wiring surface.

``dispatch_apps_rg_run`` is the **canonical product entrypoint** (CLI primitives
→ governed R4 spine + L7).  ``run_ag2_retrieval_and_prompt`` holds the canonical
``c0_retrieve_apps_rg`` / ``pa_compose_apps_rg`` call sites that must pass
``validated_request`` as the final positional argument (contract tests scan
this module).
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


def _load_app_attr(module_name: str, attr_name: str) -> Any:
    """Resolve app-owned entrypoints without static core-to-app import edges."""
    return getattr(import_module(module_name), attr_name)


def apps_rg_parse(payload: dict[str, Any]) -> Any:
    """Re-export parser behavior for legacy callers without a static app import."""
    app_parse = _load_app_attr("apps_rg.runtime.dispatch.apps_rg_dispatch", "apps_rg_parse")
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
    """Canonical apps_rg product entry — delegates to governed R4 spine + L7.

    Thin delegate to ``apps_rg.runtime.orchestration.canonical_dispatch`` so
    ``python -m apps_rg`` exercises U0→L1→L0→C0→L2→Exit with L7 emit on the
    integrated R4 entrypoint.  Use ``apps_rg.__main__`` ``--dry-run`` for
    validation-only (no spine run).

    Returns a dict so ``apps_rg.__main__`` and smoke tests can read
    ``exit_status`` / ``outcome_authorized`` without importing dataclasses.
    """
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
    """AG-2 slice: C0 then PA, both consuming ``ValidatedRequest`` (AST-scanned)."""
    c0_retrieve_apps_rg = _load_app_attr(
        "apps_rg.runtime.bindings.c0_binding",
        "c0_retrieve_apps_rg",
    )
    pa_compose_apps_rg = _load_app_attr(
        "apps_rg.runtime.bindings.pa_binding",
        "pa_compose_apps_rg",
    )

    fec = c0_retrieve_apps_rg(route, validated_request)
    return pa_compose_apps_rg(route, plan, fec, validated_request)


def apps_rg_dispatch(envelope: Any) -> Any:
    """Agent entry: delegate to app-owned ``apps_rg.runtime.dispatch``."""
    app_dispatch = _load_app_attr(
        "apps_rg.runtime.dispatch.apps_rg_dispatch",
        "apps_rg_dispatch",
    )

    return app_dispatch(envelope)
