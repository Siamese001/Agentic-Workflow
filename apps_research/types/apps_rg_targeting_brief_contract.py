"""Route-specific AppsRgTargetingBrief contract + validator.

This contract is **distinct** from the JSON ``CompanyBrief`` schema
(``apps_rg/schemas/company_research.schema.json``). The default
apps_research company-brief route still produces structured JSON with
citations; the apps_rg targeting route instead produces a sealed plain
markdown/text artifact (``company_brief_text``) suitable for direct
consumption as a delegated manual_brief in apps_rg.

Why a separate contract
------------------------
- apps_rg consumes ``company_brief_text`` as plain text — no JSON, no
  citation anchors, no source register.
- The external app record (``AppsRgTargetingBrief``) may be structured for
  provenance, but ``company_brief_text`` must validate as plain markdown.

Hard validation rules (fail-closed)
-----------------------------------
- ``company_brief_text`` length <= 2400 chars (target 1700-1900).
- <= 17 total ``- `` bullets.
- Each bullet is a single line and < 90 chars.
- Only the allowed section headers may appear.
- No JSON, code fences, citations, links, source notes, tables,
  sub-bullets, escaped HTML entities, or bracket placeholders.
- JD facts may not be restated except on the single metadata line.

A brief that fails any rule is **rejected** — the caller must surface a
sealed BLOCKED/DEGRADED artifact, never a placeholder or generic brief.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_TOTAL_CHARS = 2400
TARGET_CHARS_LOW = 1700
TARGET_CHARS_HIGH = 1900
MAX_BULLETS = 17
MAX_BULLET_CHARS = 90  # strict: each bullet must be < 90 chars

# Allowed section headers (the chosen-domain header is one of three variants).
_FIXED_HEADERS = frozenset(
    {
        "=== STRATEGIC MANDATE ===",
        "=== LEADERSHIP ===",
        "=== BUSINESS CONTEXT (JD alignment hooks) ===",
        "=== EXEC SUMMARY FRAMING (not proof) ===",
    }
)
_DOMAIN_HEADERS = frozenset(
    {
        "=== EA, DATA & M&A ===",
        "=== TECH & AI PLATFORM ===",
        "=== FINANCIALS & TRAJECTORY ===",
    }
)
ALLOWED_HEADERS = _FIXED_HEADERS | _DOMAIN_HEADERS

# Forbidden-content detectors.
_CODE_FENCE_RE = re.compile(r"```")
_LINK_RE = re.compile(r"https?://|\]\(", re.IGNORECASE)
_HTML_ENTITY_RE = re.compile(r"&#?\w+;")
_BRACKET_PLACEHOLDER_RE = re.compile(r"\[[A-Z][A-Z0-9 _/]{2,}\]")  # [ROLE_TITLE], [TICKER]
_CITATION_RE = re.compile(r"\[\d+\]|\(\s*(?:source|src|ref)[:\s]", re.IGNORECASE)
_SOURCE_NOTE_RE = re.compile(r"^\s*(?:source[s]?|citation[s]?|references?)\s*[:\-]", re.IGNORECASE)
_SUB_BULLET_RE = re.compile(r"^\s+[-*]\s")  # indented bullet
_TABLE_PIPE_RE = re.compile(r"\|")
_BULLET_RE = re.compile(r"^- ")


class BriefStatus(str, Enum):
    """Disposition of a targeting-brief validation/seal attempt."""

    SEALED = "SEALED"
    REJECTED = "REJECTED"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class TargetingBriefValidation:
    """Result of validating a candidate ``company_brief_text``."""

    valid: bool
    char_count: int
    bullet_count: int
    violations: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "char_count": self.char_count,
            "bullet_count": self.bullet_count,
            "violations": list(self.violations),
        }


@dataclass(frozen=True)
class AppsRgTargetingBrief:
    """Sealed route-specific targeting brief artifact.

    ``company_brief_text`` is the only field apps_rg consumes; the rest is
    provenance for the external app record. A brief with
    ``status != SEALED`` MUST NOT be treated as a usable briefing.
    """

    status: BriefStatus
    company_name: str
    company_brief_text: str = ""
    char_count: int = 0
    bullet_count: int = 0
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
            "violations": list(self.violations),
            "block_reason": self.block_reason,
            "metadata": dict(self.metadata),
        }


def _jd_restatement_tokens(jd_text: str) -> set[str]:
    """Salient JD tokens used to detect bullet-level JD restatement.

    Returns lowercased multi-word phrases (>= 3 words, length-bounded) drawn
    from the JD body. A targeting bullet that reproduces such a phrase
    verbatim is treated as JD restatement.
    """
    tokens: set[str] = set()
    for raw_line in (jd_text or "").splitlines():
        line = raw_line.strip().lower()
        if len(line) < 12:
            continue
        words = re.findall(r"[a-z0-9]+", line)
        # sliding 4-gram phrases give a strong verbatim-restatement signal
        for i in range(len(words) - 3):
            phrase = " ".join(words[i : i + 4])
            if len(phrase) >= 12:
                tokens.add(phrase)
    return tokens


def validate_targeting_brief_text(
    text: str,
    *,
    jd_text: str = "",
) -> TargetingBriefValidation:
    """Validate a candidate ``company_brief_text`` against the contract.

    ``jd_text`` is optional; when supplied, bullets (not the metadata line)
    that verbatim-restate a salient JD phrase are flagged.
    """
    violations: list[str] = []
    body = (text or "").strip()
    char_count = len(body)

    if not body:
        return TargetingBriefValidation(
            valid=False, char_count=0, bullet_count=0,
            violations=("empty_brief",),
        )

    if char_count > MAX_TOTAL_CHARS:
        violations.append(f"char_count_over_max:{char_count}>{MAX_TOTAL_CHARS}")

    if _CODE_FENCE_RE.search(body):
        violations.append("code_fence_present")
    if _HTML_ENTITY_RE.search(body):
        violations.append("html_entity_present")
    # JSON: an object/array literal spanning the document is forbidden.
    stripped = body.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        violations.append("json_literal_present")

    lines = body.splitlines()
    bullet_lines: list[str] = []
    # The metadata line is the (first) line beginning and ending with "|".
    metadata_line_idx = -1
    for idx, raw in enumerate(lines):
        line = raw.rstrip()
        stripped_line = line.strip()
        if metadata_line_idx < 0 and stripped_line.startswith("|") and stripped_line.endswith("|"):
            metadata_line_idx = idx
            continue
        # Headers must be in the allow-list when they look like headers.
        if stripped_line.startswith("===") or stripped_line.endswith("==="):
            if stripped_line not in ALLOWED_HEADERS:
                violations.append(f"disallowed_header:{stripped_line[:48]}")
            continue
        # Tables (pipes) anywhere other than the metadata line are forbidden.
        if _TABLE_PIPE_RE.search(line) and idx != metadata_line_idx:
            violations.append("table_pipe_present")
        # Sub-bullets (indented bullets) are forbidden.
        if _SUB_BULLET_RE.match(raw):
            violations.append("sub_bullet_present")
        if _SOURCE_NOTE_RE.match(line):
            violations.append("source_note_present")
        if _BULLET_RE.match(line):
            bullet_lines.append(line)

    # Per-bullet checks.
    jd_tokens = _jd_restatement_tokens(jd_text) if jd_text else set()
    for bullet in bullet_lines:
        content = bullet[2:]  # strip leading "- "
        if len(bullet) >= MAX_BULLET_CHARS:
            violations.append(f"bullet_too_long:{len(bullet)}>={MAX_BULLET_CHARS}")
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
    if bullet_count > MAX_BULLETS:
        violations.append(f"too_many_bullets:{bullet_count}>{MAX_BULLETS}")

    # Bracket placeholders anywhere (including metadata line) are forbidden.
    if _BRACKET_PLACEHOLDER_RE.search(body):
        if "bracket_placeholder_present" not in violations:
            violations.append("bracket_placeholder_present")

    # Deduplicate while preserving order.
    seen: set[str] = set()
    deduped = tuple(v for v in violations if not (v in seen or seen.add(v)))
    return TargetingBriefValidation(
        valid=not deduped,
        char_count=char_count,
        bullet_count=bullet_count,
        violations=deduped,
    )


def seal_targeting_brief(
    text: str,
    *,
    company_name: str,
    jd_text: str = "",
    metadata: dict[str, Any] | None = None,
) -> AppsRgTargetingBrief:
    """Validate and seal a candidate brief, or return a REJECTED artifact.

    Never returns a SEALED brief with invalid or empty text. Callers that
    receive a non-sealed brief must propagate BLOCKED/DEGRADED rather than
    substituting a placeholder.
    """
    body = (text or "").strip()
    if not body:
        return AppsRgTargetingBrief(
            status=BriefStatus.BLOCKED,
            company_name=company_name,
            block_reason="empty_company_brief_text",
            metadata=dict(metadata or {}),
        )
    result = validate_targeting_brief_text(body, jd_text=jd_text)
    if not result.valid:
        return AppsRgTargetingBrief(
            status=BriefStatus.REJECTED,
            company_name=company_name,
            char_count=result.char_count,
            bullet_count=result.bullet_count,
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
        metadata=dict(metadata or {}),
    )


def blocked_targeting_brief(
    *,
    company_name: str,
    block_reason: str,
    degraded: bool = False,
    metadata: dict[str, Any] | None = None,
) -> AppsRgTargetingBrief:
    """Construct a sealed rejection/degraded artifact (no usable brief text)."""
    return AppsRgTargetingBrief(
        status=BriefStatus.DEGRADED if degraded else BriefStatus.BLOCKED,
        company_name=company_name,
        block_reason=block_reason,
        metadata=dict(metadata or {}),
    )


__all__ = [
    "ALLOWED_HEADERS",
    "AppsRgTargetingBrief",
    "BriefStatus",
    "MAX_BULLETS",
    "MAX_BULLET_CHARS",
    "MAX_TOTAL_CHARS",
    "TARGET_CHARS_HIGH",
    "TARGET_CHARS_LOW",
    "TargetingBriefValidation",
    "blocked_targeting_brief",
    "seal_targeting_brief",
    "validate_targeting_brief_text",
]
