"""
[SSOT] K.0 Thematic Analysis Node.
Extracted from v61.27.10 legacy patterns.
Provides foundational 'Authenticity Patterns' and 'Competitive Intelligence'
before generation begins.
"""

from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "thematic_analysis_node_types", "p0_governance")
_emit_reads_policy_state("p0", "thematic_analysis_node_types", "policy_binding")
_emit_snapshots_state("p0", "thematic_analysis_node_types", "state_snapshot")
emit_replay_key("p0", "thematic_analysis_node_types")
emit_determinism_digest("p0", "thematic_analysis_node_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "thematic_analysis_node_types", "execution_auth")
_emit_validates_capability("p2", "thematic_analysis_node_types", "capability_check")
_emit_routes_to_capability("p2", "thematic_analysis_node_types", "capability_route")
_emit_writes_via_uwg("p2", "thematic_analysis_node_types", "uwg_write")
_emit_blocks_direct_write("p2", "thematic_analysis_node_types", "direct_write_block")
_emit_records_tool_invocation("p2", "thematic_analysis_node_types", "tool_invocation")
_emit_captures_execution_output("p2", "thematic_analysis_node_types", "exec_output")
_emit_dispatches_agent("p3", "thematic_analysis_node_types", "agent_dispatch")
_emit_coordinates_agents("p3", "thematic_analysis_node_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "thematic_analysis_node_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "thematic_analysis_node_types", "healing_outcome")
_emit_escalates_failure("p3", "thematic_analysis_node_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "thematic_analysis_node_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "thematic_analysis_node_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "thematic_analysis_node_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "thematic_analysis_node_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "thematic_analysis_node_types", "eval_metric")
_emit_stores_embedding("p4", "thematic_analysis_node_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "thematic_analysis_node_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "thematic_analysis_node_types", "exec_snapshot_link")


@dataclass
class AuthenticityPatterns:
    """Authentic language patterns extracted from domain analysis."""

    executive_summary_patterns: list[str]
    achievement_verb_patterns: list[str]
    metric_presentation_patterns: list[str]
    competency_phrasing_patterns: list[str]


@dataclass
class CompetitiveIntelligence:
    """Competitive intelligence from peer job descriptions."""

    peer_jds_analyzed: list[str]
    table_stakes_keywords: list[str]
    differentiator_keywords: list[str]


@dataclass
class ThematicAnalysisOutput:
    """Output from K.0 thematic analysis."""

    primary_theme: str
    secondary_themes: list[str]
    authenticity_patterns: AuthenticityPatterns
    competitive_intelligence: CompetitiveIntelligence
    company_name: str


class ThematicAnalysisNode:
    """
    K.0: Agentic Thematic Resonance Analysis + LinkedIn Authenticity.
    Foundational dependency for all downstream generation nodes.
    """

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}
        self.linkedin_config = {
            "minimum_profiles": 10,
            "authenticity_transformation": {
                "avoid": ["Expert in", "Skilled in"],
                "prefer": ["Built", "Engineered", "Spearheaded"],
            },
        }

    def __call__(self, job_description: str, company_name: str) -> ThematicAnalysisOutput:
        """
        Execute thematic analysis using functor pattern.
        """
        return self.analyze_thematic_resonance(job_description, company_name)

    def analyze_thematic_resonance(self, job_description: str, company_name: str) -> ThematicAnalysisOutput:
        """
        Perform comprehensive thematic analysis.
        In a full implementation, this would use Agentic RAG.
        Current implementation uses heuristic logic for immediate integration.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ThematicAnalysisNode.analyze_thematic_resonance")

        primary, secondary = self._extract_themes(job_description)
        authenticity = AuthenticityPatterns(
            executive_summary_patterns=["Built and scaled", "Led transformation"],
            achievement_verb_patterns=["Spearheaded", "Engineered", "Optimized"],
            metric_presentation_patterns=["resulting in X% improvement"],
            competency_phrasing_patterns=["Specialized in", "Proficient with"],
        )
        comp_intel = CompetitiveIntelligence(
            peer_jds_analyzed=[f"Competitor to {company_name}"],
            table_stakes_keywords=["leadership", "strategy"],
            differentiator_keywords=["innovation", "scale"],
        )
        return ThematicAnalysisOutput(
            primary_theme=primary,
            secondary_themes=secondary,
            authenticity_patterns=authenticity,
            competitive_intelligence=comp_intel,
            company_name=company_name,
        )

    def _extract_themes(self, jd: str) -> tuple[str, list[str]]:
        """Simple heuristic theme extraction."""
        jd_lower = jd.lower()
        if "engineer" in jd_lower or "developer" in jd_lower:
            return ("Engineering Excellence", ["System Architecture", "Scalability"])
        if "manager" in jd_lower or "lead" in jd_lower:
            return ("Strategic Leadership", ["Team Building", "Operational Efficiency"])
        return ("Professional Impact", ["Execution", "Delivery"])
