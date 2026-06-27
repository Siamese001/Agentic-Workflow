"""Frontier-era targeting briefing contract + validator.

This module intentionally keeps the old import path because legacy
apps_research/apps_rg bridge code still imports it. The contract validates a
reviewed briefing artifact whose job is to add company/contact signal that
complements the JD while remaining targeting-only context for apps_rg and
apps_lic.

The semantic gate is stricter whenever the JD implies role-relevant evidence:
required source families and signal terms must come from sourced research or
final brief text, and JD text alone cannot satisfy sourced evidence.
"""

from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from apps_research.types.jd_intent_coverage import (
    infer_evidence_intents_from_text,
    intent_ids,
    required_families_for_intents,
    signal_terms_for_intents,
)

@dataclass(frozen=True)
class BriefingProfile:
    """Budget and structure policy for a briefing consumer."""

    profile_id: str
    max_total_chars: int
    target_chars_low: int
    target_chars_high: int
    max_bullets: int
    max_line_chars: int
    min_section_count: int


BRIEFING_PROFILES: dict[str, BriefingProfile] = {
    "apps_rg": BriefingProfile(
        profile_id="apps_rg",
        max_total_chars=8000,
        target_chars_low=4000,
        target_chars_high=6500,
        max_bullets=48,
        max_line_chars=240,
        min_section_count=4,
    ),
    "apps_lic": BriefingProfile(
        profile_id="apps_lic",
        max_total_chars=2500,
        target_chars_low=1000,
        target_chars_high=2000,
        max_bullets=24,
        max_line_chars=220,
        min_section_count=3,
    ),
}

DEFAULT_BRIEFING_PROFILE = "apps_rg"

MAX_TOTAL_CHARS = BRIEFING_PROFILES[DEFAULT_BRIEFING_PROFILE].max_total_chars
TARGET_CHARS_LOW = BRIEFING_PROFILES[DEFAULT_BRIEFING_PROFILE].target_chars_low
TARGET_CHARS_HIGH = BRIEFING_PROFILES[DEFAULT_BRIEFING_PROFILE].target_chars_high
MAX_BULLETS = BRIEFING_PROFILES[DEFAULT_BRIEFING_PROFILE].max_bullets
MAX_BULLET_CHARS = BRIEFING_PROFILES[DEFAULT_BRIEFING_PROFILE].max_line_chars

_CODE_FENCE_RE = re.compile(r"```")
_LINK_RE = re.compile(r"https?://|\]\(", re.IGNORECASE)
_HTML_ENTITY_RE = re.compile(r"&#?\w+;")
_BRACKET_PLACEHOLDER_RE = re.compile(r"\[[A-Z][A-Z0-9 _/]{2,}\]")
_CITATION_RE = re.compile(r"\[\d+\]|\(\s*(?:source|src|ref)[:\s]", re.IGNORECASE)
_SOURCE_NOTE_RE = re.compile(r"^\s*(?:source[s]?|citation[s]?|references?)\s*[:\-]", re.IGNORECASE)
_SUB_BULLET_RE = re.compile(r"^\s+[-*]\s")
_TABLE_PIPE_RE = re.compile(r"\|")
_BULLET_RE = re.compile(r"^- ")
_HEADER_RE = re.compile(r"^(?:#{1,3}\s+.+|===\s*.+?\s*===)$")
_TITLE_LINE_RE = re.compile(r"\bbrief(?:ing)?\b", re.IGNORECASE)

_SIGNAL_TERMS = (
    "strategy",
    "mandate",
    "pressure",
    "operating model",
    "operating-model",
    "decision rights",
    "roadmap",
    "forward",
    "forward-looking",
    "prospective",
    "future",
    "leadership",
    "stakeholder",
    "platform",
    "architecture",
    "data",
    "ai",
    "recent",
    "event",
    "urgency",
    "outreach",
    "positioning",
    "jd complement",
    "role complement",
)

