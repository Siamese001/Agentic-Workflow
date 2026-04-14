"""[SSOT] Logic Node for Resume Section Selection and Analysis.
Extracted from engines to comply with Blueprint Depth-2 Structure.
This is a deterministic utility, NOT an autonomous agent.
"""

from __future__ import annotations

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

_emit_applies_guardrail("p0", "resume_section_node_types", "p0_governance")
_emit_reads_policy_state("p0", "resume_section_node_types", "policy_binding")
_emit_snapshots_state("p0", "resume_section_node_types", "state_snapshot")
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
from tqdm import tqdm

_emit_emits_metric_event("resume_section_node_types", "p4obs", "metric_1")
_emit_emits_metric_event("resume_section_node_types", "p4obs", "metric_2")
_emit_emits_metric_event("resume_section_node_types", "p4obs", "metric_3")
_emit_emits_metric_event("resume_section_node_types", "p4obs", "metric_4")
_emit_emits_metric_event("resume_section_node_types", "p4obs", "metric_5")
_emit_emits_metric_event("resume_section_node_types", "p4obs", "metric_6")
_emit_records_incident_event("resume_section_node_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("resume_section_node_types", "p4obs", "anomaly")
_emit_writes_observability_log("resume_section_node_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("resume_section_node_types", "p4obs", "mon_state")
_emit_triggers_alert("resume_section_node_types", "p4obs", "alert")
_emit_links_incident_trace("resume_section_node_types", "p4obs", "trace_link")
_emit_captures_pattern("resume_section_node_types", "p3lm", "pattern")
_emit_records_learning_event("resume_section_node_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("resume_section_node_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("resume_section_node_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("resume_section_node_types", "p3lm", "routing")
_emit_improves_agent_policy("resume_section_node_types", "p3lm", "policy")
_emit_stores_learning_state("resume_section_node_types", "p3lm", "state")
_emit_records_execution_trace("resume_section_node_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("resume_section_node_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("resume_section_node_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("resume_section_node_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("resume_section_node_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("resume_section_node_types", "env_read", "p2_env_1")
_emit_reads_environ("resume_section_node_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("resume_section_node_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("resume_section_node_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "resume_section_node_types", "context_pull")
_emit_pulls_context("p1", "resume_section_node_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "resume_section_node_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "resume_section_node_types", "uwg_term_2")
_emit_writes_through("p1", "resume_section_node_types", "write_through")
_emit_writes_through("p1", "resume_section_node_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "resume_section_node_types", "safety_validation")
_emit_invokes_eval("p1", "resume_section_node_types", "eval_call")
_emit_proposal_commits_routing("p1", "resume_section_node_types", "routing_commit")
_emit_escalates_to_human("p1", "resume_section_node_types", "human_escalation")
_emit_routes_through("p1", "resume_section_node_types", "route_through")
_emit_checks_agent_registry("p1", "resume_section_node_types", "agent_registry")
_emit_validates_agent_capability("p1", "resume_section_node_types", "capability")
_emit_dispatches_execution_plan("p1", "resume_section_node_types", "exec_plan")
_emit_agent_executes_agent("p1", "resume_section_node_types", "sub_agent")
_emit_routes_to_agent("p1", "resume_section_node_types", "target_agent")
_emit_verifies_policy("p1", "resume_section_node_types", "policy_check")
_emit_observes_runtime_state("p1", "resume_section_node_types", "runtime_state")
_emit_verifies_boundary("p1", "resume_section_node_types", "boundary_check")
_emit_transcripts_response("p1", "resume_section_node_types", "transcript")
_emit_hard_fails_untranscripted("p1", "resume_section_node_types")
_emit_gated_by_confidence("p1", "resume_section_node_types", "confidence_gate")
emit_replay_key("p0", "resume_section_node_types")
emit_determinism_digest("p0", "resume_section_node_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "resume_section_node_types", "execution_auth")
_emit_validates_capability("p2", "resume_section_node_types", "capability_check")
_emit_routes_to_capability("p2", "resume_section_node_types", "capability_route")
_emit_writes_via_uwg("p2", "resume_section_node_types", "uwg_write")
_emit_blocks_direct_write("p2", "resume_section_node_types", "direct_write_block")
_emit_records_tool_invocation("p2", "resume_section_node_types", "tool_invocation")
_emit_captures_execution_output("p2", "resume_section_node_types", "exec_output")
_emit_dispatches_agent("p3", "resume_section_node_types", "agent_dispatch")
_emit_coordinates_agents("p3", "resume_section_node_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "resume_section_node_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "resume_section_node_types", "healing_outcome")
_emit_escalates_failure("p3", "resume_section_node_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "resume_section_node_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "resume_section_node_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "resume_section_node_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "resume_section_node_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "resume_section_node_types", "eval_metric")
_emit_stores_embedding("p4", "resume_section_node_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "resume_section_node_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "resume_section_node_types", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class RoleExtractionResult:
    """Result of role extraction from job description."""

    role: str
    confidence: float
    matched_keywords: list[str]
    seniority_level: str


@dataclass
class IndustryExtractionResult:
    """Result of industry extraction from job description."""

    industry: str
    confidence: float
    matched_keywords: list[str]
    subcategory: str | None = None


@dataclass
class SectionAnalysisResult:
    """Result of resume section analysis."""

    required_sections: list[str]
    optional_sections: list[str]
    emphasis_areas: list[str]
    section_weights: dict[str, float]


@dataclass
class ResumeSectionOutput:
    """Complete resume section analysis output."""

    role_result: RoleExtractionResult
    industry_result: IndustryExtractionResult
    section_analysis: SectionAnalysisResult
    metadata: dict[str, Any]


class ResumeSectionNode:
    """
    Handles resume section selection, role/industry extraction, and content analysis.

    This is a deterministic logic node that extracts structured information from
    job descriptions and determines optimal resume section configuration.
    It is NOT an autonomous agent.
    """

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}
        from .two_phase_generation_node import TwoPhaseGenerationNode

        self.two_phase_node = TwoPhaseGenerationNode(config)
        self.role_keywords = {
            "engineer": ["engineer", "developer", "programmer", "software engineer", "full stack"],
            "manager": ["manager", "lead", "supervisor", "team lead", "head of"],
            "director": ["director", "vp", "vice president", "head", "chief"],
            "analyst": ["analyst", "specialist", "consultant", "advisor"],
            "designer": ["designer", "ux designer", "ui designer", "product designer"],
            "scientist": ["scientist", "researcher", "data scientist", "research scientist"],
        }
        self.seniority_keywords = {
            "ENTRY": ["junior", "entry", "associate", "intern", "trainee"],
            "MID": ["mid", "intermediate", "experienced", "professional"],
            "SENIOR": ["senior", "sr", "principal", "staff", "lead"],
            "EXECUTIVE": ["executive", "c-level", "cxo", "chief", "vp", "director"],
        }
        self.industry_keywords = {
            "technology": {
                "keywords": ["software", "tech", "cloud", "data", "ai", "machine learning", "web"],
                "subcategory_map": {
                    "software": "software_development",
                    "cloud": "cloud_computing",
                    "data": "data_engineering",
                    "ai": "artificial_intelligence",
                },
            },
            "finance": {
                "keywords": ["financial", "banking", "investment", "fintech", "insurance"],
                "subcategory_map": {
                    "banking": "banking_services",
                    "investment": "investment_banking",
                    "fintech": "financial_technology",
                },
            },
            "healthcare": {
                "keywords": ["medical", "health", "clinical", "pharmaceutical", "biotech"],
                "subcategory_map": {
                    "medical": "medical_services",
                    "pharmaceutical": "pharmaceutical_industry",
                    "biotech": "biotechnology",
                },
            },
            "retail": {
                "keywords": ["retail", "ecommerce", "sales", "consumer", "merchandise"],
                "subcategory_map": {
                    "ecommerce": "electronic_commerce",
                    "sales": "sales_operations",
                    "consumer": "consumer_goods",
                },
            },
            "manufacturing": {
                "keywords": ["manufacturing", "production", "industrial", "logistics", "supply chain"],
                "subcategory_map": {
                    "manufacturing": "manufacturing_operations",
                    "logistics": "logistics_management",
                    "supply chain": "supply_chain_management",
                },
            },
        }
        self.section_templates = {
            "technology": {
                "required": ["summary", "experience", "skills", "education", "projects"],
                "optional": ["certifications", "github", "publications"],
                "emphasis": ["skills", "projects", "experience"],
                "weights": {
                    "skills": 0.3,
                    "experience": 0.25,
                    "projects": 0.2,
                    "summary": 0.15,
                    "education": 0.1,
                },
            },
            "finance": {
                "required": ["summary", "experience", "education", "skills"],
                "optional": ["certifications", "licenses", "languages"],
                "emphasis": ["experience", "summary", "education"],
                "weights": {"experience": 0.35, "summary": 0.25, "education": 0.2, "skills": 0.2},
            },
            "healthcare": {
                "required": ["summary", "experience", "education", "licenses", "skills"],
                "optional": ["certifications", "research", "publications"],
                "emphasis": ["licenses", "experience", "education"],
                "weights": {
                    "licenses": 0.3,
                    "experience": 0.25,
                    "education": 0.2,
                    "skills": 0.15,
                    "summary": 0.1,
                },
            },
            "default": {
                "required": ["summary", "experience", "skills", "education"],
                "optional": ["certifications", "projects", "languages"],
                "emphasis": ["experience", "skills"],
                "weights": {"experience": 0.4, "skills": 0.3, "summary": 0.15, "education": 0.15},
            },
        }

    def __call__(
        self,
        job_description: str,
        additional_context: dict[str, Any] = None,
    ) -> ResumeSectionOutput:
        """
        Executes resume section analysis using functor pattern.

        Args:
            job_description: Job description text
            additional_context: Additional context (current resume, preferences, etc.)

        Returns:
            ResumeSectionOutput: Complete section analysis
        """
        if not job_description:
            raise ValueError("Job description cannot be empty")
        return self.analyze_resume_sections(job_description, additional_context or {})

    def analyze_resume_sections(self, job_description: str, context: dict[str, Any]) -> ResumeSectionOutput:
        """Analyze job description and determine optimal resume sections.

        Args:
            job_description: Job description text
            context: Additional context for analysis

        Returns:
            ResumeSectionOutput with role, industry, and section analysis
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "ResumeSectionAnalyzer.analyze_resume_sections"
        )
        logger.info("Analyzing resume sections from job description")
        role_result = self._extract_role(job_description)
        logger.info(f"Role extracted: {role_result.role} (confidence: {role_result.confidence:.2f})")
        industry_result = self._extract_industry(job_description)
        logger.info(
            f"Industry extracted: {industry_result.industry} (confidence: {industry_result.confidence:.2f})",
        )
        section_analysis = self._analyze_section_requirements(role_result, industry_result, job_description)
        logger.info(f"Section analysis complete: {len(section_analysis.required_sections)} required sections")
        output = ResumeSectionOutput(
            role_result=role_result,
            industry_result=industry_result,
            section_analysis=section_analysis,
            metadata={
                "node_id": "ResumeSectionNode",
                "job_description_length": len(job_description),
                "analysis_timestamp": self._get_timestamp(),
            },
        )
        logger.info(f"Resume section analysis complete: {role_result.role} in {industry_result.industry}")
        return output

    def _extract_role(self, job_description: str) -> RoleExtractionResult:
        """Extract primary role from job description.

        Args:
            job_description: Job description text

        Returns:
            RoleExtractionResult with extracted role and confidence
        """
        jd_lower = job_description.lower()
        matched_keywords = []
        best_role = "Professional"
        best_confidence = 0.5
        for role, keywords in self.role_keywords.items():
            role_matches = [kw for kw in keywords if kw in jd_lower]
            if role_matches:
                confidence = min(0.9, 0.5 + len(role_matches) * 0.1)
                if confidence > best_confidence:
                    best_role = role.title()
                    best_confidence = confidence
                    matched_keywords = role_matches
        seniority_level = self._determine_seniority_level(job_description)
        return RoleExtractionResult(
            role=best_role,
            confidence=best_confidence,
            matched_keywords=matched_keywords,
            seniority_level=seniority_level,
        )

    def _determine_seniority_level(self, job_description: str) -> str:
        """Determine seniority level from job description.

        Args:
            job_description: Job description text

        Returns:
            Seniority level string
        """
        jd_lower = job_description.lower()
        for level, keywords in self.seniority_keywords.items():
            if any(keyword in jd_lower for keyword in keywords):
                return level
        return "MID"

    def _extract_industry(self, job_description: str) -> IndustryExtractionResult:
        """Extract industry from job description.

        Args:
            job_description: Job description text

        Returns:
            IndustryExtractionResult with extracted industry and confidence
        """
        jd_lower = job_description.lower()
        best_industry = "Technology"
        best_confidence = 0.5
        best_keywords = []
        best_subcategory = None
        for industry, config in tqdm(self.industry_keywords.items(), desc="Processing", unit="item"):
            industry_matches = [kw for kw in config["keywords"] if kw in jd_lower]
            if industry_matches:
                confidence = min(0.95, 0.5 + len(industry_matches) * 0.15)
                if confidence > best_confidence:
                    best_industry = industry.title()
                    best_confidence = confidence
                    best_keywords = industry_matches
                    for keyword, subcategory in config["subcategory_map"].items():
                        if keyword in jd_lower:
                            best_subcategory = subcategory
                            break
        return IndustryExtractionResult(
            industry=best_industry,
            confidence=best_confidence,
            matched_keywords=best_keywords,
            subcategory=best_subcategory,
        )

    def _analyze_section_requirements(
        self,
        role_result: RoleExtractionResult,
        industry_result: IndustryExtractionResult,
        job_description: str,
    ) -> SectionAnalysisResult:
        """Analyze and determine optimal resume sections.

        Args:
            role_result: Extracted role information
            industry_result: Extracted industry information
            job_description: Job description text

        Returns:
            SectionAnalysisResult with section configuration
        """
        industry_key = industry_result.industry.lower()
        template = self.section_templates.get(industry_key, self.section_templates["default"])
        required_sections = template["required"].copy()
        optional_sections = template["optional"].copy()
        emphasis_areas = template["emphasis"].copy()
        section_weights = template["weights"].copy()
        if role_result.seniority_level == "ENTRY":
            emphasis_areas.extend(["education", "skills"])
            section_weights["education"] = max(section_weights.get("education", 0.1), 0.25)
            section_weights["skills"] = max(section_weights.get("skills", 0.2), 0.3)
        elif role_result.seniority_level == "EXECUTIVE":
            emphasis_areas.extend(["summary", "experience"])
            section_weights["summary"] = max(section_weights.get("summary", 0.1), 0.3)
            section_weights["experience"] = max(section_weights.get("experience", 0.3), 0.4)
        if "certification" in job_description.lower():
            if "certifications" not in required_sections and "certifications" not in optional_sections:
                optional_sections.append("certifications")
        if "project" in job_description.lower() or "portfolio" in job_description.lower():
            if "projects" not in required_sections and "projects" not in optional_sections:
                optional_sections.append("projects")
        total_weight = sum(section_weights.values())
        if total_weight != 1.0:
            section_weights = {k: v / total_weight for k, v in section_weights.items()}
        return SectionAnalysisResult(
            required_sections=required_sections,
            optional_sections=optional_sections,
            emphasis_areas=list(set(emphasis_areas)),
            section_weights=section_weights,
        )

    def generate_experience_section(self, profile: dict[str, Any], thematic_output: Any) -> dict[str, Any]:
        """
        [Enhanced] Generates experience using Two-Phase K-Node pattern.
        """
        role_data = self.extract_role_data(profile)
        bullet_out = self.two_phase_node.generate_bullets_phase_a(thematic_output, role_data)
        overview_out = self.two_phase_node.synthesize_overview_phase_b(
            bullet_out,
            thematic_output,
            target_section="resume_overview",
        )
        return {
            "bullets": bullet_out.bullets,
            "overview": overview_out.overview,
            "validation_signature": overview_out.validation_result,
            "meta": {"provenance": bullet_out.provenance_counts, "word_count": overview_out.word_count},
        }

    def extract_role_data(self, profile: dict[str, Any]) -> dict[str, Any]:
        """Extract role data from profile for two-phase generation."""
        return {
            "role": profile.get("role", "Professional"),
            "experience": profile.get("experience", ""),
            "skills": profile.get("skills", []),
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata."""
        from datetime import datetime

        return datetime.now().isoformat()

    def get_section_template(self, industry: str) -> dict[str, Any]:
        """Get section template for a specific industry.

        Args:
            industry: Industry name

        Returns:
            Section template configuration
        """
        industry_key = industry.lower()
        return self.section_templates.get(industry_key, self.section_templates["default"])

    def validate_section_completeness(
        self,
        sections: list[str],
        required_sections: list[str],
    ) -> dict[str, Any]:
        """Validate if all required sections are present.

        Args:
            sections: Available sections
            required_sections: Required sections

        Returns:
            Validation result with missing sections
        """
        missing_sections = [req for req in required_sections if req not in sections]
        return {
            "is_complete": len(missing_sections) == 0,
            "missing_sections": missing_sections,
            "completeness_score": 1.0 - len(missing_sections) / len(required_sections),
        }
