"""Canonical human-facing labels for résumé sections (export, manifest, run summaries).

JSON/schema keys stay ``skills`` / ``competencies`` where required; operator surfaces use
``ENGINEERING & PLATFORM COMPETENCIES`` for the same bucket.
"""

from __future__ import annotations

ENGINEERING_PLATFORM_COMPETENCIES_HEADING: str = "ENGINEERING & PLATFORM COMPETENCIES"

CERTIFICATIONS_AND_CREDENTIALS_HEADING: str = "CERTIFICATIONS & CREDENTIALS"

_SECTION_HEADING_BY_ID: dict[str, str] = {
    "certifications": CERTIFICATIONS_AND_CREDENTIALS_HEADING,
    "competencies": ENGINEERING_PLATFORM_COMPETENCIES_HEADING,
    "skills": ENGINEERING_PLATFORM_COMPETENCIES_HEADING,
    "skills_block": ENGINEERING_PLATFORM_COMPETENCIES_HEADING,
}


def summary_section_label(section_id: str) -> str:
    """Résumé section label for narrative verdicts, gate failures, and operator logs."""
    sid = str(section_id or "").strip()
    return _SECTION_HEADING_BY_ID.get(sid, sid)


__all__ = [
    "CERTIFICATIONS_AND_CREDENTIALS_HEADING",
    "ENGINEERING_PLATFORM_COMPETENCIES_HEADING",
    "summary_section_label",
]
