"""
RoleArchetypeClassifier — infer the JD's role archetype.

Reads:  'mission_input' (job_description), 'jd_facets' (preferred — from P1.2)
Writes: 'mission_input.role_type' (archetype name consumed by SectionRankerEngine)

7 archetypes, deterministic scoring:
  - executive            : C-suite, P&L, board exposure
  - strategic_advisory   : consulting, transformation, client-facing executive (Blend360-style)
  - technical_leadership : engineering leader, hands-on architect
  - product_leadership   : product/platform owner
  - sales_engineering    : pre-sales, hyperscaler alliance, GTM
  - individual_contributor : explicit IC role
  - default              : fallback

P3.2 of plan apps-rg-customization-uplift-7c4f12.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import logging
from typing import Any

from apps_rg.engines._lifecycle_emits import _emit_engine_lifecycle
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_engine_lifecycle("role_archetype_classifier")

Logger = logging.getLogger(__name__)


# Each archetype has a list of `(phrase, weight)` indicators. Highest total
# wins. Phrases are case-insensitive substring matches.
_ARCHETYPE_INDICATORS: dict[str, list[tuple[str, float]]] = {
    "executive": [
        ("ceo", 3.0), ("cfo", 2.5), ("coo", 2.5), ("svp", 3.0),
        ("c-suite", 2.0), ("p&l", 2.5), ("p and l", 2.0),
        ("board of directors", 2.5), ("board-level", 2.0),
        ("revenue ownership", 2.0), ("operating committee", 2.0),
    ],
    "strategic_advisory": [
        ("trusted advisor", 3.0), ("strategic advisor", 3.0),
        ("client leadership", 2.5), ("executive engagement", 2.5),
        ("change management", 2.0), ("organizational readiness", 2.5),
        ("consulting", 2.0), ("advisory", 2.0),
        ("non-technical", 3.0), ("you will not be writing code", 4.0),
        ("transformation", 2.0), ("roadmap", 1.5),
        ("steering committee", 2.0), ("boardroom", 2.0),
        ("private equity", 1.5), ("fortune 1000", 1.5),
    ],
    "technical_leadership": [
        ("architect", 2.0), ("engineering leader", 2.5),
        ("technical leader", 2.5), ("vp engineering", 2.5),
        ("head of engineering", 2.5), ("head of platform", 2.0),
        ("hands-on", 2.0), ("technical depth", 2.0),
        ("system design", 1.5), ("distributed systems", 1.5),
        ("write code", 2.0), ("ship code", 2.0),
    ],
    "product_leadership": [
        ("product manager", 3.0), ("vp product", 3.0),
        ("head of product", 3.0), ("product owner", 2.0),
        ("roadmap", 1.0), ("product strategy", 2.0),
        ("user research", 1.5), ("ux", 1.0),
    ],
    "sales_engineering": [
        ("pre-sales", 3.0), ("solutions engineer", 3.0),
        ("sales engineer", 3.0), ("hyperscaler", 2.0),
        ("co-sell", 2.5), ("partner", 1.0),
        ("go-to-market", 2.0), ("gtm", 2.0),
        ("quota", 2.5), ("revenue target", 2.0),
    ],
    "individual_contributor": [
        ("software engineer", 2.5), ("senior engineer", 2.0),
        ("staff engineer", 2.0), ("ic role", 3.0),
        ("hands-on coder", 3.0), ("must code", 2.5),
    ],
}

# SectionRankerEngine's strategy table only knows these four keys today.
# Map each archetype to one of them so ordering still resolves.
_ARCHETYPE_TO_STRATEGY: dict[str, str] = {
    "executive": "executive",
    "strategic_advisory": "executive",
    "technical_leadership": "technical",
    "product_leadership": "executive",
    "sales_engineering": "executive",
    "individual_contributor": "technical",
    "default": "default",
}


class RoleArchetypeClassifier(BaseRGEngine):
    """L1 cognition engine — infers JD archetype from facet vocabulary."""

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="COGNITION.ROLE_ARCHETYPE")

    @traces_execute(layer="L3_ORCHESTRATION")
    async def execute(self) -> dict[str, Any]:
        mission = self.ctx.buffer.read("mission_input") or {}
        jd_text = mission.get("job_description", "") or ""
        if not jd_text:
            self.record_fail("Missing job_description", signal="DATA_MISSING")
            return {"archetype": "default"}

        text_lower = jd_text.lower()
        scores: dict[str, float] = {}
        for archetype, indicators in _ARCHETYPE_INDICATORS.items():
            total = 0.0
            hits: list[str] = []
            for phrase, weight in indicators:
                if phrase in text_lower:
                    total += weight
                    hits.append(phrase)
            scores[archetype] = total

        # Pick best, with a small tie-break preference for strategic_advisory
        # since it's the most under-served archetype in the existing strategy table.
        best = max(scores, key=lambda k: (scores[k], k == "strategic_advisory"))
        if scores[best] < 2.0:
            best = "default"

        strategy_key = _ARCHETYPE_TO_STRATEGY.get(best, "default")

        # Mutate mission_input so SectionRankerEngine reads it.
        mission["role_type"] = strategy_key
        mission["role_archetype"] = best
        mission["role_archetype_scores"] = {k: round(v, 2) for k, v in scores.items()}
        self.ctx.buffer.write("mission_input", mission, source_agent=self.name)

        self.record_pass(
            f"Archetype: {best} (strategy_key={strategy_key}) "
            f"top_scores={sorted(scores.items(), key=lambda x: -x[1])[:3]}"
        )
        return {
            "archetype": best,
            "strategy_key": strategy_key,
            "scores": scores,
        }
