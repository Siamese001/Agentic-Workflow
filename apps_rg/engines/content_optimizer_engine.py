"""
Content Optimizer Engine - Reorders bullet points for maximum impact
Refactored from optimize_content_order.py
Following Batch 4 specifications

HARDENING: Reads 'hop2_enrichment' (or generation output). Reorders content based on
'adjusted_weights' from Buffer. Writes 'optimized_content'.
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_rg_engine import BaseRGEngine

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Logger = logging.getLogger(__name__)


class ContentOptimizerEngine(BaseRGEngine):
    """
    Sovereign Refinement Engine.
    Reads: 'hop2_enrichment', 'adjusted_weights'
    Writes: 'optimized_content'
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.OPTIMIZER")

    async def execute(self) -> list[dict[str, Any]]:
        """
        Reorder resume content based on impact scoring and weights.
        """
        # 1. READ from Buffer
        data = self.ctx.buffer.read("hop2_enrichment")
        weights = self.ctx.buffer.read("adjusted_weights", default={})

        if not data:
            self.record_fail("Missing content to optimize", signal="DATA_MISSING")
            return []

        sections = data.get("experience_sections", [])

        # 2. LOGIC: Score and Sort
        optimized_sections = []
        for section in sections:
            bullets = section.get("bullets", [])
            # Sort by impact score
            optimized_bullets = sorted(
                bullets,
                key=lambda b: self._calculate_impact_score(b, weights),
                reverse=True,
            )
            section["bullets"] = optimized_bullets
            optimized_sections.append(section)

        # 3. WRITE to Buffer - Convert list to dict for section ranker
        optimized_dict = {
            "experience_sections": optimized_sections,
            "education": data.get("education", []),
            "skills": data.get("skills", []),
        }
        self.ctx.buffer.write("optimized_content", optimized_dict, source_agent=self.name)

        self.record_pass("Content optimization complete")
        return optimized_sections

    def _calculate_impact_score(self, bullet: dict, weights: dict) -> float:
        score = 0.0
        if bullet.get("quantified_metrics"):
            score += 0.5
        # Apply section weight boost if applicable
        score *= weights.get("experience", 1.0)
        return score
