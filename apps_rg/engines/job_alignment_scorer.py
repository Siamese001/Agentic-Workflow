"""
JobAlignmentScorer Engine - JD↔bullet alignment scoring.

Reads:  'mission_input' (job_description), 'hop2_enrichment' (bullets)
Writes: 'jd_facets' (extracted JD signals), 'bullet_alignment_scores' (per-bullet 0..1)

Deterministic TF-IDF over JD facets + token overlap. No external embedding
dependency — keeps the determinism digest stable across runs.

Design notes:
- JD facets: 5 buckets (responsibilities, level, industry, soft_skills, technical).
  Pulled from JobPatternMatcher in P1.2; this engine does scoring only.
- Score formula: `0.45*facet_overlap + 0.30*tfidf_cosine + 0.15*level_fit + 0.10*recency_decay`
- Recency decay: most recent role gets 1.0, each prior role *0.85.
- Threshold for retention is enforced in ContentOptimizerEngine (P1.3).
"""

from __future__ import annotations

import logging
import math
import re
from collections import Counter
from typing import Any

from apps_rg.engines._lifecycle_emits import _emit_engine_lifecycle
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_engine_lifecycle("job_alignment_scorer")

Logger = logging.getLogger(__name__)

# Stopwords kept tight — losing too many words hurts TF-IDF on short JD facets.
_STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "have", "in", "is", "it", "of", "on", "or", "that", "the", "their", "to",
    "with", "will", "you", "your", "our", "we", "this", "these", "those", "but",
    "not", "than", "into", "across", "through", "via", "such", "all", "any",
})


def _tokenize(text: str) -> list[str]:
    """Lowercase word tokens, drop stopwords and pure-numeric tokens shorter than 2."""
    if not text:
        return []
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9\-]+", text.lower())
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]


def _tf(tokens: list[str]) -> dict[str, float]:
    if not tokens:
        return {}
    counter = Counter(tokens)
    total = sum(counter.values())
    return {term: count / total for term, count in counter.items()}


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    if not common:
        return 0.0
    dot = sum(a[t] * b[t] for t in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class JobAlignmentScorer(BaseRGEngine):
    """L3 Refinement engine — scores each bullet's alignment to JD facets."""

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.JD_ALIGNMENT")

    async def execute(self) -> dict[str, Any]:
        mission = self.ctx.buffer.read("mission_input") or {}
        jd_text = mission.get("job_description", "")
        jd_facets = self.ctx.buffer.read("jd_facets") or {}
        enriched = self.ctx.buffer.read("hop2_enrichment")

        if not jd_text:
            self.record_fail("Missing job_description in mission_input", signal="DATA_MISSING")
            return {"scores": {}, "facets": {}}
        if not enriched:
            self.record_fail("Missing hop2_enrichment", signal="DATA_MISSING")
            return {"scores": {}, "facets": {}}

        jd_tokens = _tokenize(jd_text)
        jd_tf = _tf(jd_tokens)
        jd_token_set = set(jd_tokens)

        # Flatten facet vocabulary for overlap scoring.
        facet_vocab: set[str] = set()
        for bucket_terms in jd_facets.values():
            if isinstance(bucket_terms, list):
                for term in bucket_terms:
                    facet_vocab.update(_tokenize(str(term)))

        sections = enriched.get("experience_sections", [])
        scores: dict[str, list[float]] = {}
        n_roles = len(sections)

        for role_idx, section in enumerate(sections):
            company = section.get("company", f"role_{role_idx}")
            recency = max(0.5, 0.85 ** role_idx)  # most recent = 1.0, decay 0.85 per role back
            section_scores: list[float] = []

            for bullet in section.get("bullets", []):
                text = bullet.get("bullet_text", "")
                bullet_tokens = _tokenize(text)
                bullet_tf = _tf(bullet_tokens)
                bullet_set = set(bullet_tokens)

                # Facet overlap — fraction of bullet tokens that match JD facets.
                facet_overlap = (
                    len(bullet_set & facet_vocab) / max(len(bullet_set), 1)
                    if facet_vocab else 0.0
                )
                # TF cosine vs full JD.
                cosine = _cosine(bullet_tf, jd_tf)
                # Level fit: did bullet mention scope words present in JD?
                level_words = {"executive", "c-suite", "ceo", "cfo", "coo", "svp",
                               "leadership", "transformation", "strategic", "advisory",
                               "fortune", "boardroom", "client", "stakeholder"}
                bullet_level = len(bullet_set & level_words & jd_token_set)
                level_fit = min(1.0, bullet_level / 3.0)
                # Quantification bonus — keeps the existing metric heuristic alive.
                has_metrics = bool(bullet.get("quantified_metrics"))

                score = (
                    0.45 * facet_overlap
                    + 0.30 * cosine
                    + 0.15 * level_fit
                    + 0.10 * recency
                )
                if has_metrics:
                    score = min(1.0, score * 1.10)

                bullet["alignment_score"] = round(score, 4)
                bullet["alignment_components"] = {
                    "facet_overlap": round(facet_overlap, 4),
                    "tfidf_cosine": round(cosine, 4),
                    "level_fit": round(level_fit, 4),
                    "recency": round(recency, 4),
                    "has_metrics": has_metrics,
                }
                section_scores.append(score)

            scores[company] = section_scores

        # Re-write enriched payload with alignment fields populated on bullets.
        self.ctx.buffer.write("hop2_enrichment", enriched, source_agent=self.name)
        self.ctx.buffer.write(
            "bullet_alignment_scores",
            {"per_role": scores, "n_roles": n_roles, "facet_vocab_size": len(facet_vocab)},
            source_agent=self.name,
        )
        self.record_pass(
            f"Aligned bullets across {n_roles} roles; facet vocab={len(facet_vocab)}"
        )
        return {"scores": scores, "facets": jd_facets}
