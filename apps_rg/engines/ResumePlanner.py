"""RG Planner - Resume Generation L1 Planning Layer.

Incorporated from historical agentic_workflow/l1/RgPlanner.py to provide
resume-specific planning capabilities for the 8-node sequential pipeline.

This is the L1 planning layer that coordinates:
Resume Analysis Planning → K1 Extraction → K2 Cleaning → K3 Quantification → K4 Rewriting → K5 Skill Mapping → K6 Section Assembly → K7 Formatting → K8 Validation
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

Logger = logging.getLogger(__name__)


@dataclass
class ResumeAnalysisPlan:
    """Resume analysis planning configuration."""
    target_role: str
    target_company: str
    industry_focus: str
    seniority_level: str
    analysis_depth: str  # "basic", "comprehensive", "deep"
    extraction_strategy: str  # "section_based", "semantic", "hybrid"
    quantification_approach: str  # "metrics_focus", "achievements", "impact"
    rewriting_style: str  # "professional", "modern", "industry_specific"
    skill_mapping_method: str  # "job_alignment", "industry_standards", "advanced"
    section_organization: str  # "chronological", "functional", "hybrid"
    formatting_standards: str  # "ats_optimized", "creative", "executive"
    validation_level: str  # "basic", "comprehensive", "enterprise"
    confidence_threshold: float = 0.7
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class ResumeSectionConfig:
    """Configuration for individual resume sections."""
    section_name: str
    required: bool
    max_length: int
    priority: int  # 1 = highest
    content_type: str  # "experience", "skills", "education", "projects"
    extraction_rules: List[str]
    validation_rules: List[str]
    formatting_rules: List[str]
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class ResumeProcessingPlan:
    """Complete resume processing plan for K1-K8 pipeline."""
    analysis_plan: ResumeAnalysisPlan
    section_configs: List[ResumeSectionConfig]
    extraction_params: Dict[str, object]
    cleaning_params: Dict[str, object]
    quantification_params: Dict[str, object]
    rewriting_params: Dict[str, object]
    skill_mapping_params: Dict[str, object]
    assembly_params: Dict[str, object]
    formatting_params: Dict[str, object]
    validation_params: Dict[str, object]
    execution_order: List[str]
    fallback_strategies: Dict[str, str]
    metadata: Dict[str, object] = field(default_factory=dict)


class RGPlanner:
    """Resume generation planner - L1 planning layer.

    Creates comprehensive plans for resume analysis and optimization
    across the 8-node sequential processing pipeline.
    """

    def __init__(self,
                 config: Optional[Dict[str, object]] = None,
                 telemetry_bus: Optional[Any] = None) -> None:
        """Initialize resume generation planner."""
        self.config = config or {}
        self.telemetry_bus = telemetry_bus

        # Default resume processing configurations
        self.default_config = {
            "analysis_depths": ["basic", "comprehensive", "deep"],
            "extraction_strategies": ["section_based", "semantic", "hybrid"],
            "quantification_approaches": ["metrics_focus", "achievements", "impact"],
            "rewriting_styles": ["professional", "modern", "industry_specific"],
            "skill_mapping_methods": ["job_alignment", "industry_standards", "advanced"],
            "section_organizations": ["chronological", "functional", "hybrid"],
            "formatting_standards": ["ats_optimized", "creative", "executive"],
            "validation_levels": ["basic", "comprehensive", "enterprise"]
        }

        # Standard resume sections
        self.standard_sections = [
            "contact_info", "summary", "experience", "education",
            "skills", "projects", "certifications", "achievements"
        ]

    def plan_resume_processing(
        self,
        *,
        job_input: Dict[str, object],
        resume_input: Dict[str, object],
        processing_options: Optional[Dict[str, object]] = None
    ) -> ResumeProcessingPlan:
        """Generate comprehensive resume processing plan.

        Args:
            job_input: Target job requirements and specifications
            resume_input: Current resume content and structure
            processing_options: Additional processing preferences

        Returns:
            Complete resume processing plan for K1-K8 pipeline
        """
        processing_options = processing_options or {}

        # 1. Analyze job requirements
        job_analysis = self._analyze_job_requirements(job_input)

        # 2. Analyze current resume structure
        resume_analysis = self._analyze_resume_structure(resume_input)

        # 3. Determine processing strategy
        processing_strategy = self._determine_processing_strategy(
            job_analysis, resume_analysis, processing_options
        )

        # 4. Create analysis plan
        analysis_plan = self._create_analysis_plan(job_analysis, processing_strategy)

        # 5. Configure section processing
        section_configs = self._configure_section_processing(
            resume_analysis, processing_strategy
        )

        # 6. Set K-node parameters
        k_node_params = self._set_k_node_parameters(processing_strategy)

        # 7. Define execution order
        execution_order = self._define_execution_order(processing_strategy)

        # 8. Configure fallback strategies
        fallback_strategies = self._configure_fallback_strategies(processing_strategy)

        # 9. Build complete processing plan
        processing_plan = ResumeProcessingPlan(
            analysis_plan=analysis_plan,
            section_configs=section_configs,
            extraction_params=k_node_params["extraction"],
            cleaning_params=k_node_params["cleaning"],
            quantification_params=k_node_params["quantification"],
            rewriting_params=k_node_params["rewriting"],
            skill_mapping_params=k_node_params["skill_mapping"],
            assembly_params=k_node_params["assembly"],
            formatting_params=k_node_params["formatting"],
            validation_params=k_node_params["validation"],
            execution_order=execution_order,
            fallback_strategies=fallback_strategies,
            metadata={
                "job_analysis": job_analysis,
                "resume_analysis": resume_analysis,
                "processing_strategy": processing_strategy,
                "planning_timestamp": "2024-01-01T00:00:00Z"
            }
        )

        # 10. Record telemetry (best-effort)
        self._safe_record_telemetry(processing_plan)

        return processing_plan

    def _analyze_job_requirements(self, job_input: Dict[str, object]) -> Dict[str, object]:
        """Analyze job requirements to inform processing strategy."""
        return {
            "target_role": job_input.get("title", ""),
            "target_company": job_input.get("company", ""),
            "industry": job_input.get("industry", "technology"),
            "seniority": job_input.get("seniority", "mid"),
            "required_skills": job_input.get("skills", []),
            "experience_level": job_input.get("experience_years", 0),
            "key_requirements": job_input.get("requirements", []),
            "complexity_score": self._calculate_job_complexity(job_input)
        }

    def _analyze_resume_structure(self, resume_input: Dict[str, object]) -> Dict[str, object]:
        """Analyze current resume structure and content."""
        sections = resume_input.get("sections", {})

        return {
            "total_sections": len(sections),
            "section_types": list(sections.keys()),
            "content_length": len(resume_input.get("content", "")),
            "has_metrics": "Metric" in str(sections).lower(),
            "has_achievements": "achievement" in str(sections).lower(),
            "format_quality": self._assess_format_quality(resume_input),
            "completeness_score": self._calculate_completeness(resume_input)
        }

    def _determine_processing_strategy(
        self,
        job_analysis: Dict[str, object],
        resume_analysis: Dict[str, object],
        options: Dict[str, object]
    ) -> Dict[str, object]:
        """Determine optimal processing strategy based on analysis."""
        job_complexity = job_analysis.get("complexity_score", 0.5)
        resume_quality = resume_analysis.get("completeness_score", 0.5)

        # Strategy selection based on complexity and quality
        if job_complexity > 0.8 or resume_quality < 0.3:
            analysis_depth = "deep"
            extraction_strategy = "hybrid"
            validation_level = "enterprise"
        elif job_complexity > 0.6 or resume_quality < 0.6:
            analysis_depth = "comprehensive"
            extraction_strategy = "semantic"
            validation_level = "comprehensive"
        else:
            analysis_depth = "basic"
            extraction_strategy = "section_based"
            validation_level = "basic"

        return {
            "analysis_depth": options.get("analysis_depth", analysis_depth),
            "extraction_strategy": options.get("extraction_strategy", extraction_strategy),
            "quantification_approach": options.get("quantification_approach", "achievements"),
            "rewriting_style": options.get("rewriting_style", "professional"),
            "skill_mapping_method": options.get("skill_mapping_method", "job_alignment"),
            "section_organization": options.get("section_organization", "chronological"),
            "formatting_standards": options.get("formatting_standards", "ats_optimized"),
            "validation_level": options.get("validation_level", validation_level),
            "confidence_threshold": options.get("confidence_threshold", 0.7)
        }

    def _create_analysis_plan(
        self,
        job_analysis: Dict[str, object],
        strategy: Dict[str, object]
    ) -> ResumeAnalysisPlan:
        """Create detailed resume analysis plan."""
        return ResumeAnalysisPlan(
            target_role=job_analysis["target_role"],
            target_company=job_analysis["target_company"],
            industry_focus=job_analysis["industry"],
            seniority_level=job_analysis["seniority"],
            analysis_depth=strategy["analysis_depth"],
            extraction_strategy=strategy["extraction_strategy"],
            quantification_approach=strategy["quantification_approach"],
            rewriting_style=strategy["rewriting_style"],
            skill_mapping_method=strategy["skill_mapping_method"],
            section_organization=strategy["section_organization"],
            formatting_standards=strategy["formatting_standards"],
            validation_level=strategy["validation_level"],
            confidence_threshold=strategy["confidence_threshold"]
        )

    def _configure_section_processing(
        self,
        resume_analysis: Dict[str, object],
        strategy: Dict[str, object]
    ) -> List[ResumeSectionConfig]:
        """Configure processing for each resume section."""
        section_configs = []

        for section_name in self.standard_sections:
            config = ResumeSectionConfig(
                section_name=section_name,
                required=section_name in ["contact_info", "summary", "experience"],
                max_length=self._get_section_max_length(section_name, strategy),
                priority=self._get_section_priority(section_name),
                content_type=self._get_section_content_type(section_name),
                extraction_rules=self._get_extraction_rules(section_name, strategy),
                validation_rules=self._get_validation_rules(section_name, strategy),
                formatting_rules=self._get_formatting_rules(section_name, strategy)
            )
            section_configs.append(config)

        return section_configs

    def _set_k_node_parameters(self, strategy: Dict[str, object]) -> Dict[str, Dict[str, object]]:
        """Set parameters for each K-node in the processing pipeline."""
        return {
            "extraction": {
                "strategy": strategy["extraction_strategy"],
                "depth": strategy["analysis_depth"],
                "sections": self.standard_sections
            },
            "cleaning": {
                "normalization_level": "standard",
                "remove_duplicates": True,
                "standardize_format": True
            },
            "quantification": {
                "approach": strategy["quantification_approach"],
                "extract_metrics": True,
                "focus_on_impact": True
            },
            "rewriting": {
                "style": strategy["rewriting_style"],
                "enhance_achievements": True,
                "optimize_for_ats": strategy["formatting_standards"] == "ats_optimized"
            },
            "skill_mapping": {
                "method": strategy["skill_mapping_method"],
                "job_alignment": True,
                "industry_standards": True
            },
            "assembly": {
                "organization": strategy["section_organization"],
                "prioritize_relevant": True,
                "maintain_flow": True
            },
            "formatting": {
                "standards": strategy["formatting_standards"],
                "layout_optimization": True,
                "readability_focus": True
            },
            "validation": {
                "level": strategy["validation_level"],
                "compliance_check": True,
                "quality_metrics": True
            }
        }

    def _define_execution_order(self, strategy: Dict[str, object]) -> List[str]:
        """Define optimal execution order for K-nodes."""
        return [
            "k1_extract",
            "k2_clean",
            "k3_quantify",
            "k4_rewrite",
            "k5_skillmap",
            "k6_assemble",
            "k7_format",
            "k8_validate"
        ]

    def _configure_fallback_strategies(self, strategy: Dict[str, object]) -> Dict[str, str]:
        """Configure fallback strategies for each K-node."""
        return {
            "k1_extract": "basic_section_parsing",
            "k2_clean": "minimal_normalization",
            "k3_quantify": "basic_metrics_extraction",
            "k4_rewrite": "grammar_correction_only",
            "k5_skillmap": "keyword_matching",
            "k6_assemble": "chronological_order",
            "k7_format": "standard_template",
            "k8_validate": "basic_spell_check"
        }

    def _calculate_job_complexity(self, job_input: Dict[str, object]) -> float:
        """Calculate complexity score for job requirements."""
        complexity_factors = [
            len(job_input.get("requirements", [])) * 0.1,
            len(job_input.get("skills", [])) * 0.05,
            job_input.get("experience_years", 0) * 0.02,
            len(job_input.get("description", "")) * 0.001
        ]
        return min(sum(complexity_factors), 1.0)

    def _assess_format_quality(self, resume_input: Dict[str, object]) -> float:
        """Assess current resume formatting quality."""
        # Simple heuristic based on structure and organization
        sections = resume_input.get("sections", {})
        structure_score = len(sections) / len(self.standard_sections) * 0.5
        content_score = min(len(resume_input.get("content", "")) / 1000, 1.0) * 0.5
        return structure_score + content_score

    def _calculate_completeness(self, resume_input: Dict[str, object]) -> float:
        """Calculate resume completeness score."""
        sections = resume_input.get("sections", {})
        required_sections = ["contact_info", "summary", "experience"]
        present_required = sum(1 for section in required_sections if section in sections)
        return present_required / len(required_sections)

    def _get_section_max_length(self, section_name: str, strategy: Dict[str, object]) -> int:
        """Get maximum length for a section based on strategy."""
        length_map = {
            "summary": 200,
            "experience": 500,
            "skills": 150,
            "education": 200,
            "projects": 300
        }
        return length_map.get(section_name, 100)

    def _get_section_priority(self, section_name: str) -> int:
        """Get priority level for a section."""
        priority_map = {
            "contact_info": 1,
            "summary": 2,
            "experience": 3,
            "skills": 4,
            "education": 5
        }
        return priority_map.get(section_name, 10)

    def _get_section_content_type(self, section_name: str) -> str:
        """Get content type for a section."""
        type_map = {
            "experience": "experience",
            "skills": "skills",
            "education": "education",
            "projects": "projects"
        }
        return type_map.get(section_name, "general")

    def _get_extraction_rules(self, section_name: str, strategy: Dict[str, object]) -> List[str]:
        """Get extraction rules for a section."""
        return [
            "extract_key_phrases",
            "identify_metrics",
            "detect_achievements"
        ]

    def _get_validation_rules(self, section_name: str, strategy: Dict[str, object]) -> List[str]:
        """Get validation rules for a section."""
        return [
            "check_completeness",
            "verify_relevance",
            "validate_format"
        ]

    def _get_formatting_rules(self, section_name: str, strategy: Dict[str, object]) -> List[str]:
        """Get formatting rules for a section."""
        return [
            "apply_consistent_styling",
            "optimize_readability",
            "ensure_ats_compatibility"
        ]

    def _safe_record_telemetry(self, processing_plan: ResumeProcessingPlan) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("rg_planner_executed", {
                    "analysis_depth": processing_plan.analysis_plan.analysis_depth,
                    "section_count": len(processing_plan.section_configs),
                    "validation_level": processing_plan.analysis_plan.validation_level
                })
        except Exception as e:
            Logger.debug(f"Failed to record telemetry: {e}")

    def get_planning_summary(self, processing_plan: ResumeProcessingPlan) -> Dict[str, object]:
        """Get a summary of the planning execution for debugging/telemetry."""
        return {
            "execution_id": "RgPlanner",
            "target_role": processing_plan.analysis_plan.target_role,
            "analysis_depth": processing_plan.analysis_plan.analysis_depth,
            "section_configs_count": len(processing_plan.section_configs),
            "execution_order": processing_plan.execution_order,
            "validation_level": processing_plan.analysis_plan.validation_level
        }
