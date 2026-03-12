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
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)

class ContentOptimizerEngine(BaseRGEngine):
    """
    Sovereign Refinement Engine.
    Reads: 'hop2_enrichment', 'adjusted_weights'
    Writes: 'optimized_content'
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id='REFINE.OPTIMIZER')

    async def execute(self) -> list[dict[str, Any]]:
        """
        Reorder resume content based on impact scoring and weights.
        """
        data = self.ctx.buffer.read('hop2_enrichment')
        weights = self.ctx.buffer.read('adjusted_weights', default={})
        if not data:
            self.record_fail('Missing content to optimize', signal='DATA_MISSING')
            return []
        sections = data.get('experience_sections', [])
        optimized_sections = []
        for section in sections:
            bullets = section.get('bullets', [])
            optimized_bullets = sorted(bullets, key=lambda b: self._calculate_impact_score(b, weights), reverse=True)
            section['bullets'] = optimized_bullets
            optimized_sections.append(section)
        optimized_dict = {'experience_sections': optimized_sections, 'education': data.get('education', []), 'skills': data.get('skills', [])}
        self.ctx.buffer.write('optimized_content', optimized_dict, source_agent=self.name)
        self.record_pass('Content optimization complete')
        return optimized_sections

    def _calculate_impact_score(self, bullet: dict, weights: dict) -> float:
        score = 0.0
        if bullet.get('quantified_metrics'):
            score += 0.5
        score *= weights.get('experience', 1.0)
        return score
