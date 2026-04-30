"""
Job Pattern Matcher - JD facet extraction.

Replaces the 3-regex stub (Python|Java|AWS) with a 5-bucket facet extractor:
  - responsibilities: action-oriented JD bullets ("Lead the design of...")
  - level: seniority/scope signals (SVP, executive, C-suite, board)
  - industry: vertical and account-type signals (Fortune 1000, PE, financial)
  - soft_skills: relationship/influence signals (advisory, change management)
  - technical: technology surface area mentioned (AI, cloud, ML, agentic)

Writes 'jd_facets' to the buffer for JobAlignmentScorer to consume.
Deterministic — no LLM call.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from apps_rg.engines._lifecycle_emits import _emit_engine_lifecycle
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_engine_lifecycle("job_pattern_matcher")

Logger = logging.getLogger(__name__)

# Curated facet seed vocabularies. Each list expanded by JD scan via fuzzy
# stem match. Keep deterministic — no embeddings, no external calls.
_LEVEL_SEEDS = [
    "svp", "senior vice president", "vp", "vice president", "evp",
    "executive", "c-suite", "ceo", "cfo", "coo", "caio", "cto", "chief",
    "head of", "principal", "partner", "managing director", "md",
    "fortune 1000", "fortune 500", "private equity", "pe-backed",
    "board", "boardroom", "steering committee",
]

_SOFT_SKILL_SEEDS = [
    "client leadership", "executive engagement", "trusted advisor",
    "strategic advisor", "change management", "organizational readiness",
    "transformation", "stakeholder", "consulting", "advisory",
    "relationship", "credibility", "trust", "influence", "negotiation",
    "facilitation", "alignment", "executive alignment", "executive presence",
    "communication", "collaboration", "thought leadership",
]

_INDUSTRY_SEEDS = [
    "financial services", "banking", "insurance", "asset management",
    "healthcare", "life sciences", "retail", "consumer", "manufacturing",
    "technology", "media", "telecommunications", "energy", "public sector",
    "fortune 1000", "fortune 500", "private equity", "portfolio company",
    "regulated", "compliance",
]

_TECHNICAL_SEEDS = [
    "agentic", "agentic ai", "ai agents", "autonomous workflows",
    "decision-layer automation", "generative ai", "llm", "large language model",
    "rag", "graphrag", "retrieval", "vector", "embedding",
    "machine learning", "ml", "data science", "ai platform", "ai governance",
    "cloud", "aws", "azure", "gcp", "databricks", "snowflake",
    "erp", "digital transformation", "data platform", "analytics",
    "automation", "orchestration", "multi-agent",
]

# Action verbs that mark a JD responsibility bullet.
_RESPONSIBILITY_VERB_RE = re.compile(
    r"\b(lead|own|drive|build|design|architect|develop|deliver|guide|advise|"
    r"shape|cultivate|partner|frame|translate|orchestrate|champion|mentor|"
    r"establish|define|launch|scale|grow|transform|govern)\b",
    re.IGNORECASE,
)

# Years-of-experience pattern.
_YOE_RE = re.compile(r"\b(\d{1,2})\+?\s*(?:to\s*\d{1,2}\s*)?years?\b", re.IGNORECASE)


def _scan_seeds(text: str, seeds: list[str]) -> list[str]:
    """Return seed terms found in text (case-insensitive substring match)."""
    text_lower = text.lower()
    hits = []
    for seed in seeds:
        if seed in text_lower:
            hits.append(seed)
    return hits


class JobPatternMatcher(BaseRGEngine):
    """L3 Cognition engine — extracts JD facets and writes to buffer."""

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="COGNITION.JD_FACETS")

    async def execute(self, job_description: str | None = None) -> dict[str, Any]:
        """Extract structured facets from the JD. If `job_description` not
        passed, read from `mission_input`."""
        if job_description is None:
            mission = self.ctx.buffer.read("mission_input") or {}
            job_description = mission.get("job_description", "")
        if not job_description:
            self.record_fail("Missing job_description", signal="DATA_MISSING")
            return {}

        self._mcp_audit("jd_facet_extraction_start")

        facets: dict[str, Any] = {
            "level": _scan_seeds(job_description, _LEVEL_SEEDS),
            "soft_skills": _scan_seeds(job_description, _SOFT_SKILL_SEEDS),
            "industry": _scan_seeds(job_description, _INDUSTRY_SEEDS),
            "technical": _scan_seeds(job_description, _TECHNICAL_SEEDS),
            "responsibilities": self._extract_responsibilities(job_description),
            "years_required": self._extract_yoe(job_description),
            "is_individual_contributor": self._is_ic_role(job_description),
        }

        # Cross-bucket dedup so a token doesn't double-count.
        seen: set[str] = set()
        for bucket in ("level", "soft_skills", "industry", "technical"):
            facets[bucket] = [t for t in facets[bucket] if not (t in seen or seen.add(t))]

        self.ctx.buffer.write("jd_facets", facets, source_agent=self.name)
        self.record_pass(
            f"JD facets: level={len(facets['level'])} soft={len(facets['soft_skills'])} "
            f"industry={len(facets['industry'])} tech={len(facets['technical'])} "
            f"resp={len(facets['responsibilities'])}"
        )
        return facets

    def _extract_responsibilities(self, text: str) -> list[str]:
        """Extract bullet-style responsibility statements from JD."""
        lines = re.split(r"[\n\r]+", text)
        out: list[str] = []
        for line in lines:
            stripped = line.strip().lstrip("-\u2022*").strip()
            if not stripped or len(stripped) < 20 or len(stripped) > 280:
                continue
            if _RESPONSIBILITY_VERB_RE.search(stripped):
                out.append(stripped)
        return out[:25]

    def _extract_yoe(self, text: str) -> int | None:
        m = _YOE_RE.search(text)
        if not m:
            return None
        try:
            return int(m.group(1))
        except (ValueError, IndexError):
            return None

    def _is_ic_role(self, text: str) -> bool:
        """True if JD explicitly disclaims technical/IC work."""
        ic_disclaimers = [
            "you will not be writing code",
            "non-technical",
            "not a technical role",
            "no engineering work",
        ]
        text_lower = text.lower()
        return any(p in text_lower for p in ic_disclaimers)
