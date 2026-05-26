"""U0 briefing presence signals for apps_rg L1/L0 planning.

Vocabulary split (product):
- ``grounding_required``: resume fact evidence binding (C0.1–C0.7) — always True for
  active apps_rg generation modes.
- ``apps_research_call_required``: delegate company briefing to apps_research when U0 did
  not supply an authoritative briefing artifact or inline briefing text.
"""

from __future__ import annotations

from typing import Any, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest

_BRIEFING_REF_KEYS = ("briefing_artifact_ref", "manual_brief_path")


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
    """True when company brief must be obtained via apps_research (no U0 briefing)."""

    if not active_generation_mode:
        return False
    return not briefing_supplied_at_u0(
        getattr(validated_request, "app_payload", None) or {}
    )


__all__ = [
    "briefing_supplied_at_u0",
    "apps_research_call_required_at_u0",
]
