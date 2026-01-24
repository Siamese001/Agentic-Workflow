"""
HOP1 Clerk Engine - Structural Extraction Engine
Refactored from apply_clerk_extraction.py
Following Batch 2 specifications with hallucination detection

HARDENING: Removes direct arguments. Enforces reading 'mission_input' from Buffer
and writing 'hop1_extraction' to Buffer.
"""

from __future__ import annotations
from typing import Any, Dict, List
import logging
import re

from apps_rg.engines.base.base_resume_engine import BaseRGEngine
from apps_rg.engines.safety.hallucination_detector_engine import HallucinationDetector

Logger = logging.getLogger(__name__)


class ClerkExtractionEngine(BaseRGEngine):
    """
    HOP-1: Structural Extraction Engine.
    Reads 'mission_input' -> Writes 'hop1_extraction'.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="HOP.1.CLERK")
        # Initialize sub-components using the shared context
        self.detector = HallucinationDetector(ctx)

    async def execute(self) -> Dict[str, Any]:
        """
        Execute HOP-1 extraction using Immutable Buffer data.
        """
        # 1. READ from Buffer (Deep Copy Enforced)
        mission_input = self.ctx.buffer.read("mission_input")
        if not mission_input or "master_resume" not in mission_input:
            self.record_fail("Missing 'mission_input' or 'master_resume' in Buffer", signal="DATA_MISSING")
            raise ValueError("Buffer missing mission_input")

        source = mission_input["master_resume"]
        self._mcp_audit("extraction_start")

        # 2. PROCESS (Business Logic)
        experience_sections = self._build_sections(source.get("experience", []))
        
        for section in experience_sections:
            for bullet in section.get("bullets", []):
                bullet["quantified_metrics"] = self._extract_metrics(bullet["bullet_text"])

        # 3. Hallucination Check
        all_bullets = [b["bullet_text"] for s in experience_sections for b in s["bullets"]]
        validation = self.detector.check_batch(all_bullets)
        
        if not validation["valid"]:
            self.ctx.add_signal("SOURCE_DATA_UNRELIABLE")

        output = {
            "experience_sections": experience_sections,
            "education": source.get("education", []),
            "metadata": {"source_integrity": validation["score"]}
        }
        
        # 4. WRITE to Buffer (Transaction Logged)
        # This commits the state for HOP-2 to consume
        self.ctx.buffer.write("hop1_extraction", output, source_agent=self.name)
        
        self.record_pass("HOP-1 Extraction Complete", data={"sections": len(experience_sections)})
        return output

    def _build_sections(self, raw_exp: List[Dict]) -> List[Dict]:
        """Standardize raw experience into Sovereign segments."""
        sections = []
        for exp in raw_exp:
            sections.append({
                "company": exp.get("company", "Unknown"),
                "title": exp.get("title", "Unknown"),
                "bullets": [{"bullet_text": b} for b in exp.get("bullets", [])]
            })
        return sections

    def _extract_metrics(self, text: str) -> List[str]:
        """Legacy regex extraction."""
        patterns = [r"\$\d+\.?\d*[MBK]\+?", r"\d+\.?\d*%", r"\d{1,3}(?:,\d{3})+"]
        found = []
        for pattern in patterns:
            found.extend(re.findall(pattern, text))
        return found
