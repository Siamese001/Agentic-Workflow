"""S2: Section treatment profile resolver for apps_rg resume-shipping pipeline.

App-local resolver. Loads resume_section_treatment_profile.v1.json and provides
policy lookup by section and bullet ordinal.

Hard boundaries:
- No generation behavior.
- No model calls.
- No PA, C0, L2, or agentic_core imports.
- Fails closed on unknown section or missing profile.

See: artifacts/governance/apps_rg_resume_shipping_s2_section_treatment_matrix.md
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_PROFILE_PATH = (
    Path(__file__).parent.parent.parent
    / "config"
    / "domain_contract"
    / "resume_section_treatment_profile.v1.json"
)

_REQUIRED_SECTIONS = frozenset([
    "headline",
    "executive_summary",
    "unify_narrative",
    "unify_bullets",
    "ibm_narrative",
    "ibm_bullets",
    "insurtech_narrative",
    "insurtech_bullets",
    "ey_narrative",
    "ey_bullets",
    "early_career",
    "competencies",
    "education",
    "certifications",
])

_VALID_TREATMENTS = frozenset([
    "HEAVY",
    "MODERATE",
    "LIGHT",
    "VERBATIM",
    "JD_RANKED_NOUN_PHRASES",
    "TIERED_BY_ORDINAL",
])

_profile_cache: dict[str, Any] | None = None


class SectionTreatmentProfileError(RuntimeError):
    """Raised when the treatment profile is missing or invalid. Fail-closed."""


class UnknownSectionError(SectionTreatmentProfileError):
    """Raised when a section_id is not found in the profile. Fail-closed."""


def _load_profile() -> dict[str, Any]:
    """Load and validate the treatment profile from disk. Caches after first load."""
    global _profile_cache
    if _profile_cache is not None:
        return _profile_cache

    if not _PROFILE_PATH.exists():
        raise SectionTreatmentProfileError(
            f"Treatment profile not found: {_PROFILE_PATH}. "
            "S2 requires apps_rg/config/domain_contract/resume_section_treatment_profile.v1.json"
        )

    with open(_PROFILE_PATH, encoding="utf-8") as f:
        profile = json.load(f)

    _validate_profile(profile)
    _profile_cache = profile
    return profile


def _validate_profile(profile: dict[str, Any]) -> None:
    """Fail closed if any required section is missing."""
    sections = profile.get("sections", {})
    missing = _REQUIRED_SECTIONS - set(sections.keys())
    if missing:
        raise SectionTreatmentProfileError(
            f"Treatment profile is missing required sections: {sorted(missing)}"
        )


def get_section_policy(section_id: str) -> dict[str, Any]:
    """Return the full policy dict for a section.

    Fails closed with UnknownSectionError for any section_id not in the profile.
    Never rewrites text. Never calls models, PA, or C0.
    """
    profile = _load_profile()
    sections = profile["sections"]
    if section_id not in sections:
        raise UnknownSectionError(
            f"Unknown section '{section_id}'. "
            f"Valid sections: {sorted(sections.keys())}"
        )
    return sections[section_id]


def get_bullet_treatment(section_id: str, ordinal: int) -> str:
    """Return the treatment tier string for a bullet at a given ordinal.

    For TIERED_BY_ORDINAL sections: walks ordinal_tiers in order, returns
    the tier for the first matching range (ordinal_max=null means unbounded).
    For flat treatment sections: returns section treatment directly.
    Fails closed on unknown section.
    Never rewrites text. Never calls models, PA, or C0.
    """
    policy = get_section_policy(section_id)
    treatment = policy["treatment"]

    if treatment != "TIERED_BY_ORDINAL":
        return treatment

    tiers = policy.get("bullet_ordinal_tiers", [])
    for tier in tiers:
        low = tier["ordinal_min"]
        high = tier["ordinal_max"]
        if high is None:
            if ordinal >= low:
                return tier["treatment"]
        elif low <= ordinal <= high:
            return tier["treatment"]

    raise SectionTreatmentProfileError(
        f"No tier matched for section '{section_id}' ordinal {ordinal}. "
        f"Profile tiers: {tiers}"
    )


def list_required_sections() -> list[str]:
    """Return sorted list of all required section IDs."""
    return sorted(_REQUIRED_SECTIONS)


def is_verbatim_section(section_id: str) -> bool:
    """Return True if this section must be preserved verbatim."""
    policy = get_section_policy(section_id)
    return policy.get("preserve_verbatim", False) is True


def reset_cache() -> None:
    """Reset the in-process profile cache. For testing only."""
    global _profile_cache
    _profile_cache = None


__all__ = [
    "SectionTreatmentProfileError",
    "UnknownSectionError",
    "get_section_policy",
    "get_bullet_treatment",
    "list_required_sections",
    "is_verbatim_section",
    "reset_cache",
]
