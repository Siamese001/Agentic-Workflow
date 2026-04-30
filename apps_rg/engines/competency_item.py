"""
K9 Gap Closure Engine - Leadership Competencies & Gap Closure
Refactored from GapClosureArchitectAgent.py
Following Batch 3 specifications

HARDENING: Reads 'hop2_enrichment' (Candidate Data) and 'mission_input' (JD).
Writes 'k9_competencies'. Enforces the "Exactly 6" rule via SovereignContext validation.
Now delegates skill analysis to logic_nodes for deterministic logic extraction.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from apps_rg.types.skill_extractor_node import SkillExtractorNode

from apps_rg.engines.base_rg_engine import BaseRGEngine

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

from apps_rg.engines._lifecycle_emits import _emit_engine_lifecycle

_emit_engine_lifecycle("competency_item")


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

    @traces_execute(layer="L3_ORCHESTRATION")
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
        # Bug fix (2026-04-28): SkillExtractorNode._extract_skills_from_profile
        # expects a candidate profile with shape {experience, skills, summary,
        # education} — the master_resume shape, not the HOP2 enrichment shape.
        # Passing enrichment yielded 0 skills extracted → 0% match → CRITICAL
        # gap on every run. Prefer master_resume; fall back to enrichment.
        candidate_profile = mission.get("master_resume") or enrichment
        skill_analysis = self.skill_extractor(job_description, candidate_profile)
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
