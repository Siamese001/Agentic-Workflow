"""PDF / Markdown research-briefing -> ResearchInputs adapter.

Heuristic, **no LLM**. The brief is parsed by section heading; sections with
recognized titles are mapped onto ResearchInputs fields. Unmatched sections
are appended to `company_brief` so no content is lost.

Section heuristics (case-insensitive substring match in order; first wins):

| Heading contains            | Maps to                       |
|-----------------------------|-------------------------------|
| "executive summary"         | company_brief                 |
| "company" / "organization"  | company_brief (appended)      |
| "role" / "position"         | role_areas_of_focus (bullets) |
| "trend" / "industry"        | industry_trends (bullets)     |
| "interviewer" / "lens"      | interviewer_lenses (entry)    |
| "glossary" / "terms"        | glossary_entries (parsed)     |
| "source" / "citation"       | source_register (parsed lines)|

This is "good enough to scaffold". The operator reviews the produced YAML
and refines before building.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from apps_qna.types.qna_types import (
    GlossaryEntry,
    ResearchClaim,
    ResearchInputs,
)

_BULLET_RE = re.compile(r"^\s*[-•*]\s+(.+?)\s*$", re.MULTILINE)
_HEADING_HINTS: list[tuple[str, str]] = [
    ("executive summary", "company_brief_primary"),
    ("company overview", "company_brief"),
    ("organization", "company_brief"),
    ("about the company", "company_brief"),
    ("role areas of focus", "role_areas"),
    ("areas of focus", "role_areas"),
    ("role", "role_areas"),
    ("position", "role_areas"),
    ("industry trend", "trends"),
    ("market trend", "trends"),
    ("trends", "trends"),
    ("industry", "trends"),
    ("interviewer", "interviewer"),
    ("lens", "interviewer"),
    ("glossary", "glossary"),
    ("terminology", "glossary"),
    ("source register", "sources"),
    ("citations", "sources"),
    ("references", "sources"),
]


def _classify_heading(heading: str) -> str | None:
    h = heading.lower().strip()
    for hint, target in _HEADING_HINTS:
        if hint in h:
            return target
    return None


def _bullets(text: str) -> list[str]:
    return [m.group(1).strip() for m in _BULLET_RE.finditer(text)]


def _glossary_from_text(text: str) -> list[GlossaryEntry]:
    """Parse `Term: definition` or `Term — definition` rows into GlossaryEntry."""
    entries: list[GlossaryEntry] = []
    for line in text.splitlines():
        line = line.strip().lstrip("-•* ").strip()
        if not line:
            continue
        # Match `term: definition` or `term — definition` or `term - definition`
        match = re.match(r"^([A-Z][\w\s/&-]{1,40}?)\s*[:\u2014\u2013-]\s*(.+)$", line)
        if match:
            term, defn = match.group(1).strip(), match.group(2).strip()
            entries.append(GlossaryEntry(term=term, definition=defn))
    return entries


def _sources_from_text(text: str) -> list[ResearchClaim]:
    """Parse `[SRC-NNN] claim text` lines into ResearchClaim."""
    claims: list[ResearchClaim] = []
    for line in text.splitlines():
        line = line.strip().lstrip("-•* ").strip()
        match = re.match(r"^\[?(SRC-[\w-]+)\]?\s*[:\u2014-]?\s*(.+)$", line)
        if match:
            claims.append(
                ResearchClaim(
                    claim=match.group(2).strip(),
                    claim_type="direct_evidence",
                    source_id=match.group(1).strip(),
                )
            )
    return claims


@dataclass
class _Sections:
    """Working buffer while walking the brief."""

    company_brief: list[str] = field(default_factory=list)
    role_areas: list[str] = field(default_factory=list)
    trends: list[str] = field(default_factory=list)
    interviewer_lenses: dict[str, str] = field(default_factory=dict)
    glossary: list[GlossaryEntry] = field(default_factory=list)
    sources: list[ResearchClaim] = field(default_factory=list)
    unmatched: list[str] = field(default_factory=list)


_HEADING_LINE_RE = re.compile(
    r"^(#{1,3}\s+|[A-Z][A-Z0-9 &/\-]{4,60}$)",
    re.MULTILINE,
)


def _split_sections(text: str) -> list[tuple[str, str]]:
    """Split into (heading, body) pairs.

    Recognizes:
        - Markdown headings (#, ##, ###)
        - ALL-CAPS lines that look like section headings (PDF extraction often
          emits these when the source uses bold caps).
    """
    matches = list(_HEADING_LINE_RE.finditer(text))
    if not matches:
        return [("Brief", text)]

    sections: list[tuple[str, str]] = []
    # Pre-heading lead -> "Brief"
    lead = text[: matches[0].start()].strip()
    if lead:
        sections.append(("Brief", lead))
    for i, m in enumerate(matches):
        line_end = text.find("\n", m.start())
        if line_end == -1:
            line_end = m.end()
        heading_line = text[m.start():line_end].strip()
        heading = re.sub(r"^#+\s+", "", heading_line).strip()
        body_start = line_end + 1
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        sections.append((heading, body))
    return sections


def parse_research_brief_text(text: str) -> ResearchInputs:
    """Parse plain text (already PDF-extracted or markdown) into ResearchInputs."""
    buf = _Sections()
    primary_brief: str | None = None

    for heading, body in _split_sections(text):
        target = _classify_heading(heading)
        if target == "company_brief_primary":
            primary_brief = body
            continue
        if target == "company_brief":
            buf.company_brief.append(f"## {heading}\n{body}")
            continue
        if target == "role_areas":
            buf.role_areas.extend(_bullets(body) or [body[:200]])
            continue
        if target == "trends":
            buf.trends.extend(_bullets(body) or [body[:200]])
            continue
        if target == "interviewer":
            # Treat the heading itself as the interviewer name when it
            # contains a personal name pattern, else use "Primary".
            name = heading.replace("Interviewer Lens:", "").strip() or "Primary"
            buf.interviewer_lenses[name] = body[:500]
            continue
        if target == "glossary":
            buf.glossary.extend(_glossary_from_text(body))
            continue
        if target == "sources":
            buf.sources.extend(_sources_from_text(body))
            continue
        # Unmatched -> spillover into company_brief (preserve, never drop).
        buf.unmatched.append(f"## {heading}\n{body}")

    company_brief_parts: list[str] = []
    if primary_brief:
        company_brief_parts.append(primary_brief)
    company_brief_parts.extend(buf.company_brief)
    if buf.unmatched:
        company_brief_parts.append(
            "\n\n---\n\n*Unmatched sections (review and route manually):*\n"
            + "\n\n".join(buf.unmatched)
        )

    return ResearchInputs(
        company_brief="\n\n".join(p for p in company_brief_parts if p) or None,
        role_areas_of_focus=buf.role_areas,
        industry_trends=buf.trends,
        interviewer_lenses=buf.interviewer_lenses,
        source_register=buf.sources,
        glossary_entries=buf.glossary,
        likely_questions=[],
    )


def _extract_pdf_text(path: Path) -> str:
    """Extract text from a PDF using pdfplumber, falling back to pypdf."""
    try:
        import pdfplumber  # type: ignore[import-untyped]

        with pdfplumber.open(path) as pdf:
            return "\n\n".join(page.extract_text() or "" for page in pdf.pages)
    except ImportError:
        pass
    try:
        from pypdf import PdfReader

        reader = PdfReader(path)
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)
    except ImportError as exc:
        raise RuntimeError(
            "Neither pdfplumber nor pypdf is installed. "
            "Install one to enable PDF intake: `uv pip install pdfplumber` "
            "or `uv pip install pypdf`."
        ) from exc


def load_research_brief(path: Path) -> ResearchInputs:
    """Load a research-briefing file and parse into ResearchInputs.

    Supports `.pdf`, `.md`, `.txt`. PDF goes through pdfplumber/pypdf; markdown
    and text are read directly.

    Args:
        path: filesystem path to the brief.

    Returns:
        Best-effort ResearchInputs scaffold. Operator should review.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Research brief not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text = _extract_pdf_text(path)
    else:
        text = path.read_text(encoding="utf-8")
    return parse_research_brief_text(text)
