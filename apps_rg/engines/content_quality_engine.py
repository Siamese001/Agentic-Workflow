"""
Content Quality Engine - General quality rules
Refactored from ContentQualityAgent.py

HARDENING: Reads 'hop2_enrichment' (or any content stage). Writes 'quality_report'.
Checks for forbidden phrases and metric density.
"""
from __future__ import annotations
import logging
from typing import Any
from apps_rg.engines.base_rg_engine import BaseRGEngine
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)

class ContentQualityEngine(BaseRGEngine):
    """
    Sovereign Quality Engine.
    Reads: 'hop2_enrichment' (or specified input)
    Writes: 'quality_report'
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id='QUALITY.CONTENT')

    async def execute(self, target_key: str='hop2_enrichment') -> dict[str, Any]:
        """
        Audit content for Sovereign Quality Standards.
        """
        data = self.ctx.buffer.read(target_key)
        if not data:
            return {'score': 0, 'status': 'skipped'}
        issues = []
        score = 100
        sections = data.get('experience_sections', [])
        for sec in sections:
            for bullet in sec.get('bullets', []):
                text = bullet.get('bullet_text', '').lower()
                if 'responsible for' in text:
                    issues.append(f"Weak phrase in {sec.get('company')}")
                    score -= 5
                if not bullet.get('quantified_metrics'):
                    score -= 1
        report = {'score': score, 'issues': issues, 'status': 'passed' if score > 80 else 'warning'}
        self.ctx.buffer.write('quality_report', report, source_agent=self.name)
        if score < 70:
            self.record_fail(f'Quality Score Low: {score}', data=report, signal='QUALITY_FAILURE')
        else:
            self.record_pass(f'Quality Score: {score}')
        return report
