"""Competencies lane: certifications belong in CERTIFICATIONS & CREDENTIALS only (apps_rg)."""

from __future__ import annotations

import re
from typing import Any

from apps_rg.runtime.sections.competencies_term_phrase import term_phrase

RESERVED_CERTIFICATION_CATEGORY_LABELS: frozenset[str] = frozenset(
    {
        "certifications",
        "credentials",
        "certifications & credentials",
        "certifications and credentials",
        "professional certifications",
        "licenses",
        "licences",
        "accreditations",
        "certification",
        "credential",
    }
)

_CLOUD_PLATFORM_CATEGORY_LABEL = "Cloud and Data Platforms"

_PLATFORM_MERGE_LABEL_HINTS: tuple[str, ...] = (
    "cloud and data platform",
    "cloud platform",
    "platform engineering",
    "cloud platforms",
)

# Credential names forbidden as competency terms (substring match, normalized).
_CREDENTIAL_TERM_SUBSTRINGS: tuple[str, ...] = (
    "certified machine learning engineer",
    "aws certified machine learning",
    "aws certified solutions architect",
    "databricks lakehouse fundamentals accreditation",
    "databricks lakehouse fundamentals",
    "fellow of the society of actuaries",
    "society of actuaries",
)

_CREDENTIAL_TERM_RE = re.compile(
    r"^(?:aws\s+)?certified\b|"
    r"\baccreditation\b|"
    r"\bfellow of the\b|"
    r"\bfsa\b|"
    r"\bprofessional certification",
    re.IGNORECASE,
)

# Map normalized credential phrases to platform skill phrases (not credential names).
_CREDENTIAL_TO_SKILL: tuple[tuple[str, str], ...] = (
    ("databricks lakehouse fundamentals accreditation", "Databricks Lakehouse"),
    ("databricks lakehouse fundamentals", "Databricks Lakehouse"),
    ("aws certified solutions architect professional", "AWS"),
    ("aws certified solutions architect", "AWS"),
    ("aws certified machine learning engineer", "AWS"),
    ("certified machine learning engineer associate", "AWS"),
    ("certified solutions architect professional", "AWS"),
    ("fellow of the society of actuaries", ""),
    ("society of actuaries", ""),
)


def _norm_label(label: str) -> str:
    return re.sub(r"\s+", " ", str(label or "").strip().lower())


def _norm_phrase(phrase: str) -> str:
    return re.sub(r"\s+", " ", str(phrase or "").strip().lower()).rstrip(".")


def is_reserved_certification_category(category_label: str) -> bool:
    return _norm_label(category_label) in RESERVED_CERTIFICATION_CATEGORY_LABELS


def is_credential_competency_term(phrase: str) -> bool:
    p = _norm_phrase(phrase)
    if not p:
        return False
    if _CREDENTIAL_TERM_RE.search(p):
        return True
    return any(sub in p for sub in _CREDENTIAL_TERM_SUBSTRINGS)


def credential_term_to_skill_term(phrase: str) -> str | None:
    """Map credential display text to a platform skill phrase; None means drop."""
    p = _norm_phrase(phrase)
    if not p:
        return None
    for cred, skill in _CREDENTIAL_TO_SKILL:
        if cred in p or p in cred:
            return skill if skill else None
    if "databricks" in p and "lakehouse" in p:
        return "Databricks Lakehouse"
    if "aws" in p and "certified" in p:
        return "AWS"
    if is_credential_competency_term(phrase):
        return None
    return None


def _term_dict(phrase: str, source_fact_id: str, source_fact_ids: list[str] | None = None) -> dict[str, Any]:
    sid = str(source_fact_id or "").strip()
    sids = list(source_fact_ids or ([sid] if sid else []))
    return {
        "text": phrase,
        "source_fact_id": sid,
        "source_fact_ids": sids,
    }


def _find_platform_merge_target(categories: list[dict[str, Any]]) -> dict[str, Any] | None:
    for cat in categories:
        if not isinstance(cat, dict):
            continue
        lab = _norm_label(str(cat.get("category_label") or ""))
        if any(hint in lab for hint in _PLATFORM_MERGE_LABEL_HINTS):
            return cat
    return None


def _merge_terms_into_category(
    target: dict[str, Any],
    new_terms: list[dict[str, Any]],
    *,
    changelog: list[dict[str, Any]],
    from_label: str,
) -> None:
    existing = target.get("terms")
    if not isinstance(existing, list):
        existing = []
    seen = {_norm_phrase(term_phrase(t)) for t in existing if term_phrase(t)}
    added: list[str] = []
    for t in new_terms:
        ph = term_phrase(t)
        if not ph:
            continue
        low = _norm_phrase(ph)
        if low in seen:
            continue
        seen.add(low)
        existing.append(t)
        added.append(ph)
    target["terms"] = existing
    if added:
        changelog.append(
            {
                "operation": "merge_remapped_certification_terms",
                "from_reserved_category": from_label,
                "into_category": target.get("category_label"),
                "terms_added": added,
            }
        )


