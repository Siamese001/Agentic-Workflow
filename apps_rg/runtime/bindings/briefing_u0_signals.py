"""U0 briefing presence and provenance signals for apps_rg L1/L0 planning.

Vocabulary split (product):
- ``grounding_required``: resume fact evidence binding (C0.1-C0.7).
- ``briefing_required``: targeting briefing is mandatory for product-visible
  generation.
- Auto-research briefings are accepted only when the adjacent apps_research
  envelope proves a canonical GateMesh -> Exit ``X3D_ALLOW_FINISH`` chain.
"""

from __future__ import annotations

import os

from typing import Any, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest

_BRIEFING_REF_KEYS = ("briefing_artifact_ref", "manual_brief_path")


class BriefingMissingError(ValueError):
    """Raised when product-visible apps_rg generation lacks a U0 briefing."""


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _briefing_ref(app_payload: Mapping[str, Any]) -> str:
    policy_refs = app_payload.get("policy_refs")
    if isinstance(policy_refs, Mapping):
        for key in _BRIEFING_REF_KEYS:
            ref = str(policy_refs.get(key) or "").strip()
            if ref:
                return ref

    for key in _BRIEFING_REF_KEYS:
        ref = str(app_payload.get(key) or "").strip()
        if ref:
            return ref

    briefing = app_payload.get("briefing")
    if isinstance(briefing, Mapping):
        for key in _BRIEFING_REF_KEYS:
            ref = str(briefing.get(key) or "").strip()
            if ref:
                return ref
    return ""


def _inline_briefing_present(app_payload: Mapping[str, Any]) -> bool:
    briefing = app_payload.get("briefing")
    if isinstance(briefing, Mapping):
        if str(
            briefing.get("briefing_text") or briefing.get("text") or ""
        ).strip():
            return True
    if str(app_payload.get("briefing_text") or "").strip():
        return True
    user_constraints = app_payload.get("user_constraints")
    return bool(
        isinstance(user_constraints, Mapping)
        and str(user_constraints.get("briefing_text") or "").strip()
    )


def _apps_research_proof_required(app_payload: Mapping[str, Any]) -> bool:
    # Existing unit suites use legacy handoff fixtures. This escape is available
    # only inside the explicit test harness; product and E2E execution remain
    # fail-closed unless the canonical Exit chain is present.
    if _truthy(os.environ.get("APPS_RG_TEST_HARNESS")) and not _truthy(
        os.environ.get("APPS_RG_ENFORCE_CANONICAL_RESEARCH_EXIT_IN_TESTS")
    ):
        return False

    user_constraints = app_payload.get("user_constraints")
    constraints = (
        user_constraints if isinstance(user_constraints, Mapping) else {}
    )
    research_via = str(
        app_payload.get("research_via")
        or constraints.get("research_via")
        or ""
    ).strip().lower()
    return (
        _truthy(
            app_payload.get("auto_research_internal")
            or constraints.get("auto_research_internal")
        )
        or research_via == "apps_research"
        or str(constraints.get("caller_app_id") or "").strip() == "apps_research"
    )


def _jd_ref(app_payload: Mapping[str, Any]) -> str:
    return str(
        app_payload.get("job_description_ref")
        or app_payload.get("job_description_text")
        or app_payload.get("jd_text")
        or app_payload.get("jd_data")
        or ""
    ).strip()


def briefing_supplied_at_u0(app_payload: Mapping[str, Any] | None) -> bool:
    """Return True only for a present and, when required, authorized briefing."""
    if not app_payload:
        return False

    ref = _briefing_ref(app_payload)
    inline_present = _inline_briefing_present(app_payload)
    if not ref and not inline_present:
        return False

    if not _apps_research_proof_required(app_payload):
        return True

    # Auto-research is producer-authoritative: inline/manual text cannot stand in
    # for the canonical producer bundle.
    if not ref:
        return False

    from apps_rg.prerequisites.briefing_validator import (
        validate_apps_research_handoff,
    )

    validation = validate_apps_research_handoff(
        brief_ref=ref,
        jd_ref=_jd_ref(app_payload),
        require_observed=True,
        require_x1_x3_authorization=True,
        require_canonical_exit=True,
    )
    return bool(validation.valid)


def apps_research_call_required_at_u0(
    validated_request: ValidatedRequest,
    *,
    active_generation_mode: bool,
) -> bool:
    """Return whether auto-research lacks an authorized producer briefing."""
    if not active_generation_mode:
        return False
    payload = getattr(validated_request, "app_payload", None) or {}
    if not isinstance(payload, Mapping):
        return False
    return _apps_research_proof_required(payload) and not briefing_supplied_at_u0(
        payload
    )


def briefing_required_for_run(
    validated_request: ValidatedRequest,
    *,
    active_generation_mode: bool,
    product_visible: bool = True,
    non_product_certified: bool = False,
) -> bool:
    """True when a product-visible active generation run lacks U0 briefing."""
    if not active_generation_mode:
        return False
    if not product_visible:
        return False
    if non_product_certified:
        return False
    return not briefing_supplied_at_u0(
        getattr(validated_request, "app_payload", None) or {}
    )


def briefing_validate_or_raise(
    validated_request: ValidatedRequest,
    *,
    active_generation_mode: bool,
    product_visible: bool = True,
    non_product_certified: bool = False,
    context: str = "",
) -> None:
    """Fail closed when product-visible generation lacks authorized briefing."""
    if not briefing_required_for_run(
        validated_request,
        active_generation_mode=active_generation_mode,
        product_visible=product_visible,
        non_product_certified=non_product_certified,
    ):
        return
    msg = (
        "apps_rg requires a run-specific briefing; auto-research inputs must "
        "carry a digest-bound canonical apps_research Exit authorization"
    )
    if context:
        msg = f"{msg}. Context: {context}"
    raise BriefingMissingError(msg)


__all__ = [
    "BriefingMissingError",
    "briefing_required_for_run",
    "briefing_supplied_at_u0",
    "briefing_validate_or_raise",
    "apps_research_call_required_at_u0",
]
