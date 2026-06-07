"""HOP1 profile_analysis — derive profile features from the campaign request.

Reads ``context["campaign_request"]`` (a ``CampaignRequest`` or dict with
equivalent shape) and emits ``context["profile_features"]`` carrying the
audience, compliance level, and any campaign-name-derived indicators that
downstream stages key on.

This is a re-derivation, not a resurrection — the original HOP1 body was
lost in the 2026-02-08 consolidation pass. See plan
docs/archive/windsurf/legacy-tree/plans/apps-hop-substrate-f7751b.md (Wave 2 Phase 2.2).
"""

from __future__ import annotations

from typing import Any


def _extract(request: Any, key: str, default: Any = "") -> Any:
    """Support both Pydantic ``CampaignRequest`` and plain dict shapes."""
    if request is None:
        return default
    if hasattr(request, key):
        return getattr(request, key, default)
    if isinstance(request, dict):
        return request.get(key, default)
    return default


class ProfileAnalysisEngine:
    """Emit profile features — audience, compliance, archetype hint."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        req = context.get("campaign_request")
        config = _extract(req, "config", {}) if req is not None else {}

        target_audience = _extract(config, "target_audience", "")
        compliance_level = _extract(config, "compliance_level", "standard")
        campaign_name = _extract(config, "name", "")

        # Low-cost archetype hint — keyword match on audience + name.
        corpus = f"{target_audience} {campaign_name}".lower()
        if "recruit" in corpus or "hiring" in corpus:
            archetype_hint = "RECRUITER"
        elif "exec" in corpus or "leader" in corpus:
            archetype_hint = "EXECUTIVE"
        elif "engineer" in corpus or "developer" in corpus:
            archetype_hint = "ENGINEER"
        else:
            archetype_hint = "GENERIC"

        return {
            "profile_features": {
                "target_audience": target_audience,
                "compliance_level": compliance_level,
                "campaign_name": campaign_name,
                "archetype_hint": archetype_hint,
            },
        }