def sanitize_competencies_no_certification_category(
    competencies: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Remove reserved certification categories; remap credential terms to platform skills."""
    if not isinstance(competencies, list):
        return [], []

    changelog: list[dict[str, Any]] = []
    out: list[dict[str, Any]] = []

    for cat in competencies:
        if not isinstance(cat, dict):
            continue
        label = str(cat.get("category_label") or "").strip()
        terms_raw = cat.get("terms")
        if not isinstance(terms_raw, list):
            terms_raw = []

        if is_reserved_certification_category(label):
            remapped: list[dict[str, Any]] = []
            for raw_t in terms_raw:
                phrase = term_phrase(raw_t) if isinstance(raw_t, dict) else str(raw_t or "").strip()
                skill = credential_term_to_skill_term(phrase)
                if not skill:
                    if phrase:
                        changelog.append(
                            {
                                "operation": "drop_credential_competency_term",
                                "category_label": label,
                                "phrase": phrase,
                                "reason": "reserved_for_certifications_section",
                            }
                        )
                    continue
                fid = ""
                sids: list[str] = []
                if isinstance(raw_t, dict):
                    fid = str(raw_t.get("source_fact_id") or "").strip()
                    sids = [str(x) for x in (raw_t.get("source_fact_ids") or []) if str(x).strip()]
                if not fid and sids:
                    fid = sids[0]
                remapped.append(_term_dict(skill, fid, sids))
            changelog.append(
                {
                    "operation": "remap_reserved_certification_category",
                    "from_category_label": label,
                    "remapped_term_count": len(remapped),
                    "reason": "certifications_reserved_for_dedicated_section",
                }
            )
            if remapped:
                merge_target = _find_platform_merge_target(out)
                if merge_target is not None:
                    _merge_terms_into_category(merge_target, remapped, changelog=changelog, from_label=label)
                else:
                    out.append(
                        {
                            "category_label": _CLOUD_PLATFORM_CATEGORY_LABEL,
                            "terms": remapped,
                            "source_fact_ids": sorted(
                                {
                                    str(x)
                                    for t in remapped
                                    for x in (
                                        (t.get("source_fact_ids") or [])
                                        if isinstance(t, dict)
                                        else []
                                    )
                                }
                            ),
                        }
                    )
            continue

        kept_terms: list[Any] = []
        for raw_t in terms_raw:
            phrase = term_phrase(raw_t) if isinstance(raw_t, dict) else str(raw_t or "").strip()
            if not phrase:
                continue
            if is_credential_competency_term(phrase):
                skill = credential_term_to_skill_term(phrase)
                if not skill:
                    changelog.append(
                        {
                            "operation": "drop_credential_competency_term",
                            "category_label": label,
                            "phrase": phrase,
                            "reason": "credential_name_not_competency_term",
                        }
                    )
                    continue
                fid = ""
                sids: list[str] = []
                if isinstance(raw_t, dict):
                    fid = str(raw_t.get("source_fact_id") or "").strip()
                    sids = [str(x) for x in (raw_t.get("source_fact_ids") or []) if str(x).strip()]
                kept_terms.append(_term_dict(skill, fid, sids))
                changelog.append(
                    {
                        "operation": "rewrite_credential_term_to_platform_skill",
                        "category_label": label,
                        "from_phrase": phrase,
                        "to_phrase": skill,
                    }
                )
                continue
            kept_terms.append(raw_t)

        new_cat = dict(cat)
        new_cat["terms"] = kept_terms
        out.append(new_cat)

    return out, changelog


def check_competencies_no_reserved_certification_category(
    competencies: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    if not isinstance(competencies, list):
        return False, "competencies_not_list"
    for i, cat in enumerate(competencies):
        if not isinstance(cat, dict):
            continue
        label = str(cat.get("category_label") or "").strip()
        if is_reserved_certification_category(label):
            return False, f"reserved_category_label idx={i} label={label!r}"
        for raw_t in cat.get("terms") or []:
            phrase = term_phrase(raw_t) if isinstance(raw_t, dict) else str(raw_t or "")
            if is_credential_competency_term(phrase):
                return False, f"credential_term_in_competencies idx={i} phrase={phrase!r}"
    return True, None


__all__ = [
    "RESERVED_CERTIFICATION_CATEGORY_LABELS",
    "check_competencies_no_reserved_certification_category",
    "credential_term_to_skill_term",
    "is_credential_competency_term",
    "is_reserved_certification_category",
    "sanitize_competencies_no_certification_category",
]
