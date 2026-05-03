"""apps_research outputs -> ResearchInputs adapter.

Reads the artifacts emitted by apps_research at `reports/research/`:
    - research_brief_<trace>.md     -> company_brief, role_areas_of_focus,
                                       industry_trends (heuristic section split)
    - source_register_<trace>.json  -> ResearchClaim[]

Use the most-recent brief by default, or pass an explicit `trace_id`.
"""

from __future__ import annotations

import json
import re
import warnings
from pathlib import Path

from apps_qna.types.qna_types import ResearchClaim, ResearchInputs
from apps_shared.contracts.cross_app import (
    EnvelopeLoadError,
    ResearchBriefEnvelope,
)

_DEFAULT_RESEARCH_DIR = Path("reports/research")
_BRIEF_RE = re.compile(r"^research_brief_([0-9a-f]+)\.md$")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*$", re.MULTILINE)


def _latest_trace_id(research_dir: Path) -> str:
    """Return the most-recent research-brief trace id present in `research_dir`."""
    if not research_dir.is_dir():
        raise FileNotFoundError(f"Research output directory not found: {research_dir}")
    candidates: list[tuple[float, str]] = []
    for path in research_dir.glob("research_brief_*.md"):
        match = _BRIEF_RE.match(path.name)
        if match:
            candidates.append((path.stat().st_mtime, match.group(1)))
    if not candidates:
        raise FileNotFoundError(
            f"No research_brief_<trace>.md files in {research_dir}"
        )
    return max(candidates)[1]


def _section(brief_text: str, heading: str) -> str:
    """Return the body under a markdown H2 (`## heading`); empty if not present."""
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$\n?(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(brief_text)
    return match.group(1).strip() if match else ""


def _bullets(text: str) -> list[str]:
    return [m.group(1).strip() for m in _BULLET_RE.finditer(text)]


def _claims_from_register(rows: list[dict]) -> list[ResearchClaim]:
    """Convert the source_register.json rows into typed ResearchClaim objects."""
    claims: list[ResearchClaim] = []
    for row in rows:
        # source_register uses `summary` as the claim text.
        claim_text = row.get("summary") or row.get("title") or ""
        if not claim_text:
            continue
        ct = row.get("claim_type", "direct_evidence")
        # Normalize to the Literal accepted by ResearchClaim.
        if ct not in {"direct_evidence", "interpretation", "analyst_inference", "assumption"}:
            ct = "analyst_inference"
        claims.append(
            ResearchClaim(
                claim=claim_text,
                claim_type=ct,
                source_id=row.get("source_id", "SRC-000"),
                section_id=row.get("section_id", ""),
            )
        )
    return claims


def _inputs_from_envelope(env: ResearchBriefEnvelope) -> ResearchInputs:
    claims = [
        ResearchClaim(
            claim=row.claim,
            claim_type=row.claim_type,
            source_id=row.source_id,
            section_id=row.section_id,
        )
        for row in env.payload.source_register
    ]
    return ResearchInputs(
        company_brief=env.payload.company_brief,
        role_areas_of_focus=list(env.payload.role_areas_of_focus),
        industry_trends=list(env.payload.industry_trends),
        interviewer_lenses={},
        source_register=claims,
        glossary_entries=[],
        likely_questions=[],
    )


def load_apps_research(
    trace_id: str | None = None,
    research_dir: Path | None = None,
) -> ResearchInputs:
    """Load apps_research outputs into a ResearchInputs.

    Prefers a sibling `research_brief_<trace>.envelope.json`. Falls back to
    the markdown-regex parser with DeprecationWarning.

    Args:
        trace_id: explicit trace id (`<8hex>`). If None, picks the most recent.
        research_dir: directory holding the artifacts. Defaults to
            `reports/research/` relative to CWD.

    Raises:
        FileNotFoundError: directory missing or no briefs in it.
    """
    research_dir = research_dir or _DEFAULT_RESEARCH_DIR
    if trace_id is None:
        trace_id = _latest_trace_id(research_dir)

    envelope_path = research_dir / f"research_brief_{trace_id}.envelope.json"
    if envelope_path.is_file():
        try:
            env = ResearchBriefEnvelope.load(envelope_path)
            return _inputs_from_envelope(env)
        except EnvelopeLoadError as exc:
            warnings.warn(
                f"Envelope at {envelope_path} failed to load ({exc}); "
                "falling back to markdown-regex parser.",
                DeprecationWarning,
                stacklevel=2,
            )

    brief_path = research_dir / f"research_brief_{trace_id}.md"
    register_path = research_dir / f"source_register_{trace_id}.json"

    warnings.warn(
        f"Envelope missing at {envelope_path}; falling back to markdown-regex "
        "parser. Run `python -m apps_research.outputs.envelope_emitter "
        f"--trace-id {trace_id}` to produce the envelope.",
        DeprecationWarning,
        stacklevel=2,
    )

    if not brief_path.is_file():
        raise FileNotFoundError(f"Research brief not found: {brief_path}")

    brief_text = brief_path.read_text(encoding="utf-8")

    # Heuristic section mapping. apps_research's renderer emits these H2s.
    company_brief = _section(brief_text, "Executive Summary") or brief_text[:2000]
    role_areas = _bullets(_section(brief_text, "Key Findings"))
    industry_trends = _bullets(_section(brief_text, "Strategic Implications"))

    source_register: list[ResearchClaim] = []
    if register_path.is_file():
        try:
            rows = json.loads(register_path.read_text(encoding="utf-8"))
            if isinstance(rows, list):
                source_register = _claims_from_register(rows)
        except json.JSONDecodeError:
            pass  # Tolerate malformed register; downstream sees empty list.

    return ResearchInputs(
        company_brief=company_brief.strip() or None,
        role_areas_of_focus=role_areas,
        industry_trends=industry_trends,
        interviewer_lenses={},
        source_register=source_register,
        glossary_entries=[],
        likely_questions=[],
    )
