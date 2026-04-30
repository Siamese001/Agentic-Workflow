"""
BulletDiversityGate — enforce thematic diversity within each role section.

Reads:  'optimized_content' (post-ContentOptimizerEngine, pre-SectionRanker)
Writes: 'optimized_content' (re-published with diversity-rebalanced bullets)
Signal: 'DIVERSITY_LOW' (warn-only) when a section can't reach the target
        thematic spread.

Rationale: P1 alignment scoring tends to converge a section onto a single
theme (e.g. all six Unify bullets become "platform commercialization"
variants). For a recruiter-facing resume that hurts the breadth signal.
This gate ensures each section surfaces ≥ TARGET_DISTINCT_THEMES distinct
themes when the source role has the variety to support it.

Themes are computed from the JD facet vocabulary (P1.2) intersected with
each bullet's content. Theme tagging is a deterministic substring scan,
mirroring `JobPatternMatcher`.

P4.1 of plan apps-rg-customization-uplift-7c4f12.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import logging
from typing import Any

from apps_rg.engines._lifecycle_emits import _emit_engine_lifecycle
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_engine_lifecycle("bullet_diversity_gate")

Logger = logging.getLogger(__name__)

# Top-level themes — intentionally coarse so a 5–6 bullet section can still
# meaningfully cover three. Each theme is the same canonical bucket as
# `JobPatternMatcher` facets, plus a few cross-cutting categories.
_THEMES: dict[str, tuple[str, ...]] = {
    "leadership": (
        "led", "lead", "managed", "direct", "scale", "scaled", "grew",
        "team", "organization", "hired", "mentored", "leveled",
    ),
    "platform": (
        "platform", "architecture", "framework", "infrastructure",
        "microservice", "api", "gateway", "service", "system",
    ),
    "ai_genai": (
        "ai", "llm", "agentic", "model", "generative", "rag", "graphrag",
        "vector", "embedding", "transformer", "language model", "neural",
    ),
    "commercialization": (
        "revenue", "$", "p&l", "margin", "pipeline", "renewal",
        "go-to-market", "gtm", "alliance", "partner", "co-sell",
        "productized", "productization",
    ),
    "client_advisory": (
        "client", "executive", "c-suite", "boardroom", "stakeholder",
        "advisor", "consulting", "engagement", "transformation",
        "change management", "alignment",
    ),
    "operational": (
        "uptime", "latency", "reliability", "incident", "rollback",
        "observability", "telemetry", "monitor", "ci/cd", "deployment",
    ),
    "regulatory": (
        "compliance", "regulator", "sox", "ccar", "basel", "solvency",
        "soc 2", "gdpr", "audit", "policy",
    ),
    "data_analytics": (
        "data", "analytics", "pipeline", "warehouse", "lakehouse",
        "snowflake", "databricks", "etl", "ingest",
    ),
}

# Targets — relaxed for short sections.
TARGET_DISTINCT_THEMES = 4
MIN_DISTINCT_THEMES = 2  # warn-only floor


def _tag_themes(text: str) -> list[str]:
    """Return list of themes whose seed words appear in text."""
    if not text:
        return []
    t = text.lower()
    hits: list[str] = []
    for theme, seeds in _THEMES.items():
        if any(s in t for s in seeds):
            hits.append(theme)
    return hits


class BulletDiversityGate(BaseRGEngine):
    """L3 refinement gate — enforces thematic spread per section."""

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.DIVERSITY")

    @traces_execute(layer="L3_ORCHESTRATION")
    async def execute(self) -> dict[str, Any]:
        content = self.ctx.buffer.read("optimized_content")
        if not content or not isinstance(content, dict):
            self.record_fail("Missing optimized_content", signal="DATA_MISSING")
            return {"valid": False}

        # We also want the full HOP-2 pool so we can swap in a more diverse
        # bullet if the optimizer left a section thematically thin.
        enriched = self.ctx.buffer.read("hop2_enrichment") or {}
        pool_by_company: dict[str, list[dict]] = {}
        for sec in enriched.get("experience_sections", []):
            pool_by_company[sec.get("company", "?")] = sec.get("bullets", [])

        sections = content.get("experience_sections", [])
        report: dict[str, Any] = {
            "valid": True,
            "sections": [],
            "low_diversity": [],
        }

        for section in sections:
            company = section.get("company", "?")
            bullets = section.get("bullets", [])
            for b in bullets:
                if "themes" not in b:
                    b["themes"] = _tag_themes(b.get("bullet_text", ""))
            distinct = {t for b in bullets for t in b.get("themes", [])}
            current_count = len(distinct)

            # If under target, try swap-in from pool.
            if current_count < TARGET_DISTINCT_THEMES and company in pool_by_company:
                pool = pool_by_company[company]
                # Candidates not currently in section, with theme diversity.
                current_texts = {b.get("bullet_text") for b in bullets}
                added = 0
                for cand in sorted(
                    pool,
                    key=lambda x: -float(x.get("alignment_score", 0.0)),
                ):
                    if added >= 2:  # cap at 2 swap-ins so we don't blow up section size
                        break
                    cand_text = cand.get("bullet_text")
                    if not cand_text or cand_text in current_texts:
                        continue
                    cand_themes = _tag_themes(cand_text)
                    if not cand_themes:
                        continue
                    new_themes = set(cand_themes) - distinct
                    if not new_themes:
                        continue
                    # Replace the lowest-alignment bullet only if section is
                    # already at MAX (6); otherwise append.
                    cand["themes"] = cand_themes
                    if len(bullets) >= 6:
                        bullets[-1] = cand
                    else:
                        bullets.append(cand)
                    distinct |= set(cand_themes)
                    current_texts.add(cand_text)
                    added += 1
                section["bullets"] = bullets

            final_count = len({t for b in bullets for t in b.get("themes", [])})
            section_report = {
                "company": company,
                "bullet_count": len(bullets),
                "theme_count": final_count,
                "themes": sorted({t for b in bullets for t in b.get("themes", [])}),
                "target": TARGET_DISTINCT_THEMES,
                "min": MIN_DISTINCT_THEMES,
            }
            report["sections"].append(section_report)
            if final_count < MIN_DISTINCT_THEMES and len(bullets) >= 3:
                report["low_diversity"].append(company)
                report["valid"] = False  # warn-level, not hard fail

        self.ctx.buffer.write("optimized_content", content, source_agent=self.name)
        self.ctx.buffer.write("diversity_report", report, source_agent=self.name)

        if report["low_diversity"]:
            self.record_fail(
                f"Low diversity in sections: {report['low_diversity']}",
                data=report,
                signal="DIVERSITY_LOW",
            )
        else:
            self.record_pass(
                f"Diversity gate PASSED — {len(report['sections'])} sections, "
                f"avg themes={sum(s['theme_count'] for s in report['sections'])/max(1,len(report['sections'])):.1f}"
            )
        return report
