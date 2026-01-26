"""
Template Optimizer Engine - Selects optimal presentation template
Refactored from RgTemplateOptimizerAgent.py
Following Batch 5 specifications

HARDENING: Reads 'mission_input' (JD). Selects visual strategy. Writes 'template_strategy'.
"""

from __future__ import annotations
from typing import Any
import logging

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class TemplateOptimizerEngine(BaseRGEngine):
    """
    Sovereign Refinement Engine.
    Reads: 'mission_input'
    Writes: 'template_strategy'
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.TEMPLATE")

    async def execute(self) -> dict[str, Any]:
        """
        Select presentation template based on JD analysis.
        """
        # 1. READ
        mission = self.ctx.buffer.read("mission_input")
        jd_text = mission.get("job_description", "") if mission else ""

        if not jd_text:
            self.record_fail("Empty JD", signal="DATA_MISSING")
            return {"template": "standard"}

        # 2. LOGIC
        job_type = self._detect_job_type(jd_text)

        # 3. WRITE
        result = {"job_type": job_type, "recommended_template": f"sov_v2_{job_type}"}
        self.ctx.buffer.write("template_strategy", result, source_agent=self.name)

        self.record_pass(f"Template selected: {job_type}")
        return result

    def _detect_job_type(self, text: str) -> str:
        # Simple heuristic stub
        if "manager" in text.lower() or "lead" in text.lower():
            return "executive"
        return "technical"
