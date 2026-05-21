"""apps_rg section treatment profile — per-section prompt and bullet policy.

Defines how each resume section should be treated during prompt assembly:
- HEAVY  — full rewrite with C0 evidence injection
- LIGHT  — light polish only
- VERBATIM — copy from source without modification
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

__all__ = [
    "SectionTreatmentProfileError",
    "UnknownSectionError",
    "get_bullet_treatment",
    "get_section_policy",
    "is_verbatim_section",
    "list_required_sections",
    "reset_cache",
    "_profile_cache",
]


class SectionTreatmentProfileError(Exception):
    """Base error for section treatment profile violations."""


class UnknownSectionError(SectionTreatmentProfileError):
    """Raised when a section ID is not in the treatment profile."""


_DEFAULT_PROFILE: dict[str, dict[str, Any]] = {
    "headline": {
        "treatment": "HEAVY",
        "verbatim": False,
        "required": True,
        "min_bullets": 0,
        "max_bullets": 0,
        "bullet_treatment": "NONE",
        "evidence_required": True,
        "section_type": "single_line",
    },
    "executive_summary": {
        "treatment": "HEAVY",
        "verbatim": False,
        "required": True,
        "min_bullets": 3,
        "max_bullets": 5,
        "bullet_treatment": "HEAVY",
        "evidence_required": True,
        "section_type": "bullets",
    },
    "unify_consulting": {
        "treatment": "HEAVY",
        "verbatim": False,
        "required": True,
        "min_bullets": 4,
        "max_bullets": 8,
        "bullet_treatment": "HEAVY",
        "evidence_required": True,
        "section_type": "bullets",
    },
    "ibm": {
        "treatment": "HEAVY",
        "verbatim": False,
        "required": True,
        "min_bullets": 3,
        "max_bullets": 7,
        "bullet_treatment": "HEAVY",
        "evidence_required": True,
        "section_type": "bullets",
    },
    "insurtech": {
        "treatment": "HEAVY",
        "verbatim": False,
        "required": True,
        "min_bullets": 2,
        "max_bullets": 5,
        "bullet_treatment": "HEAVY",
        "evidence_required": True,
        "section_type": "bullets",
    },
    "ey": {
        "treatment": "LIGHT",
        "verbatim": False,
        "required": True,
        "min_bullets": 2,
        "max_bullets": 5,
        "bullet_treatment": "LIGHT",
        "evidence_required": False,
        "section_type": "bullets",
    },
    "early_career": {
        "treatment": "VERBATIM",
        "verbatim": True,
        "required": True,
        "min_bullets": 1,
        "max_bullets": 3,
        "bullet_treatment": "VERBATIM",
        "evidence_required": False,
        "section_type": "bullets",
    },
    "education": {
        "treatment": "VERBATIM",
        "verbatim": True,
        "required": True,
        "min_bullets": 0,
        "max_bullets": 10,
        "bullet_treatment": "VERBATIM",
        "evidence_required": False,
        "section_type": "structured",
    },
    "certifications": {
        "treatment": "VERBATIM",
        "verbatim": True,
        "required": True,
        "min_bullets": 0,
        "max_bullets": 20,
        "bullet_treatment": "VERBATIM",
        "evidence_required": False,
        "section_type": "structured",
    },
    "awards": {
        "treatment": "LIGHT",
        "verbatim": False,
        "required": False,
        "min_bullets": 0,
        "max_bullets": 10,
        "bullet_treatment": "LIGHT",
        "evidence_required": False,
        "section_type": "bullets",
    },
    "publications": {
        "treatment": "VERBATIM",
        "verbatim": True,
        "required": False,
        "min_bullets": 0,
        "max_bullets": 20,
        "bullet_treatment": "VERBATIM",
        "evidence_required": False,
        "section_type": "structured",
    },
    "patents": {
        "treatment": "VERBATIM",
        "verbatim": True,
        "required": False,
        "min_bullets": 0,
        "max_bullets": 20,
        "bullet_treatment": "VERBATIM",
        "evidence_required": False,
        "section_type": "structured",
    },
    "speaking": {
        "treatment": "LIGHT",
        "verbatim": False,
        "required": False,
        "min_bullets": 0,
        "max_bullets": 10,
        "bullet_treatment": "LIGHT",
        "evidence_required": False,
        "section_type": "bullets",
    },
    "board_memberships": {
        "treatment": "LIGHT",
        "verbatim": False,
        "required": False,
        "min_bullets": 0,
        "max_bullets": 10,
        "bullet_treatment": "LIGHT",
        "evidence_required": False,
        "section_type": "bullets",
    },
}

_profile_cache: Optional[dict[str, dict[str, Any]]] = None


def reset_cache() -> None:
    """Clear the cached section treatment profile (test helper)."""
    global _profile_cache
    _profile_cache = None


def _load_profile() -> dict[str, dict[str, Any]]:
    """Load and cache the section treatment profile."""
    global _profile_cache
    if _profile_cache is not None:
        return _profile_cache

    yaml_candidates = [
        Path(__file__).resolve().parents[3] / "rg_evidence_profile.yaml",
        Path(__file__).resolve().parents[4] / "apps_rg" / "rg_evidence_profile.yaml",
    ]
    for path in yaml_candidates:
        if path.exists():
            try:
                import yaml
                with open(path, encoding="utf-8") as f:
                    raw = yaml.safe_load(f) or {}
                sections = raw.get("sections", {})
                if sections:
                    _profile_cache = dict(sections)
                    return _profile_cache
            except Exception:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
                pass

    _profile_cache = dict(_DEFAULT_PROFILE)
    return _profile_cache


def list_required_sections() -> list[str]:
    """Return all section IDs defined in the treatment profile."""
    return list(_load_profile().keys())


def get_section_policy(section_id: str) -> dict[str, Any]:
    """Return the treatment policy dict for a section.

    Raises
    ------
    UnknownSectionError
        If section_id is not in the profile.
    """
    profile = _load_profile()
    if section_id not in profile:
        raise UnknownSectionError(
            f"Section '{section_id}' is not defined in the section treatment profile. "
            f"Known sections: {sorted(profile.keys())}"
        )
    return dict(profile[section_id])


def is_verbatim_section(section_id: str) -> bool:
    """Return True if the section must be copied verbatim from source."""
    try:
        policy = get_section_policy(section_id)
        return bool(policy.get("verbatim", False))
    except UnknownSectionError:
        return False


def get_bullet_treatment(section_id: str, bullet_index: int) -> str:
    """Return the bullet treatment for a specific bullet position.

    Parameters
    ----------
    section_id:
        The resume section ID.
    bullet_index:
        0-based index of the bullet within the section.

    Returns
    -------
    str
        One of: "HEAVY", "LIGHT", "VERBATIM", "NONE".

    Raises
    ------
    UnknownSectionError
        If section_id is not in the profile.
    """
    policy = get_section_policy(section_id)
    return str(policy.get("bullet_treatment", "HEAVY"))