_APPS_RG_REQUIRED_SECTIONS = (
    "jd complement",
    "company dna & operating model",
    "company strategy & operating pressure",
    "leadership & stakeholder map",
    "ai, data, platform, architecture signals",
    "partnership / ecosystem motion",
    "recent events & urgency",
    "apps_rg positioning themes",
    "apps_lic outreach angles",
    "do not use as proof",
)

# Source-family aliases are intentionally conservative. Generic role_context no
# longer satisfies role-specific evidence families; those must be retrieved as
# explicit source families.
_SOURCE_FAMILY_ALIASES = {
    "company_basics": ("overview",),
    "competitive_landscape": ("strategic_priorities",),
    "leadership_and_org": ("leadership",),
    "recent_news_and_signals": ("recent_moves",),
    "financials_and_growth": ("financials_and_growth",),
    "role_context": ("role_context",),
    "partner_ecosystem": ("partner_ecosystem",),
    "commercial_motion": ("commercial_motion",),
    "adoption_motion": ("adoption_motion",),
    "regulatory_and_legal": ("regulatory_and_legal",),
    "tech_stack_and_tools": ("tech_stack_signals",),
    "tech_stack": ("tech_stack_signals",),
}


class BriefStatus(str, Enum):
    """Disposition of a targeting-brief validation/seal attempt."""

    SEALED = "SEALED"
    REJECTED = "REJECTED"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class TargetingBriefValidation:
    """Result of validating a candidate briefing artifact."""

    valid: bool
    char_count: int
    bullet_count: int
    section_count: int = 0
    profile: str = DEFAULT_BRIEFING_PROFILE
    violations: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "char_count": self.char_count,
            "bullet_count": self.bullet_count,
            "section_count": self.section_count,
            "profile": self.profile,
            "violations": list(self.violations),
        }


@dataclass(frozen=True)
class BriefingSemanticsAssessment:
    """Semantic quality gate for apps_rg-targeting briefs."""

    score: float
    profile: str = DEFAULT_BRIEFING_PROFILE
    role_archetype: str = "general"
    required_sections_present: tuple[str, ...] = ()
    missing_sections: tuple[str, ...] = ()
    source_families_present: tuple[str, ...] = ()
    source_families_missing: tuple[str, ...] = ()
    signal_terms_present: tuple[str, ...] = ()
    signal_terms_missing: tuple[str, ...] = ()
    evidence_intents: tuple[str, ...] = ()
    handoff_eligible: bool = False
    judge_name: str = "gemini-pro-3.1-preview"
    judge_model: str = "gemini-3.1-pro-preview"
    reason: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "profile": self.profile,
            "role_archetype": self.role_archetype,
            "required_sections_present": list(self.required_sections_present),
            "missing_sections": list(self.missing_sections),
            "source_families_present": list(self.source_families_present),
            "source_families_missing": list(self.source_families_missing),
            "signal_terms_present": list(self.signal_terms_present),
            "signal_terms_missing": list(self.signal_terms_missing),
            "evidence_intents": list(self.evidence_intents),
            "handoff_eligible": self.handoff_eligible,
            "judge_name": self.judge_name,
            "judge_model": self.judge_model,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class AppsRgTargetingBrief:
    """Sealed targeting brief artifact.

    ``company_brief_text`` is targeting context only. It must not be treated as
    resume proof or as source support for candidate claims.
    """

    status: BriefStatus
    company_name: str
    company_brief_text: str = ""
    char_count: int = 0
    bullet_count: int = 0
    section_count: int = 0
    profile: str = DEFAULT_BRIEFING_PROFILE
    violations: tuple[str, ...] = ()
    block_reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_sealed(self) -> bool:
        return self.status is BriefStatus.SEALED and bool(self.company_brief_text.strip())

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "company_name": self.company_name,
            "company_brief_text": self.company_brief_text,
            "char_count": self.char_count,
            "bullet_count": self.bullet_count,
            "section_count": self.section_count,
            "profile": self.profile,
            "violations": list(self.violations),
            "block_reason": self.block_reason,
            "metadata": dict(self.metadata),
        }


