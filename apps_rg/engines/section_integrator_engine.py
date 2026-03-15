"""
Section Integrator Engine - Deduplication & Overview synthesis
Refactored from section_scope_integrator_engine.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_rg_engine import BaseRGEngine
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

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
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SectionIntegratorEngine.execute")

        self._mcp_audit("integration_start")
        all_text = []
        for section in sections:
            for bullet in section.get("bullets", []):
                all_text.append(bullet.get("bullet_text", ""))
        seen = set()
        duplicates = []
        for text in all_text:
            normalized = text.lower().strip()
            if normalized in seen:
                duplicates.append(text)
            else:
                seen.add(normalized)
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
