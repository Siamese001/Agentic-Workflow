"""Pure whole-resume measurements over sealed structured artifacts."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import date
from typing import Any, Mapping, Sequence

from .constants import (
    EXPERIENCE_SECTION_SUFFIXES,
    LEADERSHIP_TERMS,
    REQUIRED_SECTION_IDS,
    SCOPE_TERMS,
)

_WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9+.#'-]*")


def _tokens(value: str) -> list[str]:
    return [match.group(0).lower() for match in _WORD_RE.finditer(value)]


def _normalized(value: str) -> str:
    return " ".join(_tokens(value))


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def _parse_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _contains_phrase(text: str, phrase: str) -> bool:
    haystack = _tokens(text)
    needle = _tokens(phrase)
    return bool(needle) and any(
        haystack[index : index + len(needle)] == needle for index in range(len(haystack) - len(needle) + 1)
    )


def _phrase_count(text: str, phrase: str) -> int:
    haystack = _tokens(text)
    needle = _tokens(phrase)
    if not needle:
        return 0
    return sum(
        haystack[index : index + len(needle)] == needle for index in range(len(haystack) - len(needle) + 1)
    )


def _jd_parroting_count(claims: Sequence[Mapping[str, Any]], jd_text: str) -> int:
    jd_tokens = _tokens(jd_text)
    if len(jd_tokens) < 8:
        return 0
    phrases = {" ".join(jd_tokens[index : index + 8]) for index in range(len(jd_tokens) - 7)}
    return sum(
        1
        for claim in claims
        if any(phrase in _normalized(str(claim.get("text") or "")) for phrase in phrases)
    )


def _keyword_insertion_count(
    sections: Sequence[Mapping[str, Any]], concepts: Sequence[Mapping[str, Any]]
) -> int:
    count = 0
    for section in sections:
        text = str(section.get("text") or "")
        for concept in concepts:
            phrase = str(concept.get("text") or "")
            if _phrase_count(text, phrase) > 2:
                count += 1
    return count


def evaluate_resume_artifact(
    artifact: Mapping[str, Any], target_context: Mapping[str, Any]
) -> dict[str, Any]:
    """Calculate deterministic quality metrics for one exact resume artifact."""

    sections = [row for row in artifact.get("sections") or [] if isinstance(row, Mapping)]
    section_ids = [str(row.get("section_id") or "") for row in sections]
    claims = [
        claim for section in sections for claim in section.get("claims") or [] if isinstance(claim, Mapping)
    ]
    material_claims = [claim for claim in claims if claim.get("material") is True]
    grounding_pass = sum(1 for claim in material_claims if claim.get("grounding_status") == "PASS")
    grounding_fail = sum(1 for claim in material_claims if claim.get("grounding_status") == "FAIL")
    grounding_unknown = sum(1 for claim in material_claims if claim.get("grounding_status") == "UNKNOWN")

    fact_values: dict[str, set[str]] = defaultdict(set)
    critical_fact_keys: set[str] = set()
    for claim in material_claims:
        for binding in claim.get("fact_bindings") or []:
            if not isinstance(binding, Mapping):
                continue
            key = str(binding.get("key") or "")
            fact_values[key].add(_normalized(str(binding.get("value") or "")))
            if binding.get("critical") is True:
                critical_fact_keys.add(key)
    inconsistent_fact_keys = sorted(key for key, values in fact_values.items() if key and len(values) > 1)
    critical_inconsistencies = [key for key in inconsistent_fact_keys if key in critical_fact_keys]

    employment_rows = [row for row in artifact.get("employment") or [] if isinstance(row, Mapping)]
    employment_by_id = {str(row.get("employment_id") or ""): row for row in employment_rows}
    chronology_inconsistencies: list[str] = []
    for row in employment_rows:
        employment_id = str(row.get("employment_id") or "")
        start = _parse_date(row.get("start_date"))
        end_value = row.get("end_date")
        end = _parse_date(end_value) if end_value is not None else None
        if start is None or (end_value is not None and end is None):
            chronology_inconsistencies.append(employment_id)
        elif end is not None and start > end:
            chronology_inconsistencies.append(employment_id)

    employer_title_inconsistencies: list[str] = []
    for claim in material_claims:
        employment_id = str(claim.get("employment_id") or "")
        if not employment_id:
            continue
        employment = employment_by_id.get(employment_id)
        if employment is None:
            employer_title_inconsistencies.append(str(claim.get("claim_id") or ""))
            continue
        for field in ("employer_id", "title_id"):
            claim_value = claim.get(field)
            if claim_value is not None and claim_value != employment.get(field):
                employer_title_inconsistencies.append(str(claim.get("claim_id") or ""))
                break

    achievement_ids = [
        str(claim.get("achievement_id") or "")
        for claim in material_claims
        if str(claim.get("achievement_id") or "")
    ]
    duplicate_achievement_count = sum(count - 1 for count in Counter(achievement_ids).values() if count > 1)

    summary_texts = {
        _normalized(str(claim.get("text") or ""))
        for section in sections
        if section.get("section_id") == "executive_summary"
        for claim in section.get("claims") or []
        if isinstance(claim, Mapping)
    }
    experience_texts = {
        _normalized(str(claim.get("text") or ""))
        for section in sections
        if str(section.get("section_id") or "").endswith(EXPERIENCE_SECTION_SUFFIXES)
        for claim in section.get("claims") or []
        if isinstance(claim, Mapping)
    }
    repeated_summary_experience = sorted((summary_texts & experience_texts) - {""})

    concepts = [row for row in target_context.get("jd_concepts") or [] if isinstance(row, Mapping)]
    concept_ids = {str(row.get("concept_id") or "") for row in concepts}
    covered_concepts = {
        str(concept_id)
        for claim in material_claims
        for concept_id in claim.get("jd_concept_ids") or []
        if str(concept_id) in concept_ids
    }
    grounded_covered_concepts = {
        str(concept_id)
        for claim in material_claims
        if claim.get("grounding_status") == "PASS" and claim.get("evidence_refs")
        for concept_id in claim.get("jd_concept_ids") or []
        if str(concept_id) in concept_ids
    }
    relevant_achievements = {str(value) for value in target_context.get("relevant_achievement_ids") or []}
    emitted_achievements = set(achievement_ids)

    section_word_counts = {
        str(section.get("section_id") or ""): len(_tokens(str(section.get("text") or "")))
        for section in sections
    }
    total_words = sum(section_word_counts.values())
    nonempty_counts = [value for value in section_word_counts.values() if value > 0]
    section_balance = (
        round(min(nonempty_counts) / max(nonempty_counts), 6)
        if nonempty_counts and max(nonempty_counts)
        else 0.0
    )
    has_experience = any(section_id.endswith(EXPERIENCE_SECTION_SUFFIXES) for section_id in section_ids)
    ats_structure_pass = (
        len(section_ids) == len(set(section_ids))
        and all(section_id in section_ids for section_id in REQUIRED_SECTION_IDS)
        and has_experience
        and all(section_word_counts.values())
        and "|" not in str(artifact.get("content") or "")
    )

    jd_parroting_count = _jd_parroting_count(material_claims, str(target_context.get("jd_text") or ""))
    keyword_insertion_count = _keyword_insertion_count(sections, concepts)
    unsupported_leadership = sum(
        1
        for claim in material_claims
        if any(_contains_phrase(str(claim.get("text") or ""), term) for term in LEADERSHIP_TERMS)
        and (claim.get("grounding_status") != "PASS" or not claim.get("evidence_refs"))
    )
    unsupported_scope = sum(
        1
        for claim in material_claims
        if any(_contains_phrase(str(claim.get("text") or ""), term) for term in SCOPE_TERMS)
        and (claim.get("grounding_status") != "PASS" or not claim.get("evidence_refs"))
    )

    failure_codes: list[str] = []
    unknown_reasons: list[str] = []
    if not material_claims:
        unknown_reasons.append("material claim inventory is empty")
    if grounding_unknown:
        unknown_reasons.append("one or more material claims have UNKNOWN grounding")
    if grounding_fail:
        failure_codes.append("MATERIAL_CLAIM_GROUNDING_NONPASS")
    if critical_inconsistencies:
        failure_codes.append("CRITICAL_CROSS_SECTION_INCONSISTENCY")
    if chronology_inconsistencies:
        failure_codes.append("CHRONOLOGY_INCONSISTENCY")
    if employer_title_inconsistencies:
        failure_codes.append("EMPLOYER_TITLE_INCONSISTENCY")
    if duplicate_achievement_count:
        failure_codes.append("DUPLICATE_ACHIEVEMENT")
    if repeated_summary_experience:
        failure_codes.append("SUMMARY_EXPERIENCE_REPETITION")
    if not ats_structure_pass:
        failure_codes.append("ATS_STRUCTURE_NONPASS")
    if jd_parroting_count:
        failure_codes.append("JD_PARROTING_RISK")
    if keyword_insertion_count:
        failure_codes.append("UNNATURAL_KEYWORD_INSERTION")
    if unsupported_leadership:
        failure_codes.append("UNSUPPORTED_LEADERSHIP_INFLATION")
    if unsupported_scope:
        failure_codes.append("UNSUPPORTED_SCOPE_INFLATION")

    metrics = {
        "material_claim_grounding_rate": _ratio(grounding_pass, len(material_claims)),
        "critical_cross_section_inconsistency_count": len(critical_inconsistencies),
        "chronology_inconsistency_count": len(chronology_inconsistencies),
        "employer_title_inconsistency_count": len(employer_title_inconsistencies),
        "duplicate_achievement_rate": (_ratio(duplicate_achievement_count, len(achievement_ids)) or 0.0),
        "summary_experience_repetition_rate": (
            _ratio(len(repeated_summary_experience), len(summary_texts)) or 0.0
        ),
        "jd_concept_coverage": _ratio(len(covered_concepts), len(concept_ids)),
        "relevant_achievement_coverage": _ratio(
            len(relevant_achievements & emitted_achievements),
            len(relevant_achievements),
        ),
        "section_balance_score": section_balance,
        "resume_word_count": total_words,
        "claim_density_per_100_words": (
            round(len(material_claims) * 100 / total_words, 6) if total_words else None
        ),
        "ats_structure_pass": ats_structure_pass,
        "evidence_backed_personalization": _ratio(len(grounded_covered_concepts), len(concept_ids)),
        "jd_parroting_risk_count": jd_parroting_count,
        "unnatural_keyword_insertion_count": keyword_insertion_count,
        "unsupported_leadership_inflation_count": unsupported_leadership,
        "unsupported_scope_inflation_count": unsupported_scope,
    }
    status = "UNKNOWN" if unknown_reasons else ("FAIL" if failure_codes else "PASS")
    return {
        "artifact_id": str(artifact.get("artifact_id") or ""),
        "status": status,
        "metrics": metrics,
        "material_defect_count": len(set(failure_codes)),
        "failure_codes": sorted(set(failure_codes)),
        "unknown_reasons": sorted(set(unknown_reasons)),
        "diagnostics": {
            "inconsistent_fact_keys": inconsistent_fact_keys,
            "critical_inconsistent_fact_keys": critical_inconsistencies,
            "chronology_inconsistency_ids": sorted(set(chronology_inconsistencies)),
            "employer_title_inconsistency_claim_ids": sorted(set(employer_title_inconsistencies)),
            "repeated_summary_experience_claims": repeated_summary_experience,
        },
    }


__all__ = ["evaluate_resume_artifact"]