def _resolve_profile(profile: str | None) -> BriefingProfile:
    key = str(profile or DEFAULT_BRIEFING_PROFILE).strip().lower()
    if key not in BRIEFING_PROFILES:
        return BRIEFING_PROFILES[DEFAULT_BRIEFING_PROFILE]
    return BRIEFING_PROFILES[key]


def _jd_restatement_tokens(jd_text: str) -> set[str]:
    """Return salient 4-gram JD phrases for verbatim-copy detection."""

    tokens: set[str] = set()
    for raw_line in (jd_text or "").splitlines():
        line = raw_line.strip().lower()
        if len(line) < 12:
            continue
        words = re.findall(r"[a-z0-9]+", line)
        for i in range(len(words) - 3):
            phrase = " ".join(words[i : i + 4])
            if len(phrase) >= 12:
                tokens.add(phrase)
    return tokens


def _plain_header_text(line: str) -> str:
    s = line.strip()
    s = re.sub(r"^#{1,3}\s*", "", s)
    s = re.sub(r"^===\s*|\s*===$", "", s)
    return s.strip().lower()


def _squash_blank_lines(lines: list[str]) -> list[str]:
    squashed: list[str] = []
    previous_blank = False
    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            if previous_blank:
                continue
            squashed.append("")
            previous_blank = True
            continue
        squashed.append(line)
        previous_blank = False

    while squashed and not squashed[0].strip():
        squashed.pop(0)
    while squashed and not squashed[-1].strip():
        squashed.pop()
    return squashed


def _normalize_brief_lines(body: str, *, cfg: BriefingProfile) -> str:
    lines = (body or "").strip().splitlines()
    normalized: list[str] = []
    previous_was_bullet = False

    for raw in lines:
        stripped = raw.rstrip()
        line = stripped.strip()
        if not line:
            normalized.append("")
            previous_was_bullet = False
            continue
        if _HEADER_RE.match(line):
            normalized.append(line)
            previous_was_bullet = False
            continue
        if line.startswith("|") and line.endswith("|"):
            normalized.append(line)
            previous_was_bullet = False
            continue
        if raw[:1].isspace() and previous_was_bullet:
            normalized.append(stripped)
            continue
        if line.startswith("- "):
            bullet = line[2:].strip()
            wrapped = textwrap.fill(
                bullet,
                width=cfg.max_line_chars,
                initial_indent="- ",
                subsequent_indent="  ",
                break_long_words=False,
                break_on_hyphens=False,
            )
            normalized.extend(wrapped.splitlines())
            previous_was_bullet = True
            continue
        if len(line) > cfg.max_line_chars:
            wrapped = textwrap.fill(
                line,
                width=cfg.max_line_chars,
                break_long_words=False,
                break_on_hyphens=False,
            )
            normalized.extend(wrapped.splitlines())
        else:
            normalized.append(line)
        previous_was_bullet = False

    return "\n".join(_squash_blank_lines(normalized))


def normalize_markdown_brief_text(text: str, *, profile: str = DEFAULT_BRIEFING_PROFILE) -> str:
    """Return a contract-friendly markdown draft with wrapped lines."""

    cfg = _resolve_profile(profile)
    return _normalize_brief_lines(text, cfg=cfg)


def normalize_targeting_brief_text(
    text: str,
    *,
    jd_text: str = "",
    profile: str = DEFAULT_BRIEFING_PROFILE,
) -> str:
    """Return a targeting-brief draft normalized for seal validation."""

    cfg = _resolve_profile(profile)
    return _normalize_brief_lines(text, cfg=cfg)


