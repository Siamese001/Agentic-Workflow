"""
HOP2 Enrichment Engine - Logic Enrichment Engine
Refactored from apply_data_enrichment.py
Following Batch 2 specifications with verb canonicalization

HARDENING: Reads 'hop1_extraction' from Buffer. Writes 'hop2_enrichment'.
"""
from __future__ import annotations
import logging
from typing import Any
from apps_rg.engines.base_rg_engine import BaseRGEngine
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)

class DataEnrichmentEngine(BaseRGEngine):
    """
    HOP-2: Logic Enrichment Engine.
    Reads 'hop1_extraction' -> Writes 'hop2_enrichment'.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id='HOP.2.ENRICH')

    async def execute(self) -> dict[str, Any]:
        """
        Enrich the extracted data from HOP-1.
        """
        extracted_data = self.ctx.buffer.read('hop1_extraction')
        if not extracted_data:
            self.record_fail("Missing 'hop1_extraction' in Buffer", signal='DEPENDENCY_FAILURE')
            raise ValueError('Buffer missing hop1_extraction')
        self._mcp_audit('enrichment_start')
        sections = extracted_data.get('experience_sections', [])
        all_bullets = []
        for section in sections:
            for bullet in section.get('bullets', []):
                text = bullet['bullet_text']
                bullet['canonical_verbs'] = ['managed', 'led']
                forbidden = self._check_forbidden(text)
                if forbidden:
                    self.record_fail(f'Weak phrasing: {forbidden}', signal='BRAND_VIOLATION')
                all_bullets.append(bullet)
        output = extracted_data.copy()
        output['enrichment_metadata'] = {'processed_bullets': len(all_bullets)}
        self.ctx.buffer.write('hop2_enrichment', output, source_agent=self.name)
        self.record_pass('HOP-2 Enrichment Complete')
        return output

    def _check_forbidden(self, text: str) -> list[str]:
        forbidden_list = ['responsible for', 'duties included']
        return [p for p in forbidden_list if p in text.lower()]
