"""
K9 Gap Closure Engine - Leadership Competencies & Gap Closure
Refactored from GapClosureArchitectAgent.py
Following Batch 3 specifications

HARDENING: Reads 'hop2_enrichment' (Candidate Data) and 'mission_input' (JD).
Writes 'k9_competencies'. Enforces the "Exactly 6" rule via SovereignContext validation.
Now delegates skill analysis to logic_nodes for deterministic logic extraction.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from apps_rg.types.skill_extractor_node import SkillExtractorNode

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "competency_item", "p0_governance")
_emit_reads_policy_state("p0", "competency_item", "policy_binding")
_emit_snapshots_state("p0", "competency_item", "state_snapshot")
emit_replay_key("p0", "competency_item")
emit_determinism_digest("p0", "competency_item")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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

    Now delegates skill gap analysis to SkillExtractorNode logic node
    to comply with Blueprint Depth-2 Structure requirements.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="K.9")
        self.skill_extractor = SkillExtractorNode(config=self.config.get("skill_config", {}))

    async def execute(self) -> list[dict[str, Any]]:
        """
        Generate gap-closing competencies based on enriched profile and JD.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "GapClosureEngine.execute")

        enrichment = self.ctx.buffer.read("hop2_enrichment")
        mission = self.ctx.buffer.read("mission_input")
        if not enrichment or not mission:
            self.record_fail("Missing dependencies for K9 Generation", signal="DATA_MISSING")
            raise ValueError("Buffer missing hop2_enrichment or mission_input")
        mission.get("job_description_keywords", [])
        self._mcp_audit("k9_generation_start")
        job_description = mission.get("job_description", "")
        skill_analysis = self.skill_extractor(job_description, enrichment)
        gap_skills = skill_analysis.gap_result.missing_skills[:6]
        competencies = self._generate_competencies(gap_skills)
        if len(competencies) != 6:
            self.record_fail(
                f"Generated {len(competencies)} competencies. Required: 6.",
                signal="GENERATION_COUNT_VIOLATION",
            )
            return []
        issues = self._validate_word_counts(competencies)
        if issues:
            self.record_fail("Competency balance violation", data={"issues": issues})
            self.ctx.add_signal("QUALITY_FAILURE")
        output = [vars(c) for c in competencies]
        self.ctx.buffer.write("k9_competencies", output, source_agent=self.name)
        self.record_pass("K9 Generation Complete using logic nodes", data={"count": 6})
        return output

    def _generate_competencies(self, gap_skills: list[str]) -> list[CompetencyItem]:
        """Generate competency items based on skill gaps.

        Args:
            gap_skills: List of skills that need to be addressed

        Returns:
            List of 6 competency items
        """
        competencies = []
        for _i, skill in enumerate(gap_skills[:6]):
            title = f"{skill} Leadership"
            description = f"Demonstrated expertise in {skill} with measurable impact and team collaboration."
            word_count = len(description.split())
            competencies.append(CompetencyItem(title=title, description=description, word_count=word_count))
        generic_competencies = [
            ("Strategic Leadership", "Strategic thinking and planning with cross-functional collaboration."),
            ("Team Development", "Building and mentoring high-performing teams with clear objectives."),
            (
                "Change Management",
                "Leading organizational change with effective communication and stakeholder engagement.",
            ),
            ("Results Orientation", "Driving measurable results through data-driven decision making."),
            ("Innovation Leadership", "Fostering innovation and creative problem-solving approaches."),
            ("Communication Excellence", "Clear, persuasive communication across all organizational levels."),
        ]
        while len(competencies) < 6:
            i = len(competencies) - len(gap_skills)
            if i < len(generic_competencies):
                title, description = generic_competencies[i]
                word_count = len(description.split())
                competencies.append(CompetencyItem(title, description, word_count))
        return competencies[:6]

    def _validate_word_counts(self, items: list[CompetencyItem]) -> list[str]:
        issues = []
        for item in items:
            if not 22 <= item.word_count <= 28:
                issues.append(f"Length violation: {item.word_count}")
        return issues