def validate_targeting_brief_text(
    text: str,
    *,
    jd_text: str = "",
    profile: str = DEFAULT_BRIEFING_PROFILE,
) -> TargetingBriefValidation:
    """Validate a briefing artifact for profile-specific downstream use."""

    cfg = _resolve_profile(profile)
    violations: list[str] = []
    body = (text or "").strip()
    char_count = len(body)

    if not body:
        return TargetingBriefValidation(
            valid=False,
            char_count=0,
            bullet_count=0,
            section_count=0,
            profile=cfg.profile_id,
            violations=("empty_brief",),
        )

    if char_count > cfg.max_total_chars:
        violations.append(f"char_count_over_max:{char_count}>{cfg.max_total_chars}")
    if _CODE_FENCE_RE.search(body):
        violations.append("code_fence_present")
    if _HTML_ENTITY_RE.search(body):
        violations.append("html_entity_present")

    stripped = body.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        violations.append("json_literal_present")

    lines = body.splitlines()
    bullet_lines: list[str] = []
    section_headers: list[str] = []
    metadata_line_idx = -1
    counted_title_line = False
    for idx, raw in enumerate(lines):
        line = raw.rstrip()
        stripped_line = line.strip()
        if metadata_line_idx < 0 and stripped_line.startswith("|") and stripped_line.endswith("|"):
            metadata_line_idx = idx
            continue
        if not stripped_line:
            continue
        if _HEADER_RE.match(stripped_line):
            section_headers.append(stripped_line)
            continue
        if (
            not counted_title_line
            and idx == 0
            and not stripped_line.startswith("-")
            and not stripped_line.startswith("|")
            and _TITLE_LINE_RE.search(stripped_line)
        ):
            section_headers.append(stripped_line)
            counted_title_line = True
            continue
        if _TABLE_PIPE_RE.search(line) and idx != metadata_line_idx:
            violations.append("table_pipe_present")
        if _SUB_BULLET_RE.match(raw):
            violations.append("sub_bullet_present")
        if _SOURCE_NOTE_RE.match(line):
            violations.append("source_note_present")
        if _BULLET_RE.match(line):
            bullet_lines.append(line)
        if len(stripped_line) > cfg.max_line_chars:
            violations.append(f"line_too_long:{len(stripped_line)}>{cfg.max_line_chars}")

    jd_tokens = _jd_restatement_tokens(jd_text) if jd_text else set()
    for bullet in bullet_lines:
        content = bullet[2:]
        if _LINK_RE.search(content):
            violations.append("link_present")
        if _CITATION_RE.search(content):
            violations.append("citation_present")
        if _BRACKET_PLACEHOLDER_RE.search(content):
            violations.append("bracket_placeholder_present")
        if jd_tokens:
            low = content.lower()
            words = re.findall(r"[a-z0-9]+", low)
            for i in range(len(words) - 3):
                phrase = " ".join(words[i : i + 4])
                if phrase in jd_tokens:
                    violations.append("jd_restatement_in_bullet")
                    snippet = re.sub(r"\s+", " ", content).strip()[:140]
                    if snippet:
                        violations.append(f"jd_restatement_in_bullet_text:{snippet}")
                    break

    bullet_count = len(bullet_lines)
    if bullet_count > cfg.max_bullets:
        violations.append(f"too_many_bullets:{bullet_count}>{cfg.max_bullets}")

    section_count = len(section_headers)
    if section_count < cfg.min_section_count:
        violations.append(f"too_few_sections:{section_count}<{cfg.min_section_count}")

    header_blob = " ".join(_plain_header_text(h) for h in section_headers)
    if section_headers and not any(term in header_blob for term in _SIGNAL_TERMS):
        violations.append("no_additive_signal_sections")

    if _LINK_RE.search(body):
        violations.append("link_present")
    if _CITATION_RE.search(body):
        violations.append("citation_present")
    if _BRACKET_PLACEHOLDER_RE.search(body):
        violations.append("bracket_placeholder_present")

    seen: set[str] = set()
    deduped = tuple(v for v in violations if not (v in seen or seen.add(v)))
    return TargetingBriefValidation(
        valid=not deduped,
        char_count=char_count,
        bullet_count=bullet_count,
        section_count=section_count,
        profile=cfg.profile_id,
        violations=deduped,
    )


def _section_headers(text: str) -> list[str]:
    headers: list[str] = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if _HEADER_RE.match(line):
            headers.append(_plain_header_text(line))
    return headers


