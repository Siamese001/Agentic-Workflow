"""PDF / Markdown research-briefing -> ResearchInputs adapter.

Two-stage classification pipeline (Wave 2):

  1. **Fast regex path** (deterministic, no model load):
     - Markdown / ALL-CAPS / numbered / Title-Case heading detection
     - Substring match on ``_HEADING_HINTS`` for the canonical targets

  2. **Spine fallback path** (semantic, BGE-M3-backed via
     ``apps_qna.integrations.spine_adapter.classify_section_topic``):
     - When the regex path returns no match for a section, the section
       body is embedded and ranked against canonical topic descriptors.
     - When ``_split_sections`` yields a single section because the PDF
       had no recognizable heading structure (the Searce-research-brief
       failure mode), the entire text is paragraph-segmented and each
       paragraph is topic-classified, then consecutive same-topic
       paragraphs are merged into synthetic sections.

The embedding path uses BGE-M3 via ``agentic_core.embeddings.bge_runtime``;
when sentence-transformers / BGE weights are unavailable the spine adapter
falls back to keyword overlap. apps_qna does not depend on BGE at import
time.

No LLM is invoked at any stage. This adapter remains "good enough to
scaffold"; the operator reviews and refines the produced YAML.

Section target taxonomy (case-insensitive substring match; first wins;
fallback path uses semantic classification when none match):

| Heading contains            | Maps to                       |
|-----------------------------|-------------------------------|
| "executive summary"         | company_brief                 |
| "company" / "organization"  | company_brief (appended)      |
| "role" / "position"         | role_areas_of_focus (bullets) |
| "trend" / "industry"        | industry_trends (bullets)     |
| "interviewer" / "lens"      | interviewer_lenses (entry)    |
| "glossary" / "terms"        | glossary_entries (parsed)     |
| "source" / "citation"       | source_register (parsed lines)|
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from apps_qna.integrations.spine_adapter import classify_section_topic
from apps_qna.types.qna_types import (
    GlossaryEntry,
    ResearchClaim,
    ResearchInputs,
)

_log = logging.getLogger(__name__)

_BULLET_RE = re.compile(r"^\s*[-•*]\s+(.+?)\s*$", re.MULTILINE)

# Spine classification descriptors. Each canonical topic key has a prose
# descriptor that BGE-M3 embeds and ranks against section text. Keys MUST
# stay in lockstep with ``_TOPIC_TO_TARGET`` and the ``buf`` field set.
_TOPIC_DESCRIPTORS: dict[str, str] = {
    "company_brief": (
        "Company background and history. Founding year, headquarters, "
        "employee count, revenue, ownership, leadership team, market "
        "positioning, partnerships, certifications, awards, recent "
        "strategic moves, mergers, acquisitions, funding rounds, "
        "corporate values, mission, vision, organizational structure."
    ),
    "role_areas": (
        "Role responsibilities and position details. Day-to-day "
        "expectations, ownership scope, reporting structure, success "
        "criteria, key deliverables, mandate, primary objectives, "
        "reporting line, decision authority, scope of accountability, "
        "required skills, leadership expectations."
    ),
    "trends": (
        "Industry trends and market dynamics. Sector inflection points, "
        "competitive landscape, technology adoption curves, regulatory "
        "shifts, market growth, demand drivers, headwinds, tailwinds, "
        "buyer behavior shifts, AI adoption patterns, vendor landscape."
    ),
    "interviewer": (
        "Interviewer professional background. Career history, education, "
        "recent publications, public speaking engagements, podcast "
        "appearances, hot buttons, technical depth, thought leadership, "
        "interviewing style, prior teams, tenure, signature initiatives."
    ),
    "glossary": (
        "Definitions of technical terms, acronyms, jargon, methodology "
        "names, framework names, process abbreviations, named platforms, "
        "product names, internal terminology, industry-specific vocabulary."
    ),
    "sources": (
        "Citations, references, source documents, evidence pointers, "
        "claim provenance, dates of access, URLs, source identifiers, "
        "bibliography entries, primary sources, secondary sources."
    ),
}

# topic_key -> ResearchInputs target slug used by the existing _classify_heading
# / parse_research_brief_text dispatch. Kept aligned with _HEADING_HINTS so the
# regex fast path and the embedding fallback path produce identical buf shapes.
_TOPIC_TO_TARGET: dict[str, str] = {
    "company_brief": "company_brief",
    "role_areas": "role_areas",
    "trends": "trends",
    "interviewer": "interviewer",
    "glossary": "glossary",
    "sources": "sources",
}

# Synthetic heading labels for sections rebuilt from paragraph-fallback
# segmentation (so the downstream renderer still sees a usable heading).
_TOPIC_TO_SYNTHETIC_HEADING: dict[str, str] = {
    "company_brief": "Company Overview",
    "role_areas": "Role Areas of Focus",
    "trends": "Industry Trends",
    "interviewer": "Interviewer Lens",
    "glossary": "Glossary",
    "sources": "Source Register",
}

# Score thresholds for the embedding-fallback classifier. Cosine on
# BGE-M3 normalized vectors generally falls in 0.3-0.7 for relevant text
# vs. descriptor; we choose 0.45 to admit moderate matches. Keyword path
# scores are word-overlap fractions and trend much lower (≈0.1-0.3 for
# real matches); 0.12 is empirically separating signal from noise.
_EMBEDDING_THRESHOLD: float = 0.45
_KEYWORD_THRESHOLD: float = 0.12
# Paragraph-fallback uses slightly looser thresholds since paragraphs are
# shorter than full sections and signal-per-token is lower.
_PARA_EMBEDDING_THRESHOLD: float = 0.40
_PARA_KEYWORD_THRESHOLD: float = 0.10
# Below this paragraph length (in chars) we don't bother classifying; the
# paragraph is appended to the current accumulating topic.
_MIN_PARAGRAPH_CHARS: int = 80
# Below this total text length, we skip paragraph-fallback segmentation
# entirely and just leave the single "Brief" section. PDFs that small are
# typically intentional one-page summaries.
_PARAGRAPH_FALLBACK_MIN_CHARS: int = 5000

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


def _classify_heading(heading: str, body: str | None = None) -> str | None:
    """Classify a section heading to a canonical target.

    Two-stage:
      1. Substring match against ``_HEADING_HINTS`` (fast, deterministic).
      2. If no regex match AND a non-empty body is provided, embed the
         body via the spine adapter and rank it against the topic
         descriptors. Returns the best match if its score clears the
         per-mode threshold.

    The body argument is keyword-only-implicit: callers that only have a
    heading (e.g. unit-test fixtures) get the legacy regex-only behavior.
    """
    h = heading.lower().strip()
    for hint, target in _HEADING_HINTS:
        if hint in h:
            return target
    if body and len(body) >= 100:
        topic, score, mode = classify_section_topic(body, _TOPIC_DESCRIPTORS)
        threshold = (
            _EMBEDDING_THRESHOLD if mode == "embedding" else _KEYWORD_THRESHOLD
        )
        if topic and score >= threshold:
            _log.debug(
                "spine-classified heading=%r target=%s score=%.3f mode=%s",
                heading,
                topic,
                score,
                mode,
            )
            return _TOPIC_TO_TARGET.get(topic)
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


# Heading detection regex. Recognizes:
#   - Markdown:    "# Title", "## Title", "### Title"
#   - ALL-CAPS:    "AMERICAS STRATEGY" (PDF emits these for bold caps)
#   - Numbered:    "1. Company Profile", "3.2 Industry Trends"
#   - Title Case:  "Industry Trends:", "Vrinda Khurjekar — Lens"
# Title-Case requires either a trailing colon, em-dash, or end-of-line
# with no trailing punctuation, to avoid matching the first line of a
# paragraph.
_HEADING_LINE_RE = re.compile(
    r"^("
    r"#{1,3}\s+\S|"                                        # markdown
    r"[A-Z][A-Z0-9 &/\-:']{4,80}$|"                        # all-caps
    r"\d+(?:\.\d+)?\.?\s+[A-Z][\w][\w\s&\-:']{2,70}$|"     # numbered
    r"[A-Z][\w&]+(?:\s+(?:[A-Z][\w&\-']*|and|of|the|in|to|for|on|with|by|at|a))*\s*[:\u2014\u2013]\s*$"  # Title-Case ending in : / em-dash / en-dash
    r")",
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


def _paragraph_topic_segmentation(text: str) -> list[tuple[str, str]]:
    """Fallback when heading detection finds <=1 section.

    Segments the text into paragraphs, classifies each via the spine
    adapter (embedding or keyword fallback), and merges consecutive
    same-topic paragraphs into synthetic sections. Used to recover from
    PDFs whose headings are stripped during extraction or whose
    structure was lost in the source layout.

    Each section is paired with a synthetic heading derived from the
    detected topic so that downstream regex-substring matching in
    ``_classify_heading`` (the fast path) still works.
    """
    paras = [
        p.strip()
        for p in re.split(r"\n\s*\n+", text)
        if len(p.strip()) >= _MIN_PARAGRAPH_CHARS
    ]
    if len(paras) < 3:
        return [("Brief", text)]

    sections: list[tuple[str, str]] = []
    current_topic: str | None = None
    current_paras: list[str] = []

    for para in paras:
        topic, score, mode = classify_section_topic(para, _TOPIC_DESCRIPTORS)
        threshold = (
            _PARA_EMBEDDING_THRESHOLD
            if mode == "embedding"
            else _PARA_KEYWORD_THRESHOLD
        )
        # Below threshold or empty topic -> stick with previous accumulating
        # topic, defaulting to "company_brief" for the very first paragraph.
        if not topic or score < threshold:
            assigned = current_topic or "company_brief"
        else:
            assigned = topic
        if assigned != current_topic and current_paras:
            heading_label = _TOPIC_TO_SYNTHETIC_HEADING.get(
                current_topic or "", "Brief"
            )
            sections.append((heading_label, "\n\n".join(current_paras)))
            current_paras = []
        current_topic = assigned
        current_paras.append(para)

    if current_paras:
        heading_label = _TOPIC_TO_SYNTHETIC_HEADING.get(
            current_topic or "", "Brief"
        )
        sections.append((heading_label, "\n\n".join(current_paras)))

    _log.info(
        "paragraph-fallback segmentation: %d paragraphs -> %d sections",
        len(paras),
        len(sections),
    )
    return sections


def parse_research_brief_text(text: str) -> ResearchInputs:
    """Parse plain text (already PDF-extracted or markdown) into ResearchInputs.

    Two-stage segmentation:

    1. ``_split_sections`` runs the heading regex (markdown / ALL-CAPS /
       numbered / Title-Case). For typical structured documents this
       produces a clean list of sections.
    2. When the regex yields only the implicit ``("Brief", text)`` tuple
       AND the text is large (> ``_PARAGRAPH_FALLBACK_MIN_CHARS``), the
       paragraph-fallback segmenter activates: it splits on blank lines,
       classifies each paragraph against ``_TOPIC_DESCRIPTORS`` via the
       spine adapter, and merges consecutive same-topic paragraphs into
       synthetic sections. This recovers from PDFs whose layout-derived
       heading structure was destroyed by the text extractor.
    """
    sections = _split_sections(text)
    if len(sections) <= 1 and len(text) > _PARAGRAPH_FALLBACK_MIN_CHARS:
        sections = _paragraph_topic_segmentation(text)

    buf = _Sections()
    primary_brief: str | None = None

    for heading, body in sections:
        target = _classify_heading(heading, body=body)
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
