"""Frontier-era targeting briefing contract + validator.

This module intentionally keeps the old import path because legacy
apps_research/apps_rg bridge code still imports it. The contract itself is no
longer the Qwen-era 2.4k / 17-bullet micro-brief. It validates a reviewed
briefing artifact whose job is to add company/contact signal that complements
the JD while remaining targeting-only context for apps_rg and apps_lic.

The validator rejects artifact shapes that are dangerous downstream:
JSON/code blobs, placeholders, inline citations/links, source notes in the
brief body, and verbatim JD restatement. Size limits are profile-specific so a
rich apps_rg briefing can coexist with a compact apps_lic packet.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


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

_SIGNAL_TERMS = (
    "strategy",
    "mandate",
    "pressure",
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
    "TargetingBriefValidation",
    "blocked_targeting_brief",
    "seal_targeting_brief",
    "validate_targeting_brief_text",
]
