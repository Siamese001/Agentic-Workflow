"""U0 briefing presence signals for apps_rg L1/L0 planning.

Vocabulary split (product):
- ``grounding_required``: resume fact evidence binding (C0.1-C0.7) — always True
  for active apps_rg generation modes.
- ``briefing_required``: targeting briefing is mandatory for product-visible
  active generation. During the graph-skills/apps_research debugging window,
  active product generation also marks apps_research as required so route
  receipts cannot silently claim the briefing path was irrelevant.
"""

from __future__ import annotations

from typing import Any, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest

_BRIEFING_REF_KEYS = ("briefing_artifact_ref", "manual_brief_path")


class BriefingMissingError(ValueError):
    """Raised when product-visible apps_rg generation lacks a U0 briefing."""


def briefing_supplied_at_u0(app_payload: Mapping[str, Any] | None) -> bool:
    """True when U0 carried an uploaded path ref or non-empty inline briefing text."""

    if not app_payload:
        return False

    policy_refs = app_payload.get("policy_refs")
    if isinstance(policy_refs, Mapping):
        for key in _BRIEFING_REF_KEYS:
            if str(policy_refs.get(key) or "").strip():
                return True

    for key in _BRIEFING_REF_KEYS:
        if str(app_payload.get(key) or "").strip():
            return True

    briefing = app_payload.get("briefing")
    if isinstance(briefing, Mapping):
        for key in _BRIEFING_REF_KEYS:
            if str(briefing.get(key) or "").strip():
                return True
        if str(briefing.get("briefing_text") or briefing.get("text") or "").strip():
            return True

    if str(app_payload.get("briefing_text") or "").strip():
        return True

    user_constraints = app_payload.get("user_constraints")
    if isinstance(user_constraints, Mapping):
        if str(user_constraints.get("briefing_text") or "").strip():
            return True

    return False


def apps_research_call_required_at_u0(
    validated_request: ValidatedRequest,
    *,
    active_generation_mode: bool,
) -> bool:
    """Return whether active product generation should require apps_research.

    This is intentionally true-by-default while debugging apps_research briefing
    integration. Callers may still suppress it for non-product fixture paths
    before writing the L1/Route contracts.
    """

    _ = validated_request
    return bool(active_generation_mode)


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
    """Fail closed when product-visible active generation lacks briefing."""

    if not briefing_required_for_run(
        validated_request,
        active_generation_mode=active_generation_mode,
        product_visible=product_visible,
        non_product_certified=non_product_certified,
    ):
        return
    msg = (
        "apps_rg requires an uploaded briefing artifact or authoritative "
        "briefing text; apps_research is required for active product generation"
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