def _research_families(research_notes: str) -> tuple[str, ...]:
    families: list[str] = []
    for raw in (research_notes or "").splitlines():
        line = raw.strip()
        if not line.startswith("### "):
            continue
        family = line[4:].strip().lower()
        for normalized in _SOURCE_FAMILY_ALIASES.get(family, (family,)):
            if normalized and normalized not in families:
                families.append(normalized)
    return tuple(families)


def _semantic_family_name(family: str) -> str:
    aliases = _SOURCE_FAMILY_ALIASES.get(family, (family,))
    return aliases[0] if aliases else family


def _role_archetype_from_jd(jd_text: str) -> str:
    intents = intent_ids(infer_evidence_intents_from_text(jd_text))
    return intents[0] if intents else "general"


def assess_targeting_brief_semantics(
    text: str,
    *,
    jd_text: str = "",
    research_notes: str = "",
    profile: str = DEFAULT_BRIEFING_PROFILE,
) -> BriefingSemanticsAssessment:
    """Assess whether the brief is dense enough to hand off to apps_rg.

    Important: JD text may identify role archetype and required evidence, but
    JD text does not satisfy sourced signal terms. Signal terms are detected
    only in the final brief and research notes.
    """

    cfg = _resolve_profile(profile)
    body = (text or "").strip()
    intents = infer_evidence_intents_from_text(jd_text)
    evidence_intents = intent_ids(intents)
    role_archetype = evidence_intents[0] if evidence_intents else "general"
    if not body:
        return BriefingSemanticsAssessment(
            score=0.0,
            profile=cfg.profile_id,
            role_archetype=role_archetype,
            evidence_intents=evidence_intents,
            reason="empty_brief",
        )

    headers = _section_headers(body)
    header_blob = " ".join(headers)
    required_sections = tuple(_APPS_RG_REQUIRED_SECTIONS)
    required_present = tuple(section for section in required_sections if section in header_blob)
    missing_sections = tuple(section for section in required_sections if section not in header_blob)

    source_families = _research_families(research_notes)
    base_required_families = ("overview", "strategic_priorities", "leadership", "recent_moves")
    intent_required_families = tuple(
        dict.fromkeys(_semantic_family_name(fam) for fam in required_families_for_intents(intents))
    )
    required_families = list(dict.fromkeys((*base_required_families, *intent_required_families)))
    source_families_present = tuple(fam for fam in required_families if fam in source_families)
    source_families_missing = tuple(fam for fam in required_families if fam not in source_families)

    body_and_research_blob = f"{body}\n{research_notes}".lower()
    research_blob = (research_notes or "").lower()
    base_signal_terms = ("company dna", "operating model", "leadership", "strategy", "urgency")
    signal_terms = list(base_signal_terms)
    intent_signal_terms = signal_terms_for_intents(intents)
    signal_terms.extend(intent_signal_terms)
    unique_signal_terms = tuple(dict.fromkeys(signal_terms))
    signal_terms_present = tuple(term for term in unique_signal_terms if term in body_and_research_blob)
    signal_terms_missing = tuple(term for term in unique_signal_terms if term not in body_and_research_blob)
    base_signal_terms_missing = tuple(term for term in base_signal_terms if term not in body_and_research_blob)

    intent_families_missing = tuple(fam for fam in intent_required_families if fam not in source_families)
    missing_intent_signals = tuple(
        intent.intent_id
        for intent in intents
        if intent.signal_terms and not any(term in research_blob for term in intent.signal_terms)
    )

    score = 1.0
    score -= 0.10 * len(missing_sections)
    score -= 0.08 * len(source_families_missing)
    score -= 0.04 * len(base_signal_terms_missing)
    if len(required_present) < max(6, len(required_sections) - 2):
        score -= 0.08
    if len(source_families_present) < len(base_required_families):
        score -= 0.08
    if intent_families_missing:
        score -= 0.12 * len(intent_families_missing)
    if missing_intent_signals:
        score -= 0.12 * len(missing_intent_signals)
    score = max(0.0, min(1.0, round(score, 3)))

    handoff_eligible = (
        score >= 0.72
        and len(missing_sections) == 0
        and len(source_families_missing) <= 1
        and "company dna" in body_and_research_blob
    )
    if intents:
        handoff_eligible = (
            score >= 0.75
            and len(missing_sections) == 0
            and not intent_families_missing
            and not missing_intent_signals
            and "company dna" in body_and_research_blob
        )

    reason = ""
    if not handoff_eligible:
        reason = ",".join(
            x
            for x in (
                "missing_sections" if missing_sections else "",
                "missing_source_families" if source_families_missing else "",
                "missing_signal_terms" if base_signal_terms_missing else "",
                "missing_intent_evidence" if intent_families_missing else "",
                "missing_sourced_intent_signal" if missing_intent_signals else "",
            )
            if x
        ) or "semantic_score_below_threshold"

    return BriefingSemanticsAssessment(
        score=score,
        profile=cfg.profile_id,
        role_archetype=role_archetype,
        required_sections_present=required_present,
        missing_sections=missing_sections,
        source_families_present=source_families_present,
        source_families_missing=source_families_missing,
        signal_terms_present=signal_terms_present,
        signal_terms_missing=signal_terms_missing,
        evidence_intents=evidence_intents,
        handoff_eligible=handoff_eligible,
        reason=reason,
    )


