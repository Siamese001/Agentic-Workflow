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


_CANONICAL_RECIPIENT_CLASSES = {
    "CEO",
    "RECRUITER",
    "SENIOR_TA",
    "HIRING_MANAGER",
    "EXECUTIVE",
    "C_LEVEL",
    "VP_ENG",
    "CTO",
    "REFERRAL_CONTACT",
}

_RECIPIENT_ALIASES = {
    "SENIOR TA": "SENIOR_TA",
    "SENIOR_TALENT_ACQUISITION": "SENIOR_TA",
    "TALENT_ACQUISITION_LEADER": "SENIOR_TA",
    "HIRING MANAGER": "HIRING_MANAGER",
    "C-LEVEL": "C_LEVEL",
    "C LEVEL": "C_LEVEL",
    "VP ENG": "VP_ENG",
}


def _extract(request: Any, key: str, default: Any = "") -> Any:
    """Support both Pydantic ``CampaignRequest`` and plain dict shapes."""
    if request is None:
        return default
    if hasattr(request, key):
        return getattr(request, key, default)
    if isinstance(request, dict):
        return request.get(key, default)
    return default


def _canonical_recipient_class(raw: Any) -> str:
    value = str(raw or "").strip().upper().replace("-", "_")
    value = _RECIPIENT_ALIASES.get(value.replace("_", " "), value)
    return value if value in _CANONICAL_RECIPIENT_CLASSES else ""


def classify_recipient_profile(profile: Any, *, fallback: str = "RECRUITER") -> str:
    """Classify a public/provided target profile into apps_lic recipient class."""
    if not isinstance(profile, dict):
        return _canonical_recipient_class(fallback) or "RECRUITER"

    explicit = _canonical_recipient_class(profile.get("seniority_class"))
    if explicit:
        return explicit

    title = str(profile.get("title", "") or "")
    background = str(profile.get("background", "") or "")
    corpus = f"{title} {background}".lower()

    talent_signal = any(
        token in corpus
        for token in (
            "talent acquisition",
            "recruiting",
            "recruitment",
            "sourcer",
            "recruiter",
        )
    )
    leadership_signal = any(
        token in corpus
        for token in (
            "head",
            "director",
            "leader",
            "lead",
            "manager",
            "vp",
            "vice president",
            "executive",
        )
    )
    if talent_signal and leadership_signal:
        return "SENIOR_TA"
    if talent_signal:
        return "RECRUITER"
    if any(
        token in corpus
        for token in (
            "chief",
            "cfo",
            "cio",
            "cdo",
            "cto",
            "ceo",
            "executive vice president",
            " evp",
            "global head",
            "president",
        )
    ):
        return "EXECUTIVE"
    if any(token in corpus for token in ("hiring manager", "engineering manager")):
        return "HIRING_MANAGER"
    if any(token in corpus for token in ("vp engineering", "vp, engineering")):
        return "VP_ENG"

    return _canonical_recipient_class(fallback) or "RECRUITER"


class ProfileAnalysisEngine:
    """Emit profile features — audience, compliance, archetype hint."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        req = context.get("campaign_request")
        config = _extract(req, "config", {}) if req is not None else {}

        target_profile = _extract(config, "target_contact", {})
        target_audience = _extract(config, "target_audience", "")
        compliance_level = _extract(config, "compliance_level", "standard")
        campaign_name = _extract(config, "name", "")
        c0_recipient_class = _canonical_recipient_class(_extract(config, "recipient_class", ""))
        recipient_class_source = str(
            _extract(config, "recipient_class_source", "")
            or ""
        ).upper()
        if recipient_class_source == "C0_DERIVED" and c0_recipient_class:
            recipient_class = c0_recipient_class
        else:
            recipient_class = classify_recipient_profile(
                target_profile,
                fallback=target_audience or "RECRUITER",
            )

        # Low-cost archetype hint — keyword match on audience + name.
        corpus = f"{recipient_class} {target_audience} {campaign_name}".lower()
        if recipient_class in {"RECRUITER", "SENIOR_TA"}:
            archetype_hint = "RECRUITER"
        elif recipient_class in {"CEO", "EXECUTIVE", "C_LEVEL", "CTO"}:
            archetype_hint = "EXECUTIVE"
        elif recipient_class in {"HIRING_MANAGER", "VP_ENG"}:
            archetype_hint = "HIRING_MANAGER"
        elif "recruit" in corpus or "hiring" in corpus:
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
                "target_contact": target_profile if isinstance(target_profile, dict) else {},
                "recipient_class": recipient_class,
                "compliance_level": compliance_level,
                "campaign_name": campaign_name,
                "archetype_hint": archetype_hint,
            },
        }


__all__ = ["ProfileAnalysisEngine", "classify_recipient_profile"]
