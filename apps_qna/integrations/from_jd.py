"""Markdown JD -> JobDescription adapter.

Splits a JD .md file on `## Heading` (H2) boundaries; everything before the
first H2 becomes a synthetic "Overview" section. Each section's body is the
text up to the next H2; extracted_keywords is a heuristic pull of capitalized
multi-word phrases plus the bullets directly under the heading.
"""

from __future__ import annotations

import re
from pathlib import Path

from apps_qna.types.qna_types import JDSection, JobDescription

_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*$", re.MULTILINE)
_CAP_PHRASE_RE = re.compile(
    r"\b(?:[A-Z][A-Za-z0-9+/.-]*(?:\s+[A-Z][A-Za-z0-9+/.-]*){0,3})\b"
)
_STOP_PHRASES: frozenset[str] = frozenset(
    {"The", "A", "An", "We", "You", "Our", "Your", "I"}
)


def _extract_keywords(body: str, max_keywords: int = 6) -> list[str]:
    """Heuristic keyword extraction: bullet leads + capitalized phrases."""
    keywords: list[str] = []
    seen: set[str] = set()

    # 1) Lead noun phrase from each bullet (first few words before first comma).
    for match in _BULLET_RE.finditer(body):
        bullet = match.group(1).strip()
        head = bullet.split(",", 1)[0].split(".", 1)[0].strip()
        if head and head.lower() not in seen and len(head) <= 60:
            keywords.append(head)
            seen.add(head.lower())
        if len(keywords) >= max_keywords:
            return keywords

    # 2) Multi-word capitalized phrases as fallback.
    for match in _CAP_PHRASE_RE.finditer(body):
        phrase = match.group(0).strip()
        if (
            phrase in _STOP_PHRASES
            or phrase.lower() in seen
            or " " not in phrase
        ):
            continue
        keywords.append(phrase)
        seen.add(phrase.lower())
        if len(keywords) >= max_keywords:
            break

    return keywords


def parse_markdown_jd(text: str, raw_path: Path | None = None) -> JobDescription:
    """Parse a markdown JD into a JobDescription with H2-split sections."""
    sections: list[JDSection] = []
    h2_matches = list(_H2_RE.finditer(text))
    if not h2_matches:
        # No H2 — single Overview section.
        body = text.strip()
        sections.append(
            JDSection(
                heading="Overview",
                body=body,
                extracted_keywords=_extract_keywords(body),
            )
        )
        return JobDescription(raw_path=raw_path, sections=sections)

    # Pre-H2 lead becomes an Overview if non-empty.
    lead = text[: h2_matches[0].start()].strip()
    if lead:
        sections.append(
            JDSection(
                heading="Overview",
                body=lead,
                extracted_keywords=_extract_keywords(lead),
            )
        )

    for i, m in enumerate(h2_matches):
        heading = m.group(1).strip()
        body_start = m.end()
        body_end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(text)
        body = text[body_start:body_end].strip()
        sections.append(
            JDSection(
                heading=heading,
                body=body,
                extracted_keywords=_extract_keywords(body),
            )
        )

    return JobDescription(raw_path=raw_path, sections=sections)


def load_markdown_jd(path: Path) -> JobDescription:
    """Load and parse a markdown JD file."""
    if not path.is_file():
        raise FileNotFoundError(f"JD file not found: {path}")
    return parse_markdown_jd(path.read_text(encoding="utf-8"), raw_path=path)
