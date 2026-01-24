"""
Section Integrator Engine - Deduplication & Overview synthesis
Refactored from section_scope_integrator_engine.py
"""

from __future__ import annotations
from typing import Any
import logging

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class SectionIntegratorEngine(BaseRGEngine):
    """
    Section Integration - Deduplication and overview synthesis.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.INTEGRATOR")

    async def execute(self, sections: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Integrate sections and remove cross-section redundancy.
        """
        self._mcp_audit("integration_start")

        # Collect all text for deduplication
        all_text = []
        for section in sections:
            for bullet in section.get("bullets", []):
                all_text.append(bullet.get("bullet_text", ""))

        # Find duplicates
        seen = set()
        duplicates = []
        for text in all_text:
            normalized = text.lower().strip()
            if normalized in seen:
                duplicates.append(text)
            else:
                seen.add(normalized)

        # Remove duplicates from sections
        deduplicated_sections = []
        for section in sections:
            unique_bullets = []
            for bullet in section.get("bullets", []):
                if bullet.get("bullet_text", "").lower().strip() in seen:
                    unique_bullets.append(bullet)
                    seen.remove(bullet.get("bullet_text", "").lower().strip())
            section["bullets"] = unique_bullets
            deduplicated_sections.append(section)

        result = {
            "sections": deduplicated_sections,
            "duplicates_removed": len(duplicates),
            "total_bullets": len(all_text) - len(duplicates),
        }

        self.record_pass(f"Integration complete: {len(duplicates)} duplicates removed", data=result)
        return result
