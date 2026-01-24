"""
K9 Gap Closure Engine - Leadership Competencies & Gap Closure
Refactored from GapClosureArchitectAgent.py
Following Batch 3 specifications

HARDENING: Reads 'hop2_enrichment' (Candidate Data) and 'mission_input' (JD).
Writes 'k9_competencies'. Enforces the "Exactly 6" rule via SovereignContext validation.
"""

from __future__ import annotations
from typing import Any
from dataclasses import dataclass
import logging

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


@dataclass
class CompetencyItem:
    title: str
    description: str
    word_count: int


class GapClosureEngine(BaseRGEngine):
    """
    K-Node K.9: Leadership Competencies & Gap Closure.
    Reads: 'hop2_enrichment', 'mission_input'
    Writes: 'k9_competencies'
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="K.9")

    async def execute(self) -> list[dict[str, Any]]:
        """
        Generate gap-closing competencies based on enriched profile and JD.
        """
        # 1. READ from Buffer
        enrichment = self.ctx.buffer.read("hop2_enrichment")
        mission = self.ctx.buffer.read("mission_input")

        if not enrichment or not mission:
            self.record_fail("Missing dependencies for K9 Generation", signal="DATA_MISSING")
            raise ValueError("Buffer missing hop2_enrichment or mission_input")

        jd_keywords = mission.get("job_description_keywords", [])  # Assuming extracted in HOP0/1
        candidate_skills = self._extract_skills(enrichment)

        self._mcp_audit("k9_generation_start")

        # 2. LOGIC: Identify Gaps
        gap_keywords = [k for k in jd_keywords if k not in candidate_skills]

        # 3. LOGIC: Generate (Mock LLM Call)
        # In prod, this uses self.get_frozen_prompt("k9_gap_closure")
        competencies = self._mock_generation(gap_keywords)

        # 4. HARDENING: Zero Tolerance Count
        if len(competencies) != 6:
            self.record_fail(
                f"Generated {len(competencies)} competencies. Required: 6.",
                signal="GENERATION_COUNT_VIOLATION",
            )
            # In a real run, trigger HealerMixin here
            return []

        # 5. HARDENING: Word Count Balance
        issues = self._validate_word_counts(competencies)
        if issues:
            self.record_fail("Competency balance violation", data={"issues": issues})
            self.ctx.add_signal("QUALITY_FAILURE")

        # 6. WRITE to Buffer
        output = [vars(c) for c in competencies]
        self.ctx.buffer.write("k9_competencies", output, source_agent=self.name)

        self.record_pass("K9 Generation Complete", data={"count": 6})
        return output

    def _extract_skills(self, data: dict) -> list[str]:
        # Helper to flatten skills from enrichment data
        return data.get("skills", [])

    def _mock_generation(self, gaps: list[str]) -> list[CompetencyItem]:
        # Stub for LLM generation
        return [CompetencyItem("Skill", "Desc", 25) for _ in range(6)]

    def _validate_word_counts(self, items: list[CompetencyItem]) -> list[str]:
        issues = []
        for item in items:
            if not (22 <= item.word_count <= 28):
                issues.append(f"Length violation: {item.word_count}")
        return issues