def seal_targeting_brief(
    text: str,
    *,
    company_name: str,
    jd_text: str = "",
    profile: str = DEFAULT_BRIEFING_PROFILE,
    metadata: dict[str, Any] | None = None,
) -> AppsRgTargetingBrief:
    """Validate and seal a candidate briefing, or return a non-sealed artifact."""

    cfg = _resolve_profile(profile)
    body = (text or "").strip()
    if not body:
        return AppsRgTargetingBrief(
            status=BriefStatus.BLOCKED,
            company_name=company_name,
            profile=cfg.profile_id,
            block_reason="empty_company_brief_text",
            metadata=dict(metadata or {}),
        )
    result = validate_targeting_brief_text(body, jd_text=jd_text, profile=cfg.profile_id)
    if not result.valid:
        return AppsRgTargetingBrief(
            status=BriefStatus.REJECTED,
            company_name=company_name,
            char_count=result.char_count,
            bullet_count=result.bullet_count,
            section_count=result.section_count,
            profile=cfg.profile_id,
            violations=result.violations,
            block_reason="contract_validation_failed",
            metadata=dict(metadata or {}),
        )
    return AppsRgTargetingBrief(
        status=BriefStatus.SEALED,
        company_name=company_name,
        company_brief_text=body,
        char_count=result.char_count,
        bullet_count=result.bullet_count,
        section_count=result.section_count,
        profile=cfg.profile_id,
        metadata=dict(metadata or {}),
    )


def blocked_targeting_brief(
    *,
    company_name: str,
    block_reason: str,
    degraded: bool = False,
    profile: str = DEFAULT_BRIEFING_PROFILE,
    metadata: dict[str, Any] | None = None,
) -> AppsRgTargetingBrief:
    """Construct a non-usable blocked/degraded artifact."""

    cfg = _resolve_profile(profile)
    return AppsRgTargetingBrief(
        status=BriefStatus.DEGRADED if degraded else BriefStatus.BLOCKED,
        company_name=company_name,
        profile=cfg.profile_id,
        block_reason=block_reason,
        metadata=dict(metadata or {}),
    )


__all__ = [
    "BRIEFING_PROFILES",
    "DEFAULT_BRIEFING_PROFILE",
    "MAX_BULLETS",
    "MAX_BULLET_CHARS",
    "MAX_TOTAL_CHARS",
    "TARGET_CHARS_HIGH",
    "TARGET_CHARS_LOW",
    "AppsRgTargetingBrief",
    "BriefStatus",
    "BriefingProfile",
    "BriefingSemanticsAssessment",
    "TargetingBriefValidation",
    "blocked_targeting_brief",
    "assess_targeting_brief_semantics",
    "normalize_markdown_brief_text",
    "normalize_targeting_brief_text",
    "seal_targeting_brief",
    "validate_targeting_brief_text",
]
